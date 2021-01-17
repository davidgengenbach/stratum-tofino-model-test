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
        last_switch = None
        for i in range(self.num_hosts):
            host_index = str(i + 1)
            host = self.addHost('h' + host_index, ip="10.0.0." + host_index, cls=NoOffloadHost)
            worker_switch = self.addSwitch('s' + host_index)
            self.addLink(host, worker_switch, autoconf=True)
            if last_switch is not None:
                self.addLink(worker_switch, last_switch, autoconf=True)
            last_switch = worker_switch


if __name__ == '__main__':
    main()
