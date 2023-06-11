import argparse
from rich.text import Text

import bconfig
import bui

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model", help="Choose a language model", choices=["gpt-3.5-turbo", "gpt-4"])
    parser.add_argument('-4', '--gpt-4', action='store_true', help='Use GPT-4')
    parser.add_argument('-3', '--gpt-3', action='store_true', help='Use GPT-3.5-Turbo')
    parser.add_argument('-v', '--version', action='store_true', help='Show version and exit')
    parser.add_argument('-t', '--test', action='store_true', help='Test output')

    args, unknown = parser.parse_known_args()

    if args.version:
        bui.live.update(Text.assemble(("🐝Bee ", bui.style("name")), ("version 0.1", bui.style("langauge"))))
        bui.live.refresh()
        exit()

    if args.test:
        bconfig.magic = False

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

    return ' '.join(unknown)

