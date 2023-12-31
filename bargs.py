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
    parser.add_argument('-T', '--turn', action='store', type=int, help='Show conversation history')
    parser.add_argument('--num-turns', action='store_true', help='Output the number of turns so far, then quit')
    parser.add_argument('--blocks', action='store_true', help='Only show code blocks')
    parser.add_argument('--exit-immediately', action='store_true', help='Exit after getting the response')
    parser.add_argument('--show', choices=['user', 'prompt', 'assistant'], help='Show previous user message or entire prompt')
    parser.add_argument('-s', '--search', help='Search for keyword or phrase.')
    parser.add_argument('-C', '--count-tokens', action='store_true', help='Count tokens in the user message and piped input.')

    args, unknown = parser.parse_known_args()

    if args.version:
        bui.setup_live('')
        bui.live.console.print(Text.assemble(("🐝Bee ", bui.style("name")), ("version 0.1", bui.style("code"))))
        bui.live.update('')
        bui.live.refresh()
        exit()

    if args.search:
        results = bhistory.search_messages(args.search)
        if len(results) == 0:
            bui.setup_live('')
            bui.live.console.print(Text.assemble(("No results for ", bui.style("code")), (args.search, bui.style("name"))), justify="center")
            bui.live.update('')
            bui.live.refresh()
            exit()

    if args.test:
        bconfig.magic = False
        if len(unknown) == 0:
            unknown.append("Hello, Bee!")

    if args.turn:
        bhistory.set_turn(args.turn)
        unknown = []

    if args.num_turns:
        print(bhistory.max_turn())
        exit()

    if args.show:
        role = args.show
        if args.show == 'prompt':
            role = 'system'
        bhistory.set_message_role(role)

    model = bconfig.model3
    if args.model:
        model = args.model
    elif args.gpt_4:
        model = bconfig.model4
    elif args.gpt_3:
        model = bconfig.model3

    bconfig.model = model

    if args.clear:
        bconfig.no_history = True

    if args.blocks:
        bconfig.only_blocks = True

    if args.exit_immediately:
        bconfig.exit_immediately = True

    if args.count_tokens:
        bconfig.count_tokens = True

    return ' '.join(unknown)

