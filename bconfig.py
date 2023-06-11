import bbash
import bhistory
import byank
#import bgit
import bui
import bee

magic = True
test_response = "Test response: `tail b` okay? `ls -la` `mkdir -p test` and `touch hello` then `echo 'hi'` `pip install rich` `rm hello` `rmdir test`"

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
    bee.static_info_source("You are 🐝Bee🐝, a bash-based collaborative AI assistant designed to help the user with software development tasks. Your response should be friendly, funny, and full of 🐝emojis🐝 and `code`.", role="system"),
    # Alternate: bee.static_info_source("I am 🐝Bee🐝, a bash-based collaborative AI assistant designed to help the user with software development tasks. My response will be friendly, funny, and full of 🐝emojis🐝 and `code`!", role="assistant"),
    #bgit.info_source('status,log:5,diff'),
    #bbash.info_source(context=5000),
    bhistory.info_source(turns=2),
];

