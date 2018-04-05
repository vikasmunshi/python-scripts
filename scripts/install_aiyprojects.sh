#!/usr/bin/env bash
# script to setup google aiy voice kit on Raspberry Pi 3 B+ running Raspbian

cd

# clone the repositiry  
[[ -d 'AIY-projects-python' ]] || git clone https://github.com/google/aiyprojects-raspbian.git AIY-projects-python

# setup python virtual env
[[ -d 'env' ]] || {
  sudo apt-get install python-virtualenv
  virtualenv -p python3 env
}

# switch to virtual env
source env/bin/activate
cd AIY-projects-python/

# install dependencies
[[ -f 'install.done' ]] || {
  scripts/install-deps.sh
  sudo scripts/install-services.sh
  pip install -e src/
  pip install RPi.GPIO
  sudo scripts/install-alsa-config.sh
  touch install.done
  echo 'going for a reboot now, please rerun this script after reboot'
  reboot
}

# configure driver
[[ -f 'configure.done' ]] || {
  python3 checkpoints/check_wifi.py
  sudo scripts/configure-driver.sh
  touch configure.done
  echo 'going for a reboot now, please rerun this script after reboot'
  reboot
}

# check audio
[[ -f 'check.done' ]] || {
  python3 checkpoints/check_audio.py
  touch check.done
 }
# start demo
python3 src/examples/voice/assistant_library_with_button_demo.py
