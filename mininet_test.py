#!/usr/bin/env python3

import subprocess

from mininet.node import Switch, Host


# sudo $(which mn) --custom mininet_test.py --switch stratum-tofino-model --host no-offload-host --controller none

class StratumTofinoModel(Switch):
    INSTANCE_INDEX = 0

    def __init__(self, name: str, instance_index=None, inNamespace=False, **kwargs):
        if instance_index is None:
            self.instance_index = StratumTofinoModel.INSTANCE_INDEX
            StratumTofinoModel.INSTANCE_INDEX += 1
        else:
            self.instance_index = instance_index
        Switch.__init__(self, name, inNamespace=inNamespace, **kwargs)

    def start(self, controllers):
        port = 0
        for intf in sorted(self.intfNames()):
            if intf == 'lo':
                continue
            bridge = f'stratumbr{self.instance_index}{port}'
            stratum_intf = f'stratumveth{self.instance_index}{port}0'
            for cmd in [
                f'ip link delete {bridge}',
                f'ip link add name {bridge} type bridge',
                f'ip link set {stratum_intf} master {bridge}',
                f'ip link set {intf} master {bridge}',
                f'ip link set {bridge} up'
            ]:
                # cmd = f'ip link set stratumveth{self.instance_index}{port}0 alias {intf}'
                print(cmd)
                subprocess.run(
                    cmd,
                    shell=True,
                    check=False
                )
            port += 1


class NoOffloadHost(Host):
    def __init__(self, name, inNamespace=True, **params):
        Host.__init__(self, name, inNamespace=inNamespace, **params)

    def config(self, **params):
        r = super(Host, self).config(**params)
        for off in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" \
                  % (self.defaultIntf(), off)
            self.cmd(cmd)
        return r


# Exports for bin/mn
switches = {'stratum-tofino-model': StratumTofinoModel}

hosts = {'no-offload-host': NoOffloadHost}
