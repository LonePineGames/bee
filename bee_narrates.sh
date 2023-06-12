#!/bin/bash

info=$(python3 moon_phase.py)
python3 moon_phase.py
echo -e $info
echo "" # newline
echo $info | b "I am currently sitting down to code. Please write a short, motivating message for me!"

