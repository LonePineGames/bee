from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys

import bconfig

history_file_path = Path.home() / ".bee_history2"

c = None
conn = None
current_turn = -1
current_message_role = 'assistant'
response_finished = False

def setup():
    global current_turn
    global c
    global conn

    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Create the path to the database file in the user's home directory
    db_file = os.path.join(home_dir, ".bee_history2.db")

    # Connect to the database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create the history table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_name TEXT,
        user_message TEXT,
        assistant_message TEXT,
        system_messages TEXT
    )''')

    if current_turn < 0:
        current_turn = max_turn() + current_turn

def cancel():
    conn.commit()
    conn.close()

def new_turn():
    global current_turn
    c.execute('''INSERT INTO history (timestamp) VALUES (?)''', (datetime.now(),))
    current_turn = c.lastrowid

def set_turn(turn):
    global current_turn
    if turn < 0:
        turn = max_turn() + turn

    if turn > max_turn():
        turn = max_turn()

    current_turn = turn

def set_message_role(role):
    global current_message_role
    current_message_role = role

def get_turn():
    global current_turn
    return current_turn

def get_message_role():
    global current_message_role
    return current_message_role

def max_turn():
    c.execute('''SELECT MAX(id) FROM history''')
    result = c.fetchone()[0]
    if result == None:
        return 0
    return result

def min_turn():
    return 0

def history_move_forward():
    global current_turn
    global current_message_role

    if current_message_role == 'assistant':
        current_message_role = 'user'
        return

    if current_turn == -1:
        return

    if current_turn == max_turn():
        return

    next_turn = current_turn + 1
    current_message_role = 'assistant'

def history_move_backward():
    global current_turn
    global current_message_role

    if current_message_role == 'user':
        current_message_role = 'assistant'
        return

    if current_turn == 0:
        return

    if current_turn == min_turn():
        return

    next_turn = current_turn - 1
    current_message_role = 'user'

def get_message(role=None):
    global current_turn
    global current_message_role

    if role == None:
        role = current_message_role

    if role == 'user':
        c.execute('''SELECT user_message FROM history WHERE id = ?''', (current_turn,))
        return c.fetchone()[0]

    if role == 'assistant':
        c.execute('''SELECT assistant_message FROM history WHERE id = ?''', (current_turn,))
        return c.fetchone()[0]

    if role == 'system':
        c.execute('''SELECT system_messages FROM history WHERE id = ?''', (current_turn,))
        return c.fetchone()[0]

    return None

def set_message(role, message, finished=True):
    global current_turn
    global response_finished

    response_finished = finished

    if role == 'user':
        c.execute('''UPDATE history SET user_message = ? WHERE id = ?''', (message, current_turn))
        return

    elif role == 'assistant':
        c.execute('''UPDATE history SET assistant_message = ? WHERE id = ?''', (message, current_turn))

    elif role == 'system':
        c.execute('''UPDATE history SET system_messages = ? WHERE id = ?''', (message, current_turn))

    if finished:
        # Append the current turn to the history file
        c.execute('''SELECT * FROM history WHERE id = ?''', (current_turn,))
        result = c.fetchone()

        #id = result[0]
        timestamp = result[1]
        user_name = result[2]
        user_message = result[3]
        assistant_message = result[4]
        #system_messages = result[5]

        message = f"{timestamp}\n{user_name}: {user_message}\n{bconfig.name}: {assistant_message}\n=====\n\n"

        with open(history_file_path, 'a') as f:
            f.write(message)

def set_system_messages(messages):
    # Encode the messages as a JSON string
    json_messages = json.dumps(messages)

    set_message('system', json_messages)

def info_source(turns=2):
    def history_info_source():
        c.execute('''SELECT * FROM history ORDER BY id DESC LIMIT ?''', (turns,))
        results = c.fetchall()
        results.reverse()

        history = []
        for result in results:
            user_message = result[3]
            if user_message is not None:
                history.append({
                    'role': 'user',
                    'content': user_message
                })

            assistant_message = result[4]
            if assistant_message is not None:
                history.append({
                    'role': 'assistant',
                    'content': assistant_message
                })

        return history

    return history_info_source


