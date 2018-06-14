#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  vault/disks.py:
#
from os.path import basename, exists, join
from shlex import split
from subprocess import PIPE, Popen

get_fstype_cmd = u'lsblk -lpf {}'
fstype_crypt = u'crypto_LUKS'
crypt_setup_cmd = u'/sbin/cryptsetup -v --cipher aes-xts-plain64 --key-size 512 --hash sha256'
crypt_setup_cmd += u' --iter-time 2000 -d - luksFormat {}'
crypt_open_cmd = u'/sbin/cryptsetup -d - luksOpen {} {}'


def execute(*args, **kwargs) -> (str, str, int):
    """execute external command in a subprocess and return stdout, stderr, and return code.
    :param args: command line string or list with command as first item and arguments
    :param kwargs: optional keyword arguments
    :parameter input: string to send to process via stdin, default None
    :return: tuple stdout as str, stderr as str, return code as int
    """
    cmd = tuple(arg for arg in split(' '.join(str(arg) for arg in args)))
    std_in = kwargs.get('input')
    cwd = kwargs.get('cwd')
    if std_in:
        std_in = std_in.encode()
    try:
        shell = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd)
        std_out, std_err = shell.communicate(input=std_in)
        rc = shell.returncode
    except OSError as e:
        return '', str(e), -1
    else:
        return std_out, std_err, rc


def open_device(device: str, passphrase: str) -> str:
    """luksOpen an encrypted device and return the path to the (mapped) encrypted disk
    :param device: path to locked disk
    :param passphrase: disk encryption passphrase
    :return: path to open disk
    """

    def fstype_is_crypt_device() -> bool:
        try:
            device_fstype = list(map(lambda d: d.split(), execute(get_fstype_cmd.format(device))[0].splitlines()))[1][1]
        except IndexError:
            return False
        else:
            return device_fstype == fstype_crypt

    device_name = basename(device)
    encrypted_device = join('/dev/mapper', device_name)
    if not fstype_is_crypt_device():
        execute(crypt_setup_cmd.format(device), input=passphrase)
    if not exists(encrypted_device):
        execute(crypt_open_cmd.format(device, device_name), input=passphrase)
    return encrypted_device
