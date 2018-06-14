#!/usr/bin/env bash

this_dir=$(readlink -f $(dirname $0))

for custodian in custodian0{1..5}; do
    key_file=${this_dir}/custodian_keys/${custodian}.key
    scp root@bmaas002.northeurope.cloudapp.azure.com:/usr/local/bin/Vault/cache/${custodian}* ${this_dir}/cache/.
    python3 -m vault client ${key_file}
    scp ${this_dir}/cache/vault* root@bmaas002.northeurope.cloudapp.azure.com:/usr/local/bin/Vault/cache/.
done