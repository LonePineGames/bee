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

base_prompt = """You are Bee, a bash-based collaborative AI assistant designed to help the user with software development tasks.

If the user asks you to use bash or interact with the computer in any way, you can do so by responding "bash: <command>". For example:

bash: mkdir test

If the user asks you to edit a file, you can do so by responding "edit: <filename>". Do not use nano or vim, instead use edit. For example:

edit: tests.py

Responses that do not start with "bash:" or "edit:" will be treated as chat messages. For example:

Hello! How can I help you today?

--- CHAT AND COMMAND HISTORY ---
"""

def build_prompt(history):
    message = ''.join(sys.argv[1:])
    #print(message)
    prompt = base_prompt
    prompt += history
    prompt += "\n---\n"
    prompt += "User: " + message + "\n"

    return prompt

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

def parse_code_sections(response):
    code_sections = re.findall(r"`{1,3}(.*?)`{1,3}", response, re.DOTALL)
    return code_sections

def display_code_sections(code_sections, focused_index):
    console = Console()
    console.print("Press 'j' to navigate to the next code section, 'k' to navigate to the previous code section, 'y' to yank into the system clipboard, or 'q' to quit: ")

    for i, section in enumerate(code_sections):
        code_text = Text(section, style="bold yellow")
        panel = Panel(code_text, title=f"Code Section {i}", style=("blue" if i == focused_index else ""))
        console.print(panel)

def handle_keyboard_input(code_sections):
    focused_index = 0
    display_code_sections(code_sections, focused_index)
    selected_sections = []
    done = False

    while not done:
        acted = False
        key = getch()

        if key == "y":
            # Get the currently focused code section
            selected_sections.append(code_sections[focused_index])
            # Copy the code section to the system clipboard
            pyperclip.copy('\n\n'.join(selected_sections))
            acted = True

        elif key == "x":
            selected_section = code_sections[focused_index]
            process = subprocess.Popen(["bash", "-c", selected_section])
            process.wait()
            acted = True

        elif key == "j":
            focused_index = min(focused_index + 1, len(code_sections)-1)
        elif key == "k":
            focused_index = max(focused_index - 1, 0)

        elif key == "q":
            done = True

        display_code_sections(code_sections, focused_index)

        if acted and len(code_sections) == 1:
            done = True

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

print('')  # Empty line

indent = "   "
thinking_text = Text(indent + "Bee: Thinking...", style="bold green")

with Live(thinking_text, auto_refresh=False) as live:
    history = fetch_history()
    history = remove_ansi_codes(history)
    #prompt = build_prompt(history)
    #response = call_openai_api(history)
    response = "```tail b``` `mkdir -p test` `touch hello`"
    response_text = Text(indent + 'Bee: ' + response, style="bold blue")
    live.update(response_text)

    code_sections = parse_code_sections(response)
    handle_keyboard_input(code_sections)

