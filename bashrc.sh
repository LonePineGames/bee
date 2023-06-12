### 🐝BEE HEADER START ###
# -version-

if [ "$SCRIPT_SESSION" == "" ]
then
    mkdir -p $HOME/sessions
    export SCRIPT_SESSION="$HOME/sessions/`date +%F-%T`-typescript.log"
    script -f $SCRIPT_SESSION
    exit
fi

export PATH="$PATH:-path-" # Bee
alias b4="b -4" # Bee w/ GPT-4
alias bhistory="b --history=20"

# Welcome message -- remove it if you don't like it
bee_narrates.sh

# Bee Tutorial
if [ ! -f -path-/.bee_tutorial_ran ]
then
    touch -path-/.bee_tutorial_ran
    # run the tutorial
    -path-/bee_tutorial.sh
fi

### 🐝BEE HEADER END ###

