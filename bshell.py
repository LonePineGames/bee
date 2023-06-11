import asyncio
from rich.text import Text
import subprocess

async def create_subprocess_shell():
    shell = await asyncio.create_subprocess_shell(
        "/bin/bash --norc",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return shell

async def bash_client(exit_event, bash_queue, live):
    async def read_shell_output(shell_reader, source):
        while not exit_event.is_set():
            line = await shell_reader.readline()
            if not line:
                break

            live.console.print(Text(line.decode()), end="")

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

