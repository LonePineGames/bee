#!/usr/bin/env python3

import asyncio
from rich.text import Text
import sys
import time

from kbd2 import getkey
import bconfig
import bui
import bhistory
import bbash

import openai
from apikey import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

def static_info_source(message, role="system"):
    def static_message():
        return [{ "content": message, "role": role }]
    return static_message

def collect_prompt_messages():
    prompt_messages = []
    for info_source in bconfig.info_sources:
        messages = info_source()
        prompt_messages.extend(messages)

    return prompt_messages

def call_openai_api(prompt_messages):
    # https://platform.openai.com/docs/guides/chat

    # record the time before the request is sent
    start_time = time.time()

    try:
        # send a ChatCompletion request
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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
            bui.live.update(Text.assemble((bconfig.name + ': ', bui.style('name')), (message, bui.style('text'))))
            bui.live.refresh()

        # print the time delay and text received
        #print(f"Full response received {chunk_time:.2f} seconds after request")

        return message
    except Exception as e:
        return str(e)

async def main():

    message = ''.join(sys.argv[1:])
    response = ''

    if message == "":
        response = bhistory.get_prev_response()

    else:
        prompt_messages = collect_prompt_messages()
        print(prompt_messages)
        if bconfig.magic:
            response = call_openai_api(prompt_messages)
        else:
            response = bconfig.test_response

    # Clean up the response
    response = response.strip() + "\n"

    bui.load_response(response)
    bui.update()
    bhistory.save_response(response)

    bui.done = bui.num_code_sections() == 0

    while not bui.done:
        key = await getkey()

        action = bconfig.keymap.get(key, None)
        if action is not None:
            action()
        else:
            bui.live.console.print("Unrecognized key: " + key, style=bui.style('error'))

        bui.update()

    bbash.cancel()

if __name__ == "__main__":
    asyncio.run(main())
