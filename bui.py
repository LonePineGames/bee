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

def display(segments, focused_index, scroll):
    result = []
    newlines = 0

    result.append(Text(bconfig.name + ": ", style=style('name')))

    for i, segment in enumerate(segments):
        seg_style = style(segment["mode"])
        if i == focused_index:
            seg_style = style("focused")

        if segment["mode"] == "block":
            if segment["language"]:
                result.append(Text(segment["language"]+'\n', style=style('language')))
            text = segment["text"]
            text = text.strip("\n")
            result.append(Text(text, style=seg_style))
        else:
            result.append(Text(segment["text"], style=seg_style))

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
    parsed_output = []
    index = 0
    pattern = re.compile(
        r"(`{3}(?P<language>\w+)?\n(?P<code_block>[\s\S]*?)`{3})?"  # Match triple backquote-delimited code block with optional language
        r"(`{1,2}(?P<code>[^`]*)`{1,2})?"  # Match single or double backquote-delimited code
        r"(?P<text>[^`]*)"  # Match non-backquote text
    )

    for match in pattern.finditer(output):
        if match.group("code_block"):
            parsed_output.append(
                {
                    "mode": "block",
                    "text": match.group("code_block"),
                    "language": match.group("language"),
                }
            )
            index = match.end("code_block")
        if match.group("code"):
            parsed_output.append({"mode": "code", "text": match.group("code")})
            index = match.end("code")

        text = match.group("text")
        if text:
            parsed_output.append({"mode": "text", "text": text})
            index = match.end("text")

    # Filter empty
    segments = [segment for segment in parsed_output if segment["text"] != ""]

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
    code_sections = [segment for segment in segments if segment["mode"] != "text"]
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

