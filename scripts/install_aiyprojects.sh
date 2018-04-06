#!/usr/bin/env bash
# script to setup google aiy voice kit on Raspberry Pi 3 B+ running Raspbian

# set-up requires reboot, so we keep track of progress in a flag file
read_stage() { [[ -f ${flag} ]] && head -n 1 ${flag} | tr -d \n || echo -n 0 ;}
update_stage() { echo -n $((${stage}+1)) >${flag} ;}
reboot_nicely() {
  cat <<<"""Going to reboot in 60 seconds.
  Note:
    In case the raspbian menu bar is not visible after reboot, remove lxpanel directory and reboot.
    open a terminal Ctrl+Alt+T or Ctrl+Alt+F1
    rm -rf ~/.config/lxpanel
    sudo reboot
  """
  read -t60 -n1 -rsp $'press any key to reboot immediately or Ctrl+C to exit...\n' response || true
  update_stage
  sudo reboot
}

set -e # terminate script on error
cd # switch to home dir

flag=~/.$(basename $0).done # use dot file in home dir to keep track of stages
stage=$(read_stage) # read the last reached stage

# clone the repositiry
[[ -d 'AIY-projects-python' ]] || git clone https://github.com/google/aiyprojects-raspbian.git AIY-projects-python

cd AIY-projects-python/

# setup python virtual env
[[ -d 'env' ]] || {
  sudo bash -c """
  yes | apt-get update
  yes | apt-get upgrade
  yes | apt-get install python-virtualenv
  """
  virtualenv -p python3 env
}

# switch to virtual env
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

# check audio
[[ ${stage} -lt 3 ]] && {
  python3 checkpoints/check_audio.py
  update_stage
 }

# start demo
[[ $(read_stage) -lt 4 ]] && {
  if [[ -f ~/assistant.json ]]; then
    python3 src/examples/voice/assistant_library_with_button_demo.py
    update_stage
  else
    cat <<<"""
    To access the cloud services you need to register a project and generate credentials for cloud APIs.
    This is documented in instructions here:
    https://aiyprojects.withgoogle.com/voice#users-guide-1-1--connect-to-google-cloud-platform
    """
    exit 0
  fi
}

# make headless
[[ $(read_stage) -lt 5 ]] && {
  read -n1 -rsp $'Press spacebar or enter to enable headless start, any other key to skip or Ctrl+C to exit...\n' key
  [[ -z ${key} ]] && {
    cp src/examples/voice/assistant_library_with_button_demo.py src/main.py
    sudo bash -c """
    systemctl enable voice-recognizer
    systemctl start voice-recognizer
    systemctl status voice-recognizer
    """
    update_stage
  }
}
