name = "🐝Bee"
magic = True
curtain = False
test_response = "Test response: `tail b` okay? `ls -la` `mkdir -p test` and `touch hello` then `echo 'hi'` `pip install rich` `rm hello` `rmdir test`"
instructions = 'a - prev, d - next, w - up, s - down, y - copy, x - execute, q - quit'

# https://rich.readthedocs.io/en/stable/style.html
# https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
styles = {
    'instructions': 'gray30',
    'name': 'bold green',
    'text': 'bold yellow',
    'code': 'bold blue',
    'block': 'bold blue',
    'language': 'gray30',
    'focused': 'black on blue',
    'error': 'bold red',
    'shell-command': 'blue',
    'shell-output': 'white',
};

import bee
import bui

# Plugins
import bbash
import bhistory
#import bhistory_file as bhistory
import byank
import bgit
import bfile

keymap = {
    'x': bbash.execute,
    'y': byank.copy,
    'w': bui.up,
    's': bui.down,
    'a': bui.left,
    'd': bui.right,
    ',': bui.up,
    'o': bui.down,
    'e': bui.right,
    '\t': bui.right,
    'q': bui.quit,
};

info_sources = [
    bee.static_info_source("You are 🐝Bee🐝, a bash-based collaborative AI assistant designed to help the user with software development tasks. Your response should be friendly, funny, and full of 🐝emojis🐝 and `code`!", role="system"),
    # Alternate: bee.static_info_source("I am 🐝Bee🐝, a bash-based collaborative AI assistant designed to help the user with software development tasks. My response will be friendly, funny, and full of 🐝emojis🐝 and `code`!", role="assistant"),
    bgit.info_source('status,log:5'),
    bbash.info_source(context=5000),
    byank.info_source(),
    bhistory.info_source(turns=4),
    bfile.info_source(),
];

