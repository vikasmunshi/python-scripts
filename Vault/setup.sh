#!/usr/bin/env bash

yum install -y rh-python36-python-devel.x86_64
echo "export PATH=${PATH}:/opt/rh/rh-python36/root/bin/" >/etc/profile.d/rh-python36.sh
export PATH=${PATH}:/opt/rh/rh-python36/root/bin/
pip3 --upgrade pip

yum install -y git.x86_64

/usr/local/bin
pip3 install -e Vault