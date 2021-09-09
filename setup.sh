#!/bin/bash
# Authors: Frank Kwizera

# 0. Define factory methods.
print_to_user() {
  echo $1
}

append_to_bashrc() {
  echo  $1 >> ~/.bashrc
}

set_git_hooks() {
  git config core.hooksPath $PWD/hooks
}

configure_flake8_strict() {
  git config flake8.strict true
}

# 1. Set git hooks
print_to_user "Configuring git hooks."
set_git_hooks

# 2. Configuring strictness of flake8 tests
print_to_user "Configuring flake"
configure_flake8_strict

# 2. Check if system has .bashrc file.
FILE=~/.bashrc
if ! test -f "$FILE"; then
    print_to_user "This setup is incompatible with your system."
    exit
fi

# 3. Check if the changes were not made in the past. Avoid duplicate exports. 
if grep -q "^export PYTHONPATH=:$PWD$" ~/.bashrc ; then
print_to_user "Path already set."
print_to_user "Setup completed."
  exit 
fi

bold=$(tput bold)
normal=$(tput sgr0)
green='\e[0;32m'

# 4. append the export command to the .bashrc file
append_to_bashrc "# Auction App"
append_to_bashrc "export PYTHONPATH=$PYTHONPATH:$PWD"
append_to_bashrc "export PATH=$PATH:$PWD"
print_to_user "-> $PYTHONPATH added to PYTHONPATH"
print_to_user "-> $PATH now includes current directory"
print_to_user "Setup completed!"

# 5. Final message to the user 
print_to_user "${green} Setup has been configured.${normal}, but "
print_to_user "You need to run ${bold}source ~/.bashrc${normal} for changes to take effect or reboot the system."