import pyperclip

import bui

selected_sections = []

def info_source(role="system"):
    # print('git_info_source')
    # bgit.info_source('status,log:5,diff'),
    def yank_info_source():
        paste = pyperclip.paste()
        if paste:
            return [{ "role": role, "content": "--- CLIPBOARD ---\n\n" + paste }]
        else:
            return []

    return yank_info_source

def copy():
    global selected_sections

    selected_sections.append(bui.get_selection())
    pyperclip.copy('\n\n'.join(selected_sections))

