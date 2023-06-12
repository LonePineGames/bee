#!/bin/bash

BYLW="\033[93m"
BBLU="\033[34m"
BWHT="\033[97m"

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

animate "${BYLW}🐝 _______  _______  _______  _______  _______  _______  _______  _______  _______  _______ _______  _______  _______  _______  _______  _______  _______  _______  _______  _______\n"

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
    animate "Please enter your OpenAI API key 🔑 "
    echo -ne "${BBLU}"
    read -p ": " OPENAI_API_KEY
    # Write the API key to apikey.py
    echo "OPENAI_API_KEY = \"$OPENAI_API_KEY\"" > apikey.py
    sleep 1

    animate "${BYLW}Key saved! 🔑\n\n"
    sleep 1
fi

animate "${BYLW}Let's make sure that you have the 🐍python requirements installed... \n\n"
sleep 1

# Check to see if python3 is installed
if ! command -v python3 &> /dev/null
then
    animate "🐍 Python3 is not installed. Please install it, then run this script again.\n"
    sleep 1
    exit
fi

# Check to see if python3 is installed
if ! command -v pip3 &> /dev/null
then
    animate "🐍 pip3 is not installed. Please install it, then run this script again.\n"
    sleep 1
    exit
fi

echo -ne "${BWHT}"

# Install the python requirements
pip3 install -r requirements.txt

echo -ne "${BYLW}"

if [ $? -eq 0 ]; then
    animate "\n🐍 Python requirements installed! \n\n"
    sleep 1
else
    animate "\n🐍 Python requirements failed to install. Please try again.\n"
    sleep 1
    exit
fi

# Read ~/.bashrc into a variable
user_bashrc=$(cat ~/.bashrc)

# In case Bee is already installed...
if [[ $user_bashrc == *"### 🐝BEE HEADER END ###"* ]]; then
    animate "Looks like Bee was previously installed!\n"
    sleep 1
    animate "I'll clean up the old version first...\n\n"
    ./uninstall.sh -q
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

animate "I'm installed! But now I have to source ~/.bashrc to make sure I'm ready to go...\n"
sleep 1

echo -ne "${BWHT}"
source ~/.bashrc

