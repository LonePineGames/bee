COLOR_YELLOW="\033[93m"

echo -e "\n${COLOR_YELLOW} 🐝 _______  _______  _______  _______  _______  _______  _______  _______  _______  _______ _______  _______  _______  _______  _______  _______  _______  _______  _______  _______\n"

user_bashrc=$(cat ~/.bashrc)
if [[ $user_bashrc == *"### 🐝BEE HEADER END ###"* ]]; then
  echo "Removing Bee 🐝 from ~/.bashrc"

  sed -i '/### 🐝BEE HEADER START ###/,/### 🐝BEE HEADER END ###/d' ~/.bashrc

  echo "Sorry to see you go! 🐝"
  echo "Please restart your terminal to complete the uninstall."
else
  echo "Bee 🐝 is not installed."
fi

#echo -e "\n"


