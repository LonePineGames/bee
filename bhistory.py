from pathlib import Path
import sys

prev_response = None
history_path = Path.home() / ".bee_history"

def get_prev_response():
    global prev_response
    if prev_response is None:
        with open(history_path, "r") as f:
            prev_response = f.read()
    return prev_response

def save_response(response):
    with open(history_path, "w") as f:
        f.write(response)

def user_message():
    return ' '.join(sys.argv[1:])

def info_source(turns=2):
    def history_info_source():
        return [
            {"role": "assistant", "content": get_prev_response()},
            {"role": "user", "content": user_message()}
        ]
    return history_info_source

