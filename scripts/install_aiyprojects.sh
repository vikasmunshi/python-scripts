#!/usr/bin/env bash
########################################################################################################################
#    Script to setup google aiy voice kit on Raspberry Pi 3 B+ running Raspbian                                        #
#    Based on instructions at:                                                                                         #
#    https://github.com/google/aiyprojects-raspbian/blob/aiyprojects/HACKING.md                                        #
#    https://speakerdeck.com/savelee/aiy-voicekit-workshop                                                             #
#                                                                                                                      #
#    Author: Vikas Munshi <vikas.munshi@gmail.com>                                                                     #
#    Version 1.0.1: 2018.04.11                                                                                           #
#                                                                                                                      #
#    Source: https://github.com/vikasmunshi/python-scripts/blob/master/scripts/install_aiyprojects.sh                  #
#    Example usage:                                                                                                    #
#    bash <(curl -s https://raw.githubusercontent.com/vikasmunshi/python-scripts/master/scripts/install_aiyprojects.sh)#
#                                                                                                                      #
########################################################################################################################
#    MIT License                                                                                                       #
#                                                                                                                      #
#    Copyright (c) 2018 Vikas Munshi                                                                                   #
#                                                                                                                      #
#    Permission is hereby granted, free of charge, to any person obtaining a copy                                      #
#    of this software and associated documentation files (the "Software"), to deal                                     #
#    in the Software without restriction, including without limitation the rights                                      #
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell                                         #
#    copies of the Software, and to permit persons to whom the Software is                                             #
#    furnished to do so, subject to the following conditions:                                                          #
#                                                                                                                      #
#    The above copyright notice and this permission notice shall be included in all                                    #
#    copies or substantial portions of the Software.                                                                   #
#                                                                                                                      #
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR                                        #
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,                                          #
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE                                       #
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER                                            #
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,                                     #
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE                                     #
#    SOFTWARE.                                                                                                         #
########################################################################################################################

# terminate script on error
set -e
# switch to home dir, rest of the script uses relative paths
cd

# involves reboot, so we keep track of progress in a flag file managed using: read_stage, update_stage, reboot_nicely
# use dot file in home dir as flag file to keep track of stages; support execution from URL
[[ -f $0 ]] && flag=~/.$(basename $0).done || flag=~/.install_aiyprojects.sh.done

# read last known stage from flag file, default 0
read_stage() { [[ -f ${flag} ]] && head -n 1 ${flag} | tr -d \n || echo -n 0 ;}

# add one to current stage and write to flag file
update_stage() { stage=$((${stage}+1)); echo -n ${stage} >${flag} ;}

# to maintain consistency in interaction using ask_user 'choice 1' 'choice 2' and allowing termination
ask_user() {
    echo -n -e "Waiting 60 secs for you to:\n\t hit \033[1m[space]\033[0m or \033[1m[enter]\033[0m to \033[1m$1\033[0m "
    echo -n -e "(default) OR type \033[1many other key\033[0m to \033[1m$2\033[0m OR press \033[1mCtrl+C to exit\033[0m"
    trap 'exit 129' SIGINT
    read -t60 -n1 -rsp $'...\n' key || true
    trap - SIGINT
    [[ -z ${key} ]] && return 0 || return 1
}

# update stage, inform the user allowing intervention and go for a reboot
reboot_nicely() {
    update_stage
    echo -e '\033[1m\033[5mTo complete setup, please rerun this script after reboot.\033[0m'
    ask_user 'reboot now' 'skip rebooting'
    [[ $? -eq 0 ]] && sudo reboot || exit 0
}

# read the last known stage and check it is valid
stage=$(read_stage)
[[ ${stage} =~ '^[0-4]$' ]] || {
    echo "Invalid stage! ${stage}"
    exit 1
}

# Workaround for issue that sometimes crashes Raspbian Menu-bar on reboot
# Fix is to delete the current user lxpanel config and reboot
# Restarting the X session (rebooting) will create a new lxpanel config and the menu bar should be visible again.
[[ ${stage} -gt 0 && ${stage} -lt 3 ]] && {
    ask_user 'continue' 'fix Raspbian Menu-bar not visible and reboot'
    [[ $? -eq 0 ]] || { sudo rm -rf ~/.config/lxpanel; sudo reboot ;}
}
# TODO - remove above workaround when no longer needed

# clone the repository
[[ -d 'AIY-projects-python' ]] || git clone https://github.com/google/aiyprojects-raspbian.git AIY-projects-python

# setup python virtual env in AIY-projects-python
[[ -d 'AIY-projects-python/env' ]] || {
    sudo bash -c """
    yes | apt-get update
    yes | apt-get upgrade
    yes | apt-get install python-virtualenv
    """
    cd AIY-projects-python/
    virtualenv -p python3 env
}

# install dependencies
[[ ${stage} -eq 0 ]] && {
    cd AIY-projects-python/; ource env/bin/activate
    scripts/install-deps.sh
    sudo scripts/install-services.sh
    pip install -e src/
    pip install RPi.GPIO
    sudo scripts/install-alsa-config.sh
    reboot_nicely
}

# configure driver
[[ ${stage} -eq 1 ]] && {
    cd AIY-projects-python/; source env/bin/activate
    python3 checkpoints/check_wifi.py
    sudo scripts/configure-driver.sh
    reboot_nicely
}

# check audio and start demo
[[ ${stage} -eq 2 ]] && {
    cd AIY-projects-python/; source env/bin/activate

    # check audio
    python3 checkpoints/check_audio.py
    ask_user 'confirm speaker and microphone work' 'indicate otherwise'
    [[ $? -eq 0 ]] || exit 1

    # start demo
    if [[ -f ~/assistant.json ]]; then
        python3 src/examples/voice/assistant_library_with_button_demo.py
        update_stage
    else
        cat <<<"""
        To access the cloud services you need to register a project and generate credentials for cloud APIs.
        This is documented in instructions here:
        https://aiyprojects.withgoogle.com/voice#users-guide-1-1--connect-to-google-cloud-platform
        """
        exit 1
    fi
}

# make headless
[[ ${stage} -eq 3 ]] && {
    ask_user 'enable headless start' 'skip'
    [[ $? -eq 0 ]] || exit 0
    [[ -f AIY-projects-python/src/main.py ]] || {
        cp AIY-projects-python/src/examples/voice/assistant_library_with_button_demo.py AIY-projects-python/src/main.py
        echo -n 'copied AIY-projects-python/src/examples/voice/assistant_library_with_button_demo.py '
        echo 'to AIY-projects-python/src/main.py'
    }
    sudo bash -c """
    systemctl enable voice-recognizer
    systemctl start voice-recognizer
    systemctl status voice-recognizer
    """
    echo 'voice-recognizer service will start at boot, using AIY-projects-python/src/main.py'
    update_stage
}
