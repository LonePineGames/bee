import asyncio
from builtins import print as native_print
import os
import pyperclip
from pathlib import Path
import re
from rich.text import Text
from rich.live import Live
import sys
import time

import bee
import bconfig
import bhistory

scroll = 0
num_visible_lines = 0
focused_index = 0
response = ''
segments = []
code_sections = []
shell_output = []
done = False
live = None

def style(style_name):
    result = bconfig.styles.get(style_name, None)
    if result is None:
        result = bconfig.styles.get('text', '')
    return result

def setup_live(mode):
    global live

    thinking_text = Text(f"{bconfig.name} 💭⏳ {mode}...", style=style('thinking'))

    if live is None:
        live = Live(thinking_text, auto_refresh=False, screen=False)
        live.start()
    else:
        live.update(thinking_text)
        live.refresh()

def quit():
    global done
    done = True

    update()

def insert_shell(result):
    shell_text = ''.join(shell_output)
    shell_text = '\n'.join(shell_text.split('\n')[-bconfig.shell_lines:])
    result.append(Text(shell_text, style=style('shell')))

def display(segments, focused_index):
    global scroll
    global num_visible_lines

    result = []
    newlines = 0
    ready_for_shell = False
    shell_done = False

    if bhistory.response_finished:
        state_emoji = '' #'✔️'
    else:
        state_emoji = '⏳ '

    # 🗨️ 💬
    result.append(Text(bhistory.get_name() + " 💬" + state_emoji + " ", style=style('name')))

    for i, segment in enumerate(segments):
        mode = segment["mode"]
        if bconfig.only_blocks and not is_code_segment(segment):
            continue

        seg_style = style(mode)
        if i == focused_index:
            seg_style = style("focused")
            ready_for_shell = not shell_done

        if mode == "block":
            if segment.get("language", None) is not None:
                result.append(Text(segment["language"]+'\n', style=style('language')))
            text = segment["text"]
            if not bconfig.only_blocks:
                text = text.strip("\n")
            result.append(Text(text, style=seg_style))

            if ready_for_shell:
                insert_shell(result)
                shell_done = True
                ready_for_shell = False
        else:
            text = segment["text"]
            if ready_for_shell and mode == "text" and '\n' in text:
                text = text.split('\n', 1)
                result.append(Text(text[0]+'\n', style=seg_style))
                insert_shell(result)
                shell_done = True
                ready_for_shell = False
                if len(text) > 1:
                    result.append(Text(text[1], style=seg_style))
            else:
                result.append(Text(segment["text"], style=seg_style))

    if bconfig.cursor != '' and not bhistory.response_finished:
        result.append(Text(bconfig.cursor, style=style('cursor')))

    if ready_for_shell and not shell_done:
        result.append(Text('\n', style=style('text')))
        insert_shell(result)
        shell_done = True

    # Merge the segments together
    response_text = Text().join(result)

    lines = response_text.split("\n")
    if scroll > 0:
        remaining_lines = lines[scroll:]
        num_visible_lines = len(remaining_lines)
        response_text = Text("\n").join(remaining_lines)
    else:
        num_visible_lines = len(lines)

    show_turn = bhistory.get_turn() < bhistory.max_turn() or bhistory.get_message_role() != 'assistant'
    #show_turn = True
    if show_turn:
        message_num = Text(f"{bhistory.get_message_role()} message #{bhistory.get_turn()} of {bhistory.max_turn()}", style=style('message-num'))

        req_tokens, resp_tokens, cost = bhistory.get_message_tokens()
        cost_str = ''
        if cost is not None and cost > 0:
            cost_str = ' / '
            if cost < 1:
                cost *= 100
                cost_str = cost_str + f"{cost:.0f}¢"
            else:
                cost_str = cost_str + f"\${cost:.2f}"
        tokens = Text(f" -- cost estimate: {req_tokens}req / {resp_tokens}resp{cost_str}\n", style=style('tokens'))

        response_text = Text.assemble(message_num, tokens, response_text)

    instructions = bconfig.instructions and not bconfig.exit_immediately and not done and (len(segments) > 1 or show_turn)
    if instructions:
        instructions = Text(bconfig.instructions + '\n', style=style('instructions'))
        response_text = Text.assemble(instructions, response_text)

    return response_text

def parse_chatgpt_output(output):
    segments = []
    index = 0
    pattern = re.compile(
        r"(`{3}(?P<language>\w+)?\n(?P<code_block>[\s\S]*?)`{3})?"  # Match triple backquote-delimited code block with optional language
        r"(`{1,2}(?P<code>[^`]*)`{1,2})?"  # Match single or double backquote-delimited code
        r"(?P<text>[^`]*)"  # Match non-backquote text
    )

    for match in pattern.finditer(output):
        output = None
        if match.group("code_block"):
            output = {
                "mode": "block",
                "text": match.group("code_block"),
                "language": match.group("language"),
            };
            segments.append(output)
            index = match.end("code_block")

        if match.group("code"):
            output = {"mode": "code", "text": match.group("code")}
            segments.append(output)
            index = match.end("code")

        if match.group("text"):
            output = {"mode": "text", "text": match.group("text")}
            segments.append(output)
            index = match.end("text")

    # Filter empty
    segments = [segment for segment in segments if segment["text"] != ""]

    for i, segment in enumerate(segments):
        segment["ndx"] = i

    return segments

def has_nonascii_chars(str):
    for char in str:
        if ord(char) > 127:
            return True
    return False

def is_code_segment(segment):
    if segment["mode"] not in ["code", "block"]:
        return False

    if len(segment["text"]) < 5 and segment["mode"] == "code":
        # Check to see if there is any emoji/unicode in the text
        if not has_nonascii_chars(segment["text"]):
            return False

    return True

def filter_code_sections(segments):
    return [segment for segment in segments if is_code_segment(segment)]

def update():
    global segments
    global code_sections
    global live
    global focused_index

    if live is None:
        return

    response = bhistory.get_message()

    if response is None:
        response = ""

    segments = parse_chatgpt_output(response)
    code_sections = filter_code_sections(segments)
    code_ndx = code_sections[focused_index]["ndx"] if len(code_sections) > 0 else -1

    response_text = display(segments, code_ndx)
    live.update(response_text)
    live.refresh()

def right():
    global focused_index
    focused_index = min(focused_index + 1, len(code_sections)-1)

def left():
    global focused_index
    focused_index = max(focused_index - 1, 0)

def up():
    global scroll
    global focused_index
    global shell_output
    scroll = scroll - 1

    if scroll < 0:
        if bhistory.move_backward():
            shell_output = []
            focused_index = 0
        scroll = 0

def down():
    global scroll
    global focused_index
    global num_visible_lines
    global shell_output

    #height, width = live.console.size
    #print(live._live_renderer._shape)
    #if num_visible_lines > height - 4:
    if num_visible_lines > 10:
        scroll = scroll + 1
    elif bhistory.move_forward():
        shell_output = []
        focused_index = 0
        scroll = 0

def num_code_sections():
    global code_sections
    return len(code_sections)

def get_selection():
    global focused_index
    global code_sections
    global segments

    code_ndx = code_sections[focused_index]["ndx"] if len(code_sections) > focused_index else -1

    return segments[code_ndx]["text"] if code_ndx >= 0 else ""

def append_to_shell_segment(msg):
    global focused_index
    global code_sections
    global segments

    shell_output.append(msg)
    update()
    #live.console.print(Text(msg, style=style('shell')), end="")
    #live.refresh()


def print(args, style=''):
    global live
    if live is not None:
        live.console.print(args, style=style)
    else:
        native_print(args)

