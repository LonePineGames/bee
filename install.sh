#!/bin/bash

BYLW="\033[93m"
BBLU="\033[34m"

#echo -e "${BYLW}Installing Bee 🐝"
#echo -e "${BBLU}Installing Bee 🐝"

BEE_VERSION=$(./b -v)
BEE_PATH=`pwd`

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

animate "${BYLW} 🐝 _______  _______  _______  _______  _______  _______  _______  _______  _______  _______ _______  _______  _______  _______  _______  _______  _______  _______  _______  _______\n"

./b -v

animate "\n${BYLW}Installing from ${BEE_PATH}...\n\n"

sleep 1

animate "🐝Bee is a command line assistant that helps you with your daily tasks. I'm here to make your life easier! 🐝\n \n"

sleep 1

# Check to see if apikey.py exists
if [ -f apikey.py ]; then
    animate "🔑 I found an OpenAI API key in apikey.py.\n"
    sleep 1
    animate "I'll use that one.\n\n"
    sleep 1

else
    # Prompt the user for their OpenAI API key
    # https://platform.openai.com/account/api-keys
    animate "🔑 I need an OpenAI API key to work.\n"
    animate "Please get one at https://platform.openai.com/account/api-keys\n"
    echo -ne "${BBLU}"
    read -p "Please enter your OpenAI API key 🔑: " OPENAI_API_KEY
    # Write the API key to apikey.py
    #echo "OPENAI_API_KEY = \"$OPENAI_API_KEY\"" > apikey.py
    sleep 1

    animate "${BYLW}Key saved! 🔑\n\n"
    sleep 1
fi

# Read ~/.bashrc into a variable
user_bashrc=$(cat ~/.bashrc)

# In case Bee is already installed...
if [[ $user_bashrc == *"### 🐝BEE HEADER END ###"* ]]; then
    animate "Looks like Bee was previously installed!\n"
    sleep 1
    animate "I'll clean up the old version first...\n\n"
    ./uninstall.sh > /dev/null
fi

bee_bashrc=$(cat ./bashrc.sh)
# Replace -version- with the current version
bee_bashrc=${bee_bashrc//-version-/`./b -v`}
# Replace -path- with the current path
bee_bashrc=${bee_bashrc//-path-/`pwd`}

# Get the shebang from the user's ~/.bashrc, and the rest of the file
shebang=$(head -n 1 ~/.bashrc)
rest=$(tail -n +2 ~/.bashrc)

# If the user's ~/.bashrc doesn't have a shebang, default to bash
if [[ $shebang != *"#!"* ]]; then
    rest="$shebang\n$rest"
    shebang="#!/bin/bash"
fi

user_bashrc="${shebang}\n${bee_bashrc}\n${rest}"
echo -e "$user_bashrc" > ~/.bashrc

source ~/.bashrc

animate "${BYLW} 🐝 _______  _______  _______  _______  _______  _______  _______  _______  _______  _______ _______  _______  _______  _______  _______  _______  _______  _______  _______  _______\n"
sleep 1

animate "\nBee 🐝 installation complete!\n\n"
sleep 1

animate "Buzz buzz! Using me is easy! 🤗\n"
sleep 1
animate "Just type '${BBLU}b \"<your question>\"${BYLW}' in your terminal and I'll be there to help you out! \n\n"
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
animate "    🐝   $ ${BBLU}b4 \"Help me with this horrible C++ error message :(\"${BYLW}\n"
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
animate "   All this information really helps me out! 😃\n"
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
animate "   - '${BBLU}bemoji finger pointing right${BYLW}'\n"
sleep 1
animate "       I can help you search for an emoji!\n"
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

animate "👉 For more options, type '${BBLU}b --help${BYLW}'\n"
sleep 1

animate "\n🐝 Have fun coding! 🐝\n"
sleep 1

