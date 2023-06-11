import asyncio
import os
from pathlib import Path
import re
from rich.text import Text
import subprocess

import bui

async def bash_client(exit_event, bash_queue, live):
    async def read_shell_output(shell_reader, source):
        while not exit_event.is_set():
            line = await shell_reader.readline()
            if not line:
                break

            live.console.print(Text(line.decode(), style=bui.style('shell-output')), end="")

    def append_bash_queue(action):
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
            command = await bash_queue.get()  # Use await bash_queue.get() to retrieve items
            command = command + '\n'
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

def remove_ansi_codes(s):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', s)

def fetch_history(context):
    script_session_file = os.getenv("SCRIPT_SESSION")

    if script_session_file is None:
        return "EMPTY HISTORY"

    script_session_path = Path(script_session_file)
    if not script_session_path.exists():
        return "EMPTY HISTORY"

    # Read the last 1000 characters of the file
    history = script_session_path.read_text()[-context:]

    history = remove_ansi_codes(history)

    return history

def info_source(context=5000):
    def bash_info_source():
        history = fetch_history(context)
        history = "BASH HISTORY: ```\n" + history.strip() + "\n```"

        return [{"role": "system", "content": history}]

    return bash_info_source

current_bash_client = None
bash_queue = None
exit_event = None

def execute():
    global current_bash_client
    global bash_queue
    global exit_event

    selected_section = bui.get_selection()

    bui.live.console.print(Text("$ " + selected_section + "", style=bui.style('shell-command')))
    bui.live.refresh()

    if current_bash_client is None:
        bash_queue = asyncio.Queue()
        exit_event = asyncio.Event()
        current_bash_client = asyncio.create_task(bash_client(exit_event, bash_queue, bui.live))

    bash_queue.put_nowait(selected_section)

def cancel():
    global current_bash_client
    global exit_event

    if current_bash_client is not None:
        exit_event.set()
        current_bash_client.cancel()
        current_bash_client = None

