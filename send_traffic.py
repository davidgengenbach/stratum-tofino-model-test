#!/usr/bin/env python3

import logging

from scapy.layers.inet import TCP, IP
from scapy.layers.l2 import Ether, ARP
from scapy.sendrecv import sendp


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--interface",
        default="h1-eth0",
        required=True
    )

    args = parser.parse_args()

    logger = logging.getLogger('generate_traffic.py')
    logger.setLevel(logging.DEBUG)
    logger.info('Arguments', args)
    try:
        packet = Ether()/ARP(hwsrc="00:00:00:00:00", pdst="10.0.0.2")
        sendp(packet, iface=args.interface, loop=1, inter=0.1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
