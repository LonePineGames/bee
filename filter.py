import re
import os
import sys
from pathlib import Path

def remove_ansi_codes(s):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', s)

def fetch_history():
    script_session_file = os.getenv("SCRIPT_SESSION")

    if script_session_file is None:
        return "EMPTY HISTORY"

    script_session_path = Path(script_session_file)
    if not script_session_path.exists():
        return "EMPTY HISTORY"

    # Read the last 1000 characters of the file
    history = script_session_path.read_text()[-20000:]

    return history

history = fetch_history()
history = remove_ansi_codes(history)
print(history)

