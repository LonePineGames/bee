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
    elif [[ $segment == *"\n"* ]]; then
      segment="${message:$i:10}"
      i=$((i+5))
    fi
    echo -ne "${segment}"
    sleep 0.05
  done
}

animate "${BYLW}🐝 _______  _______  _______  _______  _______  _______  _______  _______  _______  _______ _______  _______  _______  _______  _______  _______  _______  _______  _______  _______\n"

b -v
sleep 1

if [[ $? -ne 0 ]]; then
    animate "${BYLW}Looks like you don't have Bee installed yet! Let's fix that..."
    sleep 1
    echo ""
    ./install.sh
    exit
fi

animate "\n${BYLW}Bee 🐝 installation complete!"
sleep 1
echo -ne "\n\n"

touch ./.bee_tutorial_ran

animate "Buzz buzz! Using me is easy! 🤗"
sleep 1
echo ""
animate "Just type \`${BBLU}b \"<your question>\"${BYLW}\` in your terminal"
sleep 1
echo ""
animate "   -- and I'll be there to help you out!"
sleep 1
echo -ne "\n\n"

animate "    🐝 $ ${BBLU}b \"How do I configure my git username?\""
sleep 1
echo -ne "$BYLW\n"
animate "    🐝 $ ${BBLU}b \"How can I search for a string in a file?\""
sleep 1
echo -ne "$BYLW\n"
animate "    🐝 $ ${BBLU}b \"Can you help me setup a quick webserver?\""
sleep 1
echo -ne "$BYLW\n"
animate "    🐝 $ ${BBLU}b main.cpp \"I don't understand this error message. Can you help?\""
sleep 1
echo -ne "$BYLW\n"
animate "    🐝 $ ${BBLU}b \"Show me how to spawn a new thread in {favorite language}.\""
sleep 1
echo -ne "$BYLW\n\n"

animate "👉 I'll give you answers -- plus code you can copy or run immediately."
sleep 1
echo ""
animate "   Press X to execute and C to copy. Use WASD to navigate, Q to quit."
sleep 1
echo -ne "\n\n"

animate "👉 If you want to use GPT-4, just type b4 instead of b!"
sleep 1
echo ""
animate "    🐝 $ ${BBLU}b4 \"HELP ME! What is this gnarly C++ error message? :(\""
sleep 1
echo -ne "${BYLW}\n"
animate "        Then I'll be even smarter! (Requires GPT-4 API Access)"
sleep 1
echo ""

animate "👉 Just so you know, I can 👀see your:"
sleep 1
echo ""
animate "    - bash session history"
sleep 1
echo ""
animate "    - git repo status"
sleep 1
echo ""
animate "    - system clipboard contents"
sleep 1
echo ""
animate "    - any file you pass me by typing \`${BBLU}b file.name${BYLW}\`"
sleep 1
echo ""
animate "    (OpenAI sees this too 🤔)"
sleep 1
echo ""
animate "   But all this information really helps me out! 😃"
sleep 1
echo -ne "\n\n"

animate "👉 More ways to use me:"
sleep 1
echo ""
animate "    🐝 $ ${BBLU}b      ${BYLW}   # to see my last reply"
sleep 1
echo -ne "${BYLW}\n"

animate "    🐝 $ ${BBLU}bee    ${BYLW}   # to use your \$EDITOR to ask your question."
sleep 1
echo ""
animate "           Then bash won't get in the way!"
sleep 1
echo ""
animate "           (Stuck in vim? Ask me how to configure your \$EDITOR)"
sleep 1
echo ""

animate "    🐝 $ ${BBLU}brerun ${BYLW}   # edit and re-run your last command"
sleep 1
echo -ne "${BYLW}\n"
animate "           (\`${BBLU}brerun -4${BYLW}\` to re-run with GPT-4)"
sleep 1
echo ""

animate "    🐝 $ ${BBLU}bemoji hand pointing right"
sleep 1
echo -ne "${BYLW}\n"
animate "           I can help you search for an 👉emoji!🌼🌸💐🏵️"
sleep 1
echo ""

animate "    🐝 $ ${BBLU}bwrite public/reset.css"
sleep 1
echo -ne "${BYLW}\n"
animate "           I can quickly prototype files for you!"
sleep 1
echo ""

animate "    🐝 $ ${BBLU}ps aux --sort=%mem | b \"What's using all my memory?\""
sleep 1
echo -ne "${BYLW}\n"
animate "           Pipe any command to me to get a quick explanation."
sleep 1
echo -ne "\n\n"

animate "           Or... 😱"
sleep 1
echo ""
animate "             Use Bee in your automation scripts! 🤯"
sleep 1
echo ""
animate "    🐝 $ ${BBLU}./configure | b_or_not \"Did ./configure succeed?\" || \\"
echo ""
animate "         b4 --blocks \"What do I need to install? Use sudo.\" > temp.sh;"
echo ""
animate "         b_or_not temp.sh \"Is this a valid script?\" && \\"
sleep 1
echo ""
animate "         ..."
sleep 2
echo -ne "$BYLW\n\n"

animate "👉 If you want to configure me, open up this file: ${BBLU}bconfig.py${BYLW}.\n"
sleep 1
animate "    You can change colors, change the keymap, even write your own plugins! \n"
sleep 1
animate "👉 For more options, type '${BBLU}b --help${BYLW}'\n\n"
sleep 1

animate "${BYLW}(😞 Oh, and if you don't want to see my welcome message every time you open a new terminal -- I understand! -- just edit ${BBLU}~/.bashrc ${BYLW}to remove it. 😞)\n"
sleep 1

animate "\n🐝 Have fun coding! 🐝"
sleep 2
echo ""

