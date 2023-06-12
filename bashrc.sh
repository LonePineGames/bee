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

# Moon message -- remove it if you don't like it
moon_info=$(python3 -path-/moon_phase.py)
echo $moon_info | b "I am currently sitting down to code. Please write a short, motivating message for me! (40 words or less.)"

### 🐝BEE HEADER END ###

