#!/usr/bin/env bash

set -eux

sysctl -w vm.nr_hugepages=1024
mkdir /mnt/huge || true
mount -t hugetlbfs nodev /mnt/huge || true

veth_setup.sh 
tofino-model --p4-target-config /usr/share/stratum/tofino_skip_p4.conf $@ &

start-stratum.sh  -bf_sim -bf_switchd_background=false -enable_onlp=false