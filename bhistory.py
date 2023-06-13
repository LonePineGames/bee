from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys

import bconfig
import bbash
import bui

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

    # Check if the database file exists
    db_file_exists = os.path.isfile(db_file)

    # Connect to the database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute('pragma busy_timeout=10000')
    c.execute('pragma journal_mode=wal')

    # Create the history table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_name TEXT,
        user_message TEXT,
        assistant_message TEXT,
        system_messages TEXT
    )''')

    if not db_file_exists:
        new_turn()
        set_message('user', 'Hello, Bee!')
        set_message('assistant', 'Hi! I\'m Bee, your personal assistant.', finished=True)

    if current_turn < 0:
        current_turn = max_turn() + current_turn + 1

def cancel():
    conn.commit()
    conn.close()

def new_turn():
    global current_turn
    c.execute('''INSERT INTO history (timestamp, user_name, user_message, assistant_message, system_messages) VALUES (?, '', '', '', '')''', (datetime.now(),))
    current_turn = c.lastrowid
    #bui.print(current_turn)

def set_turn(turn):
    global current_turn
    if turn < 0:
        turn = max_turn() + turn + 1

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
        return 1
    return result

def min_turn():
    return 1

def move_forward():
    global current_turn
    global current_message_role

    if current_message_role == 'user':
        current_message_role = 'assistant'
        return True

    if current_turn == -1:
        return False

    if current_turn == max_turn():
        return False

    current_turn = current_turn + 1
    current_message_role = 'user'
    return True

def move_backward():
    global current_turn
    global current_message_role
    global response_finished

    if current_message_role == 'assistant':
        current_message_role = 'user'
        response_finished = True
        return True

    if current_turn == min_turn():
        return False

    current_turn = current_turn - 1
    current_message_role = 'assistant'
    response_finished = True
    return True

def get_name(role=None):
    global current_turn
    global current_message_role

    if role == None:
        role = current_message_role

    if role == 'user':
        c.execute('''SELECT user_name FROM history WHERE id = ?''', (current_turn,))
        result = c.fetchone()
        if result is None:
            return bconfig.your_name
        return result[0]

    elif role == 'assistant':
        return bconfig.name

    else:
        return role

def get_message(role=None):
    global current_turn
    global current_message_role

    if role == None:
        role = current_message_role

    result = None

    if role == 'user':
        c.execute('''SELECT user_message FROM history WHERE id = ?''', (current_turn,))
        result = c.fetchone()

    elif role == 'assistant':
        c.execute('''SELECT assistant_message FROM history WHERE id = ?''', (current_turn,))
        result = c.fetchone()

    elif role == 'system':
        c.execute('''SELECT system_messages FROM history WHERE id = ?''', (current_turn,))
        result = c.fetchone()

    if result is not None:
        return result[0]

    return ''

def set_message(role, message, finished=False):
    global current_turn

    if role == 'user':
        user_name = bbash.get_user_name()
        c.execute('''UPDATE history SET user_message = ?, user_name = ? WHERE id = ?''', (message, user_name, current_turn))
        return

    elif role == 'assistant':
        c.execute('''UPDATE history SET assistant_message = ? WHERE id = ?''', (message, current_turn))

    elif role == 'system':
        c.execute('''UPDATE history SET system_messages = ? WHERE id = ?''', (message, current_turn))

def finish_response():
    global response_finished
    response_finished = True

    # Append the current turn to the history file
    c.execute('''SELECT * FROM history WHERE id = ?''', (current_turn,))
    result = c.fetchone()

    #id = result[0]
    timestamp = result[1]
    user_name = result[2]
    user_message = result[3]
    assistant_message = result[4]
    #system_messages = result[5]

    message = f"{timestamp}\n{user_name}: {user_message}\n\n{bconfig.name}: {assistant_message}\n=====\n\n"

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


