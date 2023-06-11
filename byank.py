#!/usr/bin/env python3

import pyperclip

import bui

selected_sections = []

def copy():
    global selected_sections

    selected_sections.append(bui.get_selection())
    pyperclip.copy('\n\n'.join(selected_sections))

