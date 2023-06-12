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

    selection = bui.get_selection()

    if len(selected_sections) > 0 and selection == selected_sections[-1]:
        selected_sections = [selection]

    elif selection in selected_sections:
        return

    else:
        selected_sections.append(selection)

    #bui.print('copied: ' + str(selected_sections))
    pyperclip.copy('\n\n'.join(selected_sections))

