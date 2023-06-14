#!/bin/bash

echo ""
moon_info=$(moon_phase.py)
joke=$(python3 -c "import pyjokes; print(pyjokes.get_joke())")
info="$moon_info\nJoke of the Day: $joke"
echo -e "$info"
echo -e "$info" | b --exit-immediately "This is an automated message. I am currently logging in to code, and you're going to help! Please write a short, friendly welcome narrative for me! (40 words or less.) Use my name: $(whoami)."

