import asyncio
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

scroll = 0
focused_index = 0
response = ''
segments = []
code_sections = []
shell_output = []
done = False

def style(style_name):
    return bconfig.styles.get(style_name, None)

thinking_text = Text(bconfig.name + ": Thinking...", style=style('thinking'))
live = Live(thinking_text, auto_refresh=False, screen=False)
live.start()

def quit():
    global done
    done = True

def load_response(resp):
    global response

    response = resp

def insert_shell(result):
    shell_text = ''.join(shell_output)
    shell_text = '\n'.join(shell_text.split('\n')[-bconfig.shell_lines:])
    result.append(Text(shell_text, style=style('shell')))

def display(segments, focused_index, scroll):
    result = []
    newlines = 0
    ready_for_shell = False
    shell_done = False

    result.append(Text(bconfig.name + ": ", style=style('name')))

    for i, segment in enumerate(segments):
        seg_style = style(segment["mode"])
        if i == focused_index:
            seg_style = style("focused")
            ready_for_shell = not shell_done

        if segment["mode"] == "block":
            if segment["language"]:
                result.append(Text(segment["language"]+'\n', style=style('language')))
            text = segment["text"]
            text = text.strip("\n")
            result.append(Text(text, style=seg_style))

            if ready_for_shell:
                insert_shell(result)
                shell_done = True
                ready_for_shell = False
        else:
            text = segment["text"]
            if ready_for_shell and segment["mode"] == "text" and '\n' in text:
                text = text.split('\n', 1)
                result.append(Text(text[0]+'\n', style=seg_style))
                insert_shell(result)
                shell_done = True
                ready_for_shell = False
                if len(text) > 1:
                    result.append(Text(text[1], style=seg_style))
            else:
                result.append(Text(segment["text"], style=seg_style))

    if not shell_done:
        result.append(Text('\n', style=style('text')))
        insert_shell(result)

    # Merge the segments together
    response_text = Text().join(result)

    if scroll > 0:
        lines = response_text.split("\n")
        remaining_lines = lines[scroll:]
        response_text = Text("\n").join(remaining_lines)

    if len(segments) > 1 and bconfig.instructions:
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

def update():
    global response
    global segments
    global code_sections
    global live
    global focused_index

    if response.startswith(bconfig.name + ":"):
        response = response[len(bconfig.name + ":"):]

    segments = parse_chatgpt_output(response)
    code_sections = [segment for segment in segments if segment["mode"] in ["code", "block"]]
    code_ndx = code_sections[focused_index]["ndx"] if len(code_sections) > 0 else -1

    response_text = display(segments, code_ndx, scroll)
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
    scroll = max(scroll - 1, 0)

def down():
    global scroll
    scroll = scroll + 1

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

