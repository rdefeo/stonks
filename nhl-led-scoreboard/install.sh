#!/bin/bash

# User warning
echo "This will install the 'stonks' board to your nhl-led-scoreboard"
echo ""
echo "WARNING: This will modify files in your nhl-led-scoreboard directory. No backups will be made"
echo ""
echo "If you have already run this installer, running it again may produce errors"
echo "To start from scratch, press Ctrl-C, and then reinstall nhl-led-scoreboard before trying again"
echo ""
read -r -p "Are you sure you want to continue? [y/N]: " choice
choice=${choice,,} # tolower
if [[ $choice =~ ^(no|n| ) ]] || [[ -z $choice ]]; then
    echo "Aborting stonks install..."
    exit
fi

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo ""
cd "${DIR}" || exit

# Install all pip3 requirements using the requirements.txt file
echo "Installing required python packages..."
sudo pip3 install -r requirements.txt --upgrade

# Modify the nhl-led-scoreboard source to inject Stonks
echo "Modifying nhl-led-scoreboard installation for stonks..."
python3 install_modify.py

cd "/.." || exit
echo -e "\nIf you didn't see any errors above, stonks should be installed!\n"
echo "$(tput bold)$(tput smso)$(tput setaf 2)Install script complete!$(tput sgr0)"