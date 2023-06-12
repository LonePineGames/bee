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

### 🐝BEE HEADER END ###

