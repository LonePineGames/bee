import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

history_file_path = Path.home() / ".bee_history"

# Get the user's home directory
home_dir = os.path.expanduser("~")

# Create the path to the database file in the user's home directory
db_file = os.path.join(home_dir, ".bee_history.db")

# Connect to the database
conn = sqlite3.connect(db_file)
c = conn.cursor()

# Create the history table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS history
             (role TEXT, content TEXT, timestamp TIMESTAMP)''')

# Insert a new message into the history table
def save_response(response, role):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values = (role, response, timestamp)
    c.execute("INSERT INTO history VALUES (?, ?, ?)", values)
    conn.commit()

    if role == "assistant":
        with open(history_file_path, "w") as f:
            f.write(response)

# Retrieve the conversation history from the database
def get_history(turns):
    c.execute("SELECT role, content, timestamp FROM history ORDER BY timestamp DESC LIMIT ?", (turns,))
    return [{"role": role, "content": content, "timestamp": timestamp}
            for role, content, timestamp in c.fetchall()]

# Close the database connection when finished
def close():
    conn.close()

def get_user_message():
    return ' '.join(sys.argv[1:])

def get_prev_response():
    c.execute("SELECT content FROM history WHERE role = 'assistant' ORDER BY timestamp DESC LIMIT 1")
    return c.fetchone()[0]

# Use the info_source function to retrieve the history
def info_source(turns=2):
    def history_info_source():
        history = get_history(turns)
        history.reverse()
        result = [{"role": item["role"], "content": item["content"]} for item in history]
        return result

    return history_info_source


