#!/usr/bin/env bash

set -eux

# To check: the number of hugepages per switch is 128?
sysctl -w vm.nr_hugepages=1024
mkdir /mnt/huge || true
mount -t hugetlbfs nodev /mnt/huge || true

# The veths will be created WITHIN the Docker container - not the host system (because of bridged- instead of host-network)
veth_setup.sh
tofino-model --p4-target-config /usr/share/stratum/tofino_skip_p4.conf $@ &
start-stratum.sh  -bf_sim -bf_switchd_background=false -enable_onlp=false