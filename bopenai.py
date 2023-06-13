#!/usr/bin/env python3

#from rich.text import Text
import time

import bconfig
#import bui

def call_openai_api(prompt_messages, callback):

    try:
        import openai
        from apikey import OPENAI_API_KEY
        openai.api_key = OPENAI_API_KEY

        # record the time before the request is sent
        start_time = time.time()

        # send a ChatCompletion request
        # https://platform.openai.com/docs/guides/chat
        response = openai.ChatCompletion.create(
            model=bconfig.model,
            temperature=0.8,
            max_tokens=1000,
            stream=True,
            messages=prompt_messages,
        )

        #message = ''

        # iterate through the stream of events
        for chunk in response:
            chunk_time = time.time() - start_time  # calculate the time delay of the chunk
            chunk_message = chunk['choices'][0]['delta']  # extract the message
            callback(chunk_message.get('content', ''))
            #message = message + chunk_message.get('content', '')
            #bui.load_response(message, finished=False)
            #bui.update()

            #bui.live.update(Text.assemble((bconfig.name + ': ', bui.style('name')), (message, bui.style('text'))))
            #bui.live.refresh()

        # print the time delay and text received
        #print(f"Full response received {chunk_time:.2f} seconds after request")

    except ImportError:
        msg = "Please run ./install.sh to configure your OpenAI API key."
        bui.print(msg, style=bui.style("error"))
        exit(1)

    except Exception as e:
        return str(e)


