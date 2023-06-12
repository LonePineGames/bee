COLOR_YELLOW="\033[93m"

# if -q, do it quickly and quietly
if [[ $1 == "-q" ]]; then
  sed -i '/### 🐝BEE HEADER START ###/,/### 🐝BEE HEADER END ###/d' ~/.bashrc
  exit 1
fi

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

animate "${COLOR_YELLOW}🐝 _______  _______  _______  _______  _______  _______  _______  _______  _______  _______ _______  _______  _______  _______  _______  _______  _______  _______  _______  _______\n \n"
sleep 1

user_bashrc=$(cat ~/.bashrc)
if [[ $user_bashrc == *"### 🐝BEE HEADER END ###"* ]]; then
  animate "Removing Bee 🐝 from ~/.bashrc \n"

  sed -i '/### 🐝BEE HEADER START ###/,/### 🐝BEE HEADER END ###/d' ~/.bashrc

  sleep 1
  animate "Sorry to see you go! 🐝\n"
  sleep 1
  animate "Please 🔁restart your terminal💻 to complete the uninstall.\n"
  sleep 1
else
  animate "Bee 🐝 is not installed."
  sleep 1
fi

#echo -e "\n"


