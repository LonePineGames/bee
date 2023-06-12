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
from apikey import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

def static_info_source(message, role="system"):
    def static_message():
        return [{ "role": role, "content": message }]
    return static_message

def collect_prompt_messages():
    prompt_messages = []
    for info_source in bconfig.info_sources:
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

def get_bee_response(message):
    response = ''

    if message == "":
        response = bhistory.get_prev_response()

    else:
        prompt_messages = collect_prompt_messages()

        if not bconfig.curtain:
            if bui.live is not None:
                bui.live.console.print(prompt_messages)
            else:
                print(prompt_messages)

        if bconfig.magic:
            response = call_openai_api(prompt_messages)
            response = response.strip() + "\n"
            bhistory.save_response(response, "assistant")
        else:
            response = bconfig.test_response
            response = response.strip() + "\n"

    return response

async def get_bee_response_and_handle(message):
    response = get_bee_response(message)

    bui.load_response(response, finished=True)
    bui.update()

    bui.done = bui.num_code_sections() == 0

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
                bui.live.console.print(stdin_message)
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
        bui.live.console.print("Exiting gracefully...")
        get_bee_response_task.cancel()
        bbash.cancel()
        bhistory.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while not bui.done:
        #await asyncio.sleep(0.1)

        key = await kbd2.getkey()

        if key is None:
            continue

        action = bconfig.keymap.get(key, None)
        if action is not None:
            action()
        else:
            bui.live.console.print("Unrecognized key: " + key, style=bui.style('error'))

        bui.update()

    # TODO: find a modular way to close plugins
    await asyncio.gather(get_bee_response_task)
    get_bee_response_task.cancel()
    bbash.cancel()
    bhistory.close()


def noninteractive_main():
    def signal_handler(sig, frame):
        print("Exiting gracefully...")
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
    response = get_bee_response(message)

    # Echo to stdout
    print(response)

    bhistory.close()

if __name__ == "__main__":
    if not os.isatty(sys.stdout.fileno()):
        noninteractive_main()
    else:
        asyncio.run(main())

