
The way it works is, I run a shell command like `b Help me with this python issue...` and Bee (GPT) can respond based on shell history (typescript) and a single turn of conversation history.

It works pretty well, but I'm not sure where to go next. Some things I'm thinking about: 
* break up the file into smaller files for easier development
* allow the user to interact with the keyboard while the streaming response is still arriving (make call_openai_api async or threaded or something)
* collect the conversation history, maybe in sqlite, maybe in a separate daemon
* building on the logs of conversation history, maybe create an webapp that can produce colorful html logs using aha or AnsiPress.
* add a way to select between gpt-3.5-turbo and gpt-4, which is smarter but slower and more expensive. Maybe I can call `b4` to get gpt-4.
* if I call b with a filename (eg `b main.py Help me with this python file...`) then Bee sees the file or part of the file
* some sort of search algo / classical AI algo that can filter all the possible input to Bee for the most relevant things. I can feed Bee information from different sources including conversation history, shell history/typescript, the content of files, etc. How can I most intelligently decide which information to put in the context window, to make most economic use of tokens?

I want to work towards a system where I can write `./bash_script.sh | b "Handle this script output" > bee_output.txt. It would be nice to retain as much interactivity (or as little as the user chooses) to maintain the nice Bee interface. I think I want to use stdin and stdout, probably I want to detect when b is being called as part of a script, and then disable rich.live and just use stdout? Disable keyboard handling?
