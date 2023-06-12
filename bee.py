#!/usr/bin/env python3

import asyncio
from rich.text import Text
import os
import signal
import sys
import time

import kbd2
import bconfig
import bui
#import bhistory_file as bhistory
import bhistory
import bbash
import bargs

import openai

def static_info_source(message, role="system"):
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

def call_openai_api(prompt_messages):
    # https://platform.openai.com/docs/guides/chat

    # record the time before the request is sent
    start_time = time.time()

    try:
        # send a ChatCompletion request
        response = openai.ChatCompletion.create(
            model=bconfig.model,
            temperature=0.8,
            max_tokens=1000,
            stream=True,
            messages=prompt_messages,
        )

        message = ''
        # iterate through the stream of events
        for chunk in response:
            chunk_time = time.time() - start_time  # calculate the time delay of the chunk
            chunk_message = chunk['choices'][0]['delta']  # extract the message
            message = message + chunk_message.get('content', '')
            bui.load_response(message, finished=False)
            bui.update()

            #bui.live.update(Text.assemble((bconfig.name + ': ', bui.style('name')), (message, bui.style('text'))))
            #bui.live.refresh()

        # print the time delay and text received
        #print(f"Full response received {chunk_time:.2f} seconds after request")

        return message
    except Exception as e:
        return str(e)

async def get_bee_response(message):
    response = ''

    if message == "":
        response = bhistory.get_prev_response()

        if bconfig.animate_previous_response and bui.live is not None:
            bui.print('Loading previous response...')
            for i in range(0, len(response), 5):
                bui.load_response(response[:i], finished=False)
                bui.update()
                await asyncio.sleep(0.1)

    else:
        prompt_messages = collect_prompt_messages()

        if not bconfig.curtain:
            bui.print(prompt_messages)

        if bconfig.magic:
            try:
                from apikey import OPENAI_API_KEY
                openai.api_key = OPENAI_API_KEY
            except ImportError:
                msg = "Please run ./install.sh to configure your OpenAI API key."
                bui.print(msg, style=bui.style("error"))
                exit(1)

            response = call_openai_api(prompt_messages)
            response = response.strip() + "\n"
            bhistory.save_response(response, "assistant")
        else:
            response = bconfig.test_response
            response = response.strip() + "\n"

    return response

async def get_bee_response_and_handle(message):
    response = await get_bee_response(message)

    bui.load_response(response, finished=True)
    bui.update()

    #bui.done = len(message) < 200 and bui.num_code_sections() == 0

    if bui.done:
        kbd2.cancel = True

def parse_args_and_input():
    message = bargs.parse_args()

    if not os.isatty(sys.stdin.fileno()):
        stdin_message = sys.stdin.read()
        # Reopen the terminal as stdin
        sys.stdin = open('/dev/tty')

        if stdin_message != "":
            if bui.live is not None:
                bui.print(stdin_message)
            message = message + '\n' + stdin_message
            message = message.strip()

    return message

async def main():
    bui.setup_live('Reading')
    message = parse_args_and_input()

    if message != "":
        bhistory.save_response(message, "user")

    bui.setup_live('Thinking')
    get_bee_response_task = asyncio.create_task(get_bee_response_and_handle(message))

    def signal_handler(sig, frame):
        bui.print("Exiting gracefully...")
        get_bee_response_task.cancel()
        bbash.cancel()
        bhistory.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if bconfig.exit_immediately:
        bui.done = True

    while not bui.done:
        #await asyncio.sleep(0.1)

        key = await kbd2.getkey()

        if key is None:
            continue

        action = bconfig.keymap.get(key, None)
        if action is not None:
            action()
        else:
            bui.print("Unrecognized key: " + key, style=bui.style('error'))

        bui.update()

    # TODO: find a modular way to close plugins
    await asyncio.gather(get_bee_response_task)
    get_bee_response_task.cancel()
    bbash.cancel()
    bhistory.close()


async def noninteractive_main():
    def signal_handler(sig, frame):
        bui.print("Exiting gracefully...")
        bhistory.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    message = bargs.parse_args()

    if not os.isatty(sys.stdin.fileno()):
        stdin_message = sys.stdin.read()
        if stdin_message != "":
            message = message + '\n' + stdin_message
            message = message.strip()

    bhistory.save_response(message, "user")
    response = await get_bee_response(message)

    if bconfig.only_blocks:
        segments = bui.parse_chatgpt_output(response)
        code_sections = [segment for segment in segments if segment["mode"] == "block"]

        # If there are no code sections, then just return the whole response
        if len(code_sections) > 0:
            response = "\n".join([section["text"] for section in code_sections])

    # Echo to stdout
    print(response)

    bhistory.close()

import asyncio

def my_exception_handler(loop, context):
    # Print the exception message and the stack trace.
    bui.print("Caught an exception: ", context["message"])
    bui.print("Stack trace: ")
    for line in context["traceback"]:
        bui.print(line)

loop = asyncio.get_event_loop()
loop.set_exception_handler(my_exception_handler)

if __name__ == "__main__":
    if not os.isatty(sys.stdout.fileno()):
        asyncio.run(noninteractive_main())
    else:
        asyncio.run(main())

