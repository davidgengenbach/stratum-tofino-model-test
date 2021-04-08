import subprocess

from mininet import log
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.topo import Topo

from mininet_test import StratumTofinoModel, NoOffloadHost


def run_cmd(cmd: str, check=True) -> str:
    return subprocess.run(cmd, shell=True, check=check, stdout=subprocess.PIPE).stdout.decode('utf-8')


def cleanup():
    run_cmd('mn --clean', check=False)
    bridges = [x.split(' ')[1].split(':')[0] for x in run_cmd('ip link').splitlines()]
    bridges = [x for x in bridges if x.count('stratumbr') == 1]

    for bridge in bridges:
        run_cmd(f'ip link delete {bridge}')


def main():
    # 'debug'
    # 'info'
    # 'output'
    # 'warning'
    # 'error'
    # 'critical'

    cleanup()
    log.setLogLevel('info')
    topo = CerebroTopo(hosts=2)
    net = Mininet(
        topo=topo,
        switch=StratumTofinoModel,
        host=NoOffloadHost,
        controller=None
    )
    net.start()
    CLI(net)
    net.stop()


class CerebroTopo(Topo):

    def __init__(self, hosts=1, **opts):
        self.num_hosts = hosts
        Topo.__init__(self, **opts)

    def build(self, *args, **params):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        self.addLink(switch1, switch2)

        host1 = self.addHost(f'h1', ip=f"10.0.0.1")
        self.addLink(switch1, host1)

        host2 = self.addHost(f'h2', ip=f"10.0.0.2")
        self.addLink(switch2, host2)


if __name__ == '__main__':
    main()
