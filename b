#!/usr/bin/env python3

magic = True

import os
import sys
import pyperclip
from pathlib import Path
import re
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich import print
import subprocess
import termios
import threading
import time
import tty

import openai
from config import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

import shlex
import asyncio
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.styles import Style

async def create_subprocess_shell():
    shell = await asyncio.create_subprocess_shell(
        "/bin/bash --norc",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return shell

async def bash_client(exit_event, bash_queue, live):
    #print("bash_client")
    async def read_shell_output(shell_reader, source):
        while not exit_event.is_set():
            line = await shell_reader.readline()
            if not line:
                break

            live.console.print(Text(line.decode()), end="")
            # Define the style for the output text
            #style = Style.from_dict({"output": "green"})
            # Print the output above the prompt using the print_formatted_text function.
            # The end argument is set to "\n" (the default value) to preserve newlines.
            #message.send(source, line.decode())
            # print_formatted_text(line.decode(), style=style, end="")

    def append_bash_queue(action):
        # print("append_bash_queue", bash_command)
        bash_queue.put_nowait(action['argument'])

    # Create an interactive Bash shell subprocess
    shell = await asyncio.create_subprocess_shell(
        "/bin/bash --norc",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async def run_bash_queue():
        while not exit_event.is_set():
            #print("waiting for bash_queue")
            command = await bash_queue.get()  # Use await bash_queue.get() to retrieve items
            command = command + '\n'
            #print(command + "*")
            shell.stdin.write(command.encode())
            await shell.stdin.drain()

    tasks = [
        asyncio.create_task(read_shell_output(shell.stdout, "stdout")),
        asyncio.create_task(read_shell_output(shell.stderr, "stderr")),
        asyncio.create_task(run_bash_queue())
    ]

    # Wait for the exit event to be set.
    await exit_event.wait()

    # Cancel all tasks.
    for task in tasks:
        task.cancel()

    # Wait for all tasks to complete or be canceled.
    await asyncio.gather(*tasks, return_exceptions=True)

import sys
import select
import tty
import termios

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

async def getkey():
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while True:
            if isData():
                c = sys.stdin.read(1)
                return c
            await asyncio.sleep(0.1)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


#def getkey():
    #old_settings = termios.tcgetattr(sys.stdin)
    #tty.setcbreak(sys.stdin.fileno())
    #try:
        #b = os.read(sys.stdin.fileno(), 3).decode()
        #if len(b) == 3:
            #k = ord(b[2])
        #else:
            #k = ord(b)
        #key_mapping = {
            #127: 'backspace',
            #10: 'return',
            #32: 'space',
            #9: 'tab',
            #27: 'esc',
            #65: 'up',
            #66: 'down',
            #67: 'right',
            #68: 'left'
        #}
        #return key_mapping.get(k, chr(k))
    #finally:
        #termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

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

def call_openai_api(history, message, prev_response):
    history = "```" + history + "```"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.8,
            max_tokens=1000,
            stop=["User:"],
            messages=[
                {"role": "system", "content": "You are Bee, a bash-based collaborative AI assistant designed to help the user with software development tasks."},
                {"role": "system", "content": history},
                {"role": "assistant", "content": prev_response},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

def display_code_sections(segments, focused_index):
    result = []
    if len(segments) > 1:
        instructions = Text('j - next, k - prev, Tab - next, y - copy, x - execute, q - quit\n', style="red")
        result.append(instructions)

    result.append(Text("Bee: ", style="bold green"))

    for i, segment in enumerate(segments):
        style = "bold white" if i == focused_index else ("bold blue" if segment["mode"] != "text" else "bold yellow")
        if segment["mode"] == "block":
            result.append(Text(segment["language"]+'\n', style="bold gray30"))
            result.append(Text(segment["text"], style=style))
        else:
            result.append(Text(segment["text"], style=style))

    # Merge the segments together
    response_text = Text().join(result)
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
        if match.group("language") and match.group("code_block"):
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
        if text.strip() != "":
            parsed_output.append({"mode": "text", "text": text})
            index = match.end("text")

    return parsed_output

async def main():
    thinking_text = Text("Bee: Thinking...", style="bold green")

    with Live(thinking_text, auto_refresh=False, screen=False) as live:
        current_bash_client = None
        bash_queue = asyncio.Queue()
        exit_event = asyncio.Event()

        response = ''
        prev_response = ''
        with open(Path.home() / ".bee_history", "r") as f:
            prev_response = f.read()
        message = ''.join(sys.argv[1:])

        if message == "":
            response = prev_response

        else:
            history = fetch_history()
            history = remove_ansi_codes(history)
            response = call_openai_api(history, message, prev_response) if magic else "Test response: ```tail b``` okay? `ls -la` `mkdir -p test` and `touch hello` then `echo 'hi'` `pip install rich` `rm hello` `rmdir test`" # test response

            # write the response to ~/.bee_history
            with open(Path.home() / ".bee_history", "w") as f:
                f.write(response)

        # Clean up the response
        response = response.strip() + "\n"

        segments = parse_chatgpt_output(response)

        # Split the response into segments
        #segments = re.split("`", response)

        #segments = [{
            #"text": segment,
            #"mode": ("code" if i % 2 == 1 else "text"),
            #"style": ("bold blue" if i % 2 == 0 else "bold yellow")
        #} for i, segment in enumerate(segments)]

        # Filter empty
        segments = [segment for segment in segments if segment["text"] != ""]

        for i, segment in enumerate(segments):
            segment["ndx"] = i

        code_sections = [segment for segment in segments if segment["mode"] != "text"]

        response_text = display_code_sections(segments, -1)
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
            key = await getkey()

            if key == "y":
                # Get the currently focused code section
                selected_sections.append(code_sections[focused_index]['text'])
                # Copy the code section to the system clipboard
                pyperclip.copy('\n\n'.join(selected_sections))
                acted = True

            elif key == "x":
                selected_section = code_sections[focused_index]['text']

                live.console.print(Text("$ " + selected_section + ""))
                live.refresh()
                acted = True

                #print("Executing: " + selected_section + " current_bash_client: " + str(current_bash_client))
                if current_bash_client is None:
                    current_bash_client = asyncio.create_task(bash_client(exit_event, bash_queue, live))

                bash_queue.put_nowait(selected_section)

            elif key == "j" or key == "\t":
                focused_index = min(focused_index + 1, len(code_sections)-1)
            elif key == "k":
                focused_index = max(focused_index - 1, 0)

            elif key == "q":
                done = True

            if acted and len(code_sections) == 1:
                done = True

        exit_event.set()
        if current_bash_client is not None:
            current_bash_client.cancel()
            current_bash_client = None

if __name__ == "__main__":
    asyncio.run(main())

