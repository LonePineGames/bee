#!/usr/bin/env python3
import re
import os
import sys
import time
import pyperclip
import subprocess
from pathlib import Path
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich import print
from getch import getch

import openai
from config import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

def remove_ansi_codes(s):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', s)

def fetch_history():
    script_session_file = os.getenv("SCRIPT_SESSION")

    if script_session_file is None:
        return "EMPTY HISTORY"

    script_session_path = Path(script_session_file)
    if not script_session_path.exists():
        return "EMPTY HISTORY"

    # Read the last 1000 characters of the file
    history = script_session_path.read_text()[-5000:]

    return history

def call_openai_api(history):
    history = "```" + history + "```"
    message = ''.join(sys.argv[1:])
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.8,
            max_tokens=1000,
            stop=["User:"],
            messages=[
                {"role": "system", "content": "You are Bee, a bash-based collaborative AI assistant designed to help the user with software development tasks."},
                {"role": "system", "content": history},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

def display_code_sections(segments, focused_index):
    # Create Text objects for each segment, coloring based on their index
    colored_segments = [
        Text(segment["text"], style=("bold white" if i == focused_index else ("bold blue" if segment["mode"] == "code" else "bold yellow")))
        for i, segment in enumerate(segments)
    ]

    colored_segments.insert(0, Text("Bee: ", style="bold green"))
    instructions = Text('j - next, k - prev, Tab - next, y - copy, x - execute, q - quit\n', style="red")
    colored_segments.insert(0, instructions)

    # Merge the segments together
    response_text = Text().join(colored_segments)
    return response_text

thinking_text = Text("Bee: Thinking...", style="bold green")

with Live(thinking_text, auto_refresh=False, screen=False) as live:
    history = fetch_history()
    history = remove_ansi_codes(history)
    #response = call_openai_api(history)
    response = "Test response: ```tail b``` okay? `ls -la` `mkdir -p test` and `touch hello` then `echo 'hi'` `pip install rich` `rm hello` `rmdir test`" # test response for now

    # Split the response into segments
    segments = re.split("`", response)

    segments = [{
        "text": segment,
        "mode": ("code" if i % 2 == 1 else "text"),
        "style": ("bold blue" if i % 2 == 0 else "bold yellow")
    } for i, segment in enumerate(segments)]

    # Filter empty
    segments = [segment for segment in segments if segment["text"] != ""]

    for i, segment in enumerate(segments):
        segment["ndx"] = i

    code_sections = [segment for segment in segments if segment["mode"] == "code"]

    response_text = display_code_sections(segments, 0)
    live.update(response_text)
    live.refresh()

    focused_index = 0
    selected_sections = []
    done = len(code_sections) == 0

    while not done:
        code_ndx = code_sections[focused_index]["ndx"] if len(code_sections) > 0 else -1
        response_text = display_code_sections(segments, code_ndx)
        live.update(response_text)
        live.refresh()

        acted = False
        key = getch()

        if key == "y":
            # Get the currently focused code section
            selected_sections.append(code_sections[focused_index]['text'])
            # Copy the code section to the system clipboard
            pyperclip.copy('\n\n'.join(selected_sections))
            acted = True

        elif key == "x":
            selected_section = code_sections[focused_index]['text']

            live.console.print(Text("$ " + selected_section + ""))

            process = subprocess.Popen(["bash", "-c", selected_section], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            # Display the output of the command
            live.console.print(Text(out.decode()), end="")
            live.console.print(Text(err.decode()), end="")

            #live.console.print('')  # Empty line
            live.refresh()
            acted = True

        elif key == "j" or key == "\t":
            focused_index = min(focused_index + 1, len(code_sections)-1)
        elif key == "k":
            focused_index = max(focused_index - 1, 0)

        elif key == "q":
            done = True

        if acted and len(code_sections) == 1:
            done = True

