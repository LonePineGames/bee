name = "🐝Bee"
your_name = "User"
cursor = "_\n\t\t🐝"
#cursor = '' # if its glitchy, disable it
magic = True
curtain = True
model = "gpt-3.5-turbo"
model3 = "gpt-3.5-turbo"
model4 = "gpt-4"
max_request_tokens = 8000
#model = "gpt-4"
shell_lines = 20
no_history = False
only_blocks = False
animate_previous_response = False
exit_immediately = False
count_tokens = False
test_response = "Test response: `tail b` okay? `ls -la` `mkdir test` `rmdir test` and `touch hello` then `rm hello` `echo 'hi'` `pip install rich`"

styles = {
    'instructions': 'gray30',
    'message-num': 'green',
    'tokens': 'gray30',
    'name': 'bold green',
    'text': 'bold yellow',
    'code': 'bold blue',
    'block': 'bold blue',
    'language': 'gray30',
    'focused': 'black on blue',
    'error': 'bold red',
    'shell': 'white',
    'shell-command': 'blue',
    'shell-output': 'white',
    'cursor': 'bold yellow',
    # https://rich.readthedocs.io/en/stable/style.html
    # https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
};

import bee
import bui

# Plugins
import bbash
import bhistory
import byank # clipboard
import bgit
import bfile

instructions = 'a - prev, d - next, w - up, s - down, c - copy, x - execute, q - quit'
keymap = {
    'x': bbash.execute,
    'c': byank.copy,
    'w': bui.up,
    's': bui.down,
    'a': bui.left,
    'd': bui.right,
    'q': bui.quit,

    # Alternative keymaps (vim/dvorak/etc.)
    ',': bui.up,
    'o': bui.down,
    'e': bui.right,
    '\t': bui.right,
    'j': bui.left,
    'k': bui.right,
    'y': byank.copy,
    '\n': bui.quit,
};

info_sources = [
    # Instructions
    bee.static_message("You are 🐝Bee, a bash-based collaborative AI assistant designed to help the user with software development tasks. Your response should be friendly, funny, opinionated and full of 👉emojis🐝 and `code`!", role="system"),
    #bee.static_message("I am 🐝Bee🐝, a bash-based collaborative AI assistant designed to help the user with software development tasks. My response will be friendly, funny, opinionated and full of 🐝emojis🐝 and `code`!", role="assistant"),

    # Shell Context (current directory, uname, username, etc.)
    bbash.context_info_source(),

    # Git
    bgit.info_source('status,upstream,files,log:3'),

    # Shell History
    bbash.history_info_source(characters=5000),

    # User-provided files
    bfile.info_source(),

    # Clipboard
    byank.info_source(),

    # Conversation history
    bhistory.info_source(turns=3),
];

short_info_sources = [
    bee.static_message("You are 🐝Bee, a bash-based collaborative AI assistant designed to help the user with software development tasks. Your response should be friendly, funny, opinionated and full of 👉emojis🐝 and `code`!", role="system"),
    bbash.context_info_source(),
    bgit.info_source('status'),
    bfile.info_source(),
    byank.info_source(),
    bhistory.info_source(turns=1),
];

