from mininet import log
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.topo import Topo

from mininet_test import StratumTofinoModel, NoOffloadHost


def main():
    # 'debug'
    # 'info'
    # 'output'
    # 'warning'
    # 'error'
    # 'critical'
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
        host1 = self.addHost(f'h1', ip=f"10.0.0.1")
        host2 = self.addHost(f'h2', ip=f"10.0.0.2")
        self.addLink(switch1, host1)
        self.addLink(switch1, host2)

        host3 = self.addHost(f'h3', ip=f"10.0.0.3")
        switch2 = self.addSwitch('s2')
        self.addLink(switch2, host3)

        self.addLink(switch1, switch2)


if __name__ == '__main__':
    main()
