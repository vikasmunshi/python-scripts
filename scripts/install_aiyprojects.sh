#!/usr/bin/env bash
########################################################################################################################
#    Script to setup google aiy voice kit on Raspberry Pi 3 B+ running Raspbian
#    Based partly on instructions at https://github.com/google/aiyprojects-raspbian/blob/aiyprojects/HACKING.md
#    Author: Vikas Munshi <vikas.munshi@gmail.com>
#    Version 1.0: 2018.04.06
########################################################################################################################
#    MIT License
#
#    Copyright (c) 2018 Vikas Munshi
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
########################################################################################################################

# involves reboot, so we keep track of progress in a flag file managed using: read_stage, update_stage, reboot_nicely

# read last known stage from flag file, default 0
read_stage() { [[ -f ${flag} ]] && head -n 1 ${flag} | tr -d \n || echo -n 0 ;}

# add one to current stage and write to flag file
update_stage() { stage=$((${stage}+1)); echo -n ${stage} >${flag} ;}

# update stage, inform the user allowing intervention and go for a reboot
reboot_nicely() {
    update_stage
    read -t60 -n1 -rsp $'Going to reboot in 60 seconds, press any key to reboot now or Ctrl+C to exit...\n' _ || true
    sudo reboot
}

# terminate script on error; switch to home dir, rest of the script uses relative paths
set -e
cd

# use dot file in home dir as flag file to keep track of stages and read the last known stage
flag=~/.$(basename $0).done
stage=$(read_stage)

# Workaround for issue that sometimes crashes Raspbian Menu-bar on reboot
# Fix is to delete the current user lxpanel config and reboot
# Restarting the X session (rebooting) will create a new lxpanel config file and the menu bar should be visible again.
[[ ${stage} -gt 0 && ${stage} -lt 3 ]] && {
    echo 'Press any key to fix Raspbian Menu-bar not visible, space-bar or enter to skip or Ctrl+C to exit...'
    echo "fix will delete ~/.config/lxpanel and reboot"
    read -t60 -n1 -rs fix || true
    [[ -z ${fix} ]] || {
        sudo rm -rf ~/.config/lxpanel
        sudo reboot
    }
}
# TODO - remove above workaround when no longer needed

# clone the repository
[[ -d 'AIY-projects-python' ]] || git clone https://github.com/google/aiyprojects-raspbian.git AIY-projects-python

# switch dir, rest of the script uses relative paths to AIY-projects-python
cd AIY-projects-python/

# setup python virtual env in AIY-projects-python
[[ -d 'env' ]] || {
    sudo bash -c """
    yes | apt-get update
    yes | apt-get upgrade
    yes | apt-get install python-virtualenv
    """
    virtualenv -p python3 env
}

# activate virtual env, rest of the script uses python virtualenv
source env/bin/activate

# install dependencies
[[ ${stage} -lt 1 ]] && {
    scripts/install-deps.sh
    sudo scripts/install-services.sh
    pip install -e src/
    pip install RPi.GPIO
    sudo scripts/install-alsa-config.sh
    reboot_nicely
}

# configure driver
[[ ${stage} -lt 2 ]] && {
    python3 checkpoints/check_wifi.py
    sudo scripts/configure-driver.sh
    reboot_nicely
}

# check audio and start demo
[[ ${stage} -lt 3 ]] && {
    # check audio
    python3 checkpoints/check_audio.py
    echo 'Press space-bar or enter to confirm speaker and microphone work, any other key otherwise or Ctrl+C to exit...'
    read -t60 -n1 -rs confirm_check_audio || true
    [[ -z ${confirm_check_audio} ]] || exit 1

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
[[ ${stage} -lt 4 ]] && {
  read -n1 -rsp $'Press space-bar or enter to enable headless start, any other key to skip or Ctrl+C to exit...\n' key
  [[ -z ${key} ]] && {
    [[ -f src/main.py ]] || {
        echo "will setup assistant_library_with_button_demo for headless start"
        cp src/examples/voice/assistant_library_with_button_demo.py src/main.py
    }
    sudo bash -c """
    systemctl enable voice-recognizer
    systemctl start voice-recognizer
    systemctl status voice-recognizer
    """
    update_stage
  }
}
