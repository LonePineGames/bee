import os
import sys

def get_cursor_pos(filename):
    viminfo_file = os.path.expanduser("~/.local/share/nvim")
    with open(viminfo_file, "r") as f:
        for line in f:
            if line.startswith("'\""):
                parts = line.split(":")
                if len(parts) > 3 and parts[1] == filename:
                    try:
                        return int(parts[3])
                    except ValueError:
                        pass
    return None

def read_around_cursor(filename, num_chars=1500):
    cursor_pos = get_cursor_pos(filename)
    if cursor_pos is None:
        cursor_pos = 0

    with open(filename, 'r') as f:
        file_length = len(f.read())
        start_pos = max(0, cursor_pos - num_chars/2)
        if cursor_pos + num_chars < file_length:
            start_pos = max(0, min(start_pos, file_length - num_chars))
        # Move the file pointer to the cursor position
        f.seek(start_pos)

        to_read = min(num_chars, file_length - start_pos)

        return f.read(to_read)

def info_source(role="user"):
    def file_info_source():
        args = sys.argv[1:]
        results = []
        for filename in args:
            print(filename, os.path.isfile(filename))
            # if the file doesn't exist, continue
            if os.path.isfile(filename) == False:
                continue

            contents = read_around_cursor(filename, num_chars=1000)
            #print(contents)
            if contents:
                results.append({ "role": role, "content": f"--- {filename} ---\n{contents}" })

        return results

    return file_info_source

