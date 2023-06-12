import argparse
from rich.text import Text

import bconfig
import bui
import bhistory

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model", help="Choose a language model", choices=["gpt-3.5-turbo", "gpt-4"])
    parser.add_argument('-4', '--gpt-4', action='store_true', help='Use GPT-4')
    parser.add_argument('-3', '--gpt-3', action='store_true', help='Use GPT-3.5-Turbo')
    parser.add_argument('-v', '--version', action='store_true', help='Show version and exit')
    parser.add_argument('-t', '--test', action='store_true', help='Test output')
    parser.add_argument('-c', '--clear', action='store_true', help='No conversation history')
    parser.add_argument('-H', '--history', action='store', type=int, help='Show conversation history')
    parser.add_argument('--blocks', action='store_true', help='Only show code blocks')
    parser.add_argument('--exit-immediately', action='store_true', help='Exit after getting the response')

    args, unknown = parser.parse_known_args()

    if args.version:
        bui.setup_live('')
        bui.live.console.print(Text.assemble(("🐝 Bee ", bui.style("name")), ("version 0.1", bui.style("code"))))
        bui.live.update('')
        bui.live.refresh()
        exit()

    if args.test:
        bconfig.magic = False
        if len(unknown) == 0:
            unknown.append("Hello, Bee!")

    if args.history:
        bconfig.magic = False
        history = bhistory.get_history(args.history)
        history.reverse()
        result = ''
        for message in history:
            author = ''
            if message['role'] == 'user':
                author = bconfig.your_name
            elif message['role'] == 'assistant':
                author = bconfig.name
            else:
                continue
            print(message)
            result += f"{author}: {message['content']}\n\n"

        bconfig.test_response = result
        if len(unknown) == 0:
            unknown.append("Hello, Bee!")

    #if args.help:
        #bui.live.update(Text.assemble(("🐝 Bee ", bui.style("name")), ("version 0.1", bui.style("code"))))
        #print("Usage: b [file] \"Ask Bee a question!\"")
        #print("Options:")
        #print("  -m, --model [model]  Choose a language model")
        #print("  -4, --gpt-4          Use GPT-4")
        #print("  -3, --gpt-3          Use GPT-3.5-Turbo")
        #print("  -t, --test           Test output")
        #print("  -h, --help           Show this help message and exit")
        #exit()

    model = "gpt-3.5-turbo"
    if args.model:
        model = args.model
    elif args.gpt_4:
        model = "gpt-4"
    elif args.gpt_3:
        model = "gpt-3.5-turbo"

    bconfig.model = model

    if args.clear:
        bconfig.no_history = True

    if args.blocks:
        bconfig.only_blocks = True

    if args.exit_immediately:
        bconfig.exit_immediately = True

    return ' '.join(unknown)

