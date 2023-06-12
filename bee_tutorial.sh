#!/bin/bash

BYLW="\033[93m"
BBLU="\033[34m"

function animate {
  message=$1
  length=${#message}
  for (( i=0; i<${length}; i+=5 )); do
    segment="${message:$i:5}"
    if [[ $segment == *"\0"* ]]; then
      segment="${message:$i:10}"
      i=$((i+5))
    fi
    echo -ne "${segment}"
    sleep 0.05
  done
}

animate "${BYLW}🐝 _______  _______  _______  _______  _______  _______  _______  _______  _______  _______ _______  _______  _______  _______  _______  _______  _______  _______  _______  _______\n"

b -v

if [[ $? -ne 0 ]]; then
    animate "${BYLW}Looks like you don't have Bee installed yet! Let's fix that...\n"
    sleep 1
    ./install.sh
    exit
fi

animate "\n${BYLW}Bee 🐝 installation complete!\n\n"
sleep 1

touch ./.bee_tutorial_ran

animate "Buzz buzz! Using me is easy! 🤗\n"
sleep 1
animate "Just type '${BBLU}b \"<your question>\"${BYLW}' in your terminal \n"
animate "   -- and I'll be there to help you out! \n\n"
sleep 1

animate "    🐝   $ ${BBLU}b \"How do I configure my git username?\"${BYLW}\n"
sleep 1
animate "    🐝   $ ${BBLU}b \"How can I search for a string in a file?\"${BYLW}\n"
sleep 1
animate "    🐝   $ ${BBLU}b \"Can you help me setup a quick webserver?\"${BYLW}\n"
sleep 1
animate "    🐝   $ ${BBLU}b main.cpp \"I don't understand this error message. Can you help?\"${BYLW}\n"
sleep 1
animate "    🐝   $ ${BBLU}b \"Show me how to spawn a new thread in {favorite language}.\"  ${BYLW}"
sleep 1

animate "\n\n👉 I'll give you answers -- plus code you can copy or run immediately. Press X to execute and C to copy. Use WASD to navigate. \n"
sleep 1
animate "👉 Press Q to quit -- then type 'b' with no arguments to see my last reply again.\n\n"
sleep 1

animate "👉 If you want to use GPT-4, just type b4 instead of b! \n"
sleep 1
animate "    🐝   $ ${BBLU}b4 \"HELP ME! What is this gnarly C++ error message? :(\"${BYLW}\n"
sleep 1
animate "        Then I'll be even smarter! (Requires GPT-4 API Access) \n"
sleep 1

# finger pointing emoji: 👉
# eyes emoji: 👀

animate "👉 Just so you know, I can 👀see your: \n"
sleep 1
animate "    - bash session history\n"
sleep 1
animate "    - git repo status\n"
sleep 1
animate "    - system clipboard contents\n"
sleep 1
animate "    - any file you pass me by typing '${BBLU}b file.name${BYLW}'\n"
sleep 1
animate "    (OpenAI sees this too 🤔)\n"
sleep 1
animate "   But all this information really helps me out! 😃\n \n"
sleep 1

animate "👉 More ways to use me: \n"
sleep 1
animate "   - '${BBLU}b${BYLW}' to see my last reply\n"
sleep 1
animate "   - '${BBLU}bee${BYLW}' to use your \$EDITOR to ask your question.\n"
sleep 1
animate "       Then bash won't get in the way!\n"
sleep 1
animate "       (Stuck in vim? Ask me how to configure your \$EDITOR) \n"
sleep 1
animate "   - '${BBLU}bemoji tree${BYLW}' \n"
sleep 1
animate "       I can help you search for an emoji!🌼🌸💐🏵️\n"
sleep 1
animate "   - '${BBLU}bwrite public/reset.css${BYLW}'\n"
sleep 1
animate "       I can quickly prototype files for you!\n"
sleep 1
animate "   - '${BBLU}ps aux --sort=%mem | b \"What's using all my memory?\"${BYLW}'\n"
sleep 1
animate "       Pipe any command to me to get a quick explanation.\n"
sleep 1
animate "   - '${BBLU}./configure || b4 \"What do I need to install? Use sudo.\" | grep \"sudo apt\"${BYLW}'\n"
sleep 1
animate "       Use b in your automation scripts!\n"
sleep 1

animate "👉 If you want to configure me, open up this file: ${BBLU}bconfig.py${BYLW}.\n"
sleep 1
animate "    You can change colors, change the keymap, even write your own plugins! \n\n"
sleep 1

animate "👉 For more options, type '${BBLU}b --help${BYLW}'\n\n"
sleep 1

animate "${BYLW}(😞 Oh, and if you don't want to see my welcome message every time you open a new terminal -- I understand! -- just edit ${BBLU}~/.bashrc ${BYLW}to remove it. 😞)\n"
sleep 1

animate "\n🐝 Have fun coding! 🐝\n"
sleep 1

