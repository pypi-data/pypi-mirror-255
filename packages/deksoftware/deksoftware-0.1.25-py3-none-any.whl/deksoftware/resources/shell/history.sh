#!/bin/bash

sudo cat <<EOF | tee ~/.inputrc
"\e[A": history-search-backward
"\e[B": history-search-forward
EOF
#bind -f  ~/.inputrc

sudo rm -rf ~/.bash_history
history -c
