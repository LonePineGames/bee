#!/usr/bin/env python3

import asyncio
from rich.text import Text
import os
import signal
import sys
import time

import bargs
import bbash
import bconfig
import bhistory
import bopenai
import bui
import kbd2

interactive = False

def static_message(message, role="system"):
    def static_message():
        return [{ "role": role, "content": message }]
    return static_message

def collect_prompt_messages():
    prompt_messages = []
    sources = bconfig.info_sources if not bconfig.no_history else bconfig.short_info_sources
    for info_source in sources:
        messages = info_source()
        prompt_messages.extend(messages)

    # Filter for length
    prompt_messages = [{
        "role": message["role"],
        "content": message["content"][:1000]
    } for message in prompt_messages]

    return prompt_messages

def update_response(response, finished=False):
    global interactive

    if response.startswith(bconfig.name):
        response = response[len(bconfig.name):]

    bhistory.set_message('assistant', response, finished=finished)

    if interactive:
        bui.update()

async def get_bee_response(message):
    global interactive

    prompt_messages = collect_prompt_messages()
    bhistory.set_system_messages(prompt_messages)
    if not bconfig.curtain:
        bui.print(prompt_messages)

    if bconfig.magic:
        message = ''
        def openai_api_callback(chunk):
            message += chunk
            update_response(message)

        bopenai.call_openai_api(prompt_messages, openai_api_callback)
        update_response(message, finished=True)

    else:
        update_response(bconfig.test_response, finished=True)

    if bui.done:
        kbd2.cancel = True

def parse_args_and_input():
    global interactive
    message = bargs.parse_args()

    if not os.isatty(sys.stdin.fileno()):
        stdin_message = sys.stdin.read()

        if interactive:
            # Reopen the terminal as stdin
            sys.stdin = open('/dev/tty')

        if stdin_message != "":
            if interactive and bui.live is not None:
                bui.print(stdin_message)
            message = message + '\n' + stdin_message
            message = message.strip()

    return message

def restore_cursor():
    # Restore the cursor state
    os.system("echo -n '\\033[?25h'")

restore_cursor.cancel = restore_cursor

def print_noninteractive_response():
    response = bhistory.get_message()
    if bconfig.only_blocks:
        segments = bui.parse_chatgpt_output(response)
        code_sections = [segment for segment in segments if segment["mode"] == "block"]

        # If there are no code sections, then just return the whole response
        if len(code_sections) > 0:
            response = "\n".join([section["text"] for section in code_sections])

    # Echo to stdout
    print(response)

async def main():
    global interactive

    cancelable = [bbash]
    def signal_handler(sig, frame):
        bui.print("Exiting gracefully...")
        for task in cancelable:
            task.cancel()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    interactive = os.isatty(sys.stdout.fileno())

    if interactive:
        # Save the current cursor state
        os.system("echo -n '\\033[?25p'")
        cancelable.append(restore_cursor)

        bui.setup_live('Reading')

    bhistory.setup()
    cancelable.append(bhistory)

    message = parse_args_and_input()
    get_bee_response_task = None

    if message != "":
        bhistory.new_turn()
        bhistory.set_message('user', message)

        if interactive:
            bui.setup_live('Thinking')

        get_bee_response_task = asyncio.create_task(get_bee_response(message))
        cancelable.append(get_bee_response_task)
    else:
        bhistory.response_finished = True

    if bconfig.exit_immediately or not interactive:
        bui.done = True

    while not bui.done:
        key = await kbd2.getkey()

        if key is None:
            continue

        action = bconfig.keymap.get(key, None)
        if action is not None:
            action()
        else:
            bui.print("Unrecognized key: " + key, style=bui.style('error'))

        bui.update()

    if get_bee_response_task is not None:
        await asyncio.gather(get_bee_response_task)

    if not interactive:
        print_noninteractive_response()

    for task in cancelable:
        task.cancel()

def my_exception_handler(loop, context):
    # Print the exception message and the stack trace.
    bui.print("Caught an exception: ", context["message"])
    bui.print("Stack trace: ")
    for line in context["traceback"]:
        bui.print(line)

loop = asyncio.get_event_loop()
loop.set_exception_handler(my_exception_handler)

if __name__ == "__main__":
    asyncio.run(main())

