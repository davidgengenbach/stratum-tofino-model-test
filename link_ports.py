#!/usr/bin/env python3

import subprocess
import typing

# TODO: use pyroute2 (https://pypi.org/project/pyroute2/) for some of this?

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Stratum and tofino-model: link ports')
    parser.add_argument(
        '--docker_compose_service_name',
        type=str,
        default='tofino_model'
    )
    parser.add_argument(
        '--ports_per_tofino_model',
        type=int,
        default=64
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    instances = running_stratum_tofino_models()
    for idx, instance in enumerate(instances):
        link_docker_namespace(instance)
        assert namespace_exists(instance)
        for port in range(0, args.ports_per_tofino_model):
            link_tofino_model_port(instance, idx, port)


def get_namespaces() -> typing.List[str]:
    return [x for x in run_cmd(['ls', '/var/run/netns']).splitlines()]


def namespace_exists(name: str) -> bool:
    return len([x for x in get_namespaces() if x == name]) == 1


def link_docker_namespace(name: str):
    pid = run_cmd(['docker', 'inspect', name, '-f', "'{{.State.Pid}}'"]).strip()[1:-1]
    run_cmd(['rm', '-rf', f'/var/run/netns/{name}'])
    run_cmd(['ln', '-s', f'/proc/{pid}/ns/net', f'/var/run/netns/{name}'])


def activate_interface(interface: str, namespace: typing.Optional[str] = None):
    run_cmd(namespace_cmd(['ip', 'link', 'set', interface, 'up'], namespace=namespace))


def move_interface_to_netns(interface: str, namespace: str):
    run_cmd(['ip', 'link', 'set', interface, 'netns', namespace])


def create_bridge(name: str, namespace: str):
    run_cmd(namespace_cmd(['ip', 'link', 'add', 'name', name, 'type', 'bridge'], namespace=namespace))


def add_interface_to_bridge(interface: str, bridge: str, namespace: typing.Optional[str] = None):
    run_cmd(namespace_cmd(['ip', 'link', 'set', interface, 'master', bridge], namespace=namespace))


def create_veth(veth0, veth1):
    run_cmd(['ip', 'link', 'add', veth0, 'type', 'veth', 'peer', 'name', veth1])


def link_tofino_model_port(instance, model_index, port):
    # veth names are "stratumvethXYZ" where
    # X = model index,
    # Y = port, and
    # Z = veth index (0 or 1)
    veth_prefix = f'stratumveth{model_index}{port}'
    # The host veth
    veth0 = veth_prefix + '0'
    # The container veth
    veth1 = veth_prefix + '1'
    # This bridge is created INSIDE the container network namespace
    bridge = f'stratumbridge{port}'
    # The port veth interface name by tofino-model (inside container)
    port_interface = f'veth{port}'

    create_veth(veth0, veth1)
    activate_interface(veth0)
    move_interface_to_netns(veth1, instance)
    # Important: activate AFTER moving into namespace
    activate_interface(veth1, instance)

    # Create bridge to connect port veth with our veth1
    create_bridge(bridge, instance)
    add_interface_to_bridge(veth1, bridge, namespace=instance)
    add_interface_to_bridge(port_interface, bridge, namespace=instance)
    # Do not forget to activate bridge!
    activate_interface(bridge, instance)


def running_stratum_tofino_models(needle='tofino_model') -> typing.List[str]:
    out = [x.split(' ')[0] for x in run_cmd(['docker-compose', 'ps']).splitlines() if
           x.count(needle) > 0 and x.count('Exit') == 0]
    return list(sorted(out))


def run_cmd(cmd: typing.List[str], check=True) -> str:
    print(' '.join(cmd))
    return subprocess.run(cmd, stdout=subprocess.PIPE, check=check).stdout.decode('utf-8')


def namespace_cmd(cmd: typing.List[str], namespace: typing.Optional[str] = None) -> typing.List[str]:
    if namespace:
        cmd = ['ip', 'netns', 'exec', namespace] + cmd
    return cmd


def interfaces(namespace: typing.Optional[str] = None) -> typing.List[str]:
    return [x.strip() for x in run_cmd(namespace_cmd(['ip', 'link'], namespace=namespace)).splitlines()]


if __name__ == '__main__':
    main()
