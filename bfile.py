import os

def get_cursor_pos(filename):
    viminfo_file = os.path.expanduser("~/.viminfo")
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

