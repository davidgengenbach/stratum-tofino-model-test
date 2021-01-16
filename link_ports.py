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

    instances = running_stratum_tofino_models(args.docker_compose_service_name)
    for idx, instance in enumerate(instances):
        link_docker_namespace(instance)
        assert namespace_exists(instance)
        # TODO: the number of ports could be inferred by looking at the number of veths in the container namespace (before creating veths ourselves, of course)
        for port in range(0, args.ports_per_tofino_model):
            link_tofino_model_port(instance, idx, port)


def get_namespaces() -> typing.List[str]:
    return run_cmd(['ls', '/var/run/netns']).splitlines()


def namespace_exists(name: str) -> bool:
    return name in get_namespaces()


def link_docker_namespace(name: str):
    pid = run_cmd(['docker', 'inspect', name, '-f', "'{{.State.Pid}}'"]).strip()[1:-1]
    run_cmd(['rm', '-rf', f'/var/run/netns/{name}'])
    run_cmd(['ln', '-s', f'/proc/{pid}/ns/net', f'/var/run/netns/{name}'])


def activate_interface(*, interface: str, namespace: typing.Optional[str] = None):
    run_cmd(namespace_cmd(['ip', 'link', 'set', interface, 'up'], namespace=namespace))


def move_interface_to_netns(*, interface: str, namespace: str):
    run_cmd(['ip', 'link', 'set', interface, 'netns', namespace])


def create_bridge(*, name: str, namespace: str):
    run_cmd(namespace_cmd(['ip', 'link', 'add', 'name', name, 'type', 'bridge'], namespace=namespace))


def add_interface_to_bridge(*, interface: str, bridge: str, namespace: str):
    run_cmd(namespace_cmd(['ip', 'link', 'set', interface, 'master', bridge], namespace=namespace))


def create_veth(*, veth0: str, veth1: str):
    run_cmd(['ip', 'link', 'add', veth0, 'type', 'veth', 'peer', 'name', veth1])


def link_tofino_model_port(instance: str, model_index: int, port: int):
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

    create_veth(veth0=veth0, veth1=veth1)
    activate_interface(interface=veth0)
    move_interface_to_netns(interface=veth1, namespace=instance)
    # Important: activate AFTER moving into namespace
    activate_interface(interface=veth1, namespace=instance)

    # Create bridge to connect port veth with our veth1
    create_bridge(name=bridge, namespace=instance)
    add_interface_to_bridge(interface=veth1, bridge=bridge, namespace=instance)
    add_interface_to_bridge(interface=port_interface, bridge=bridge, namespace=instance)
    # Do not forget to activate bridge!
    activate_interface(interface=bridge, namespace=instance)


def running_stratum_tofino_models(needle: str) -> typing.List[str]:
    # TODO: is there machine-readable output?
    out = [x.split(' ')[0] for x in run_cmd(['docker-compose', 'ps']).splitlines()
           if x.count(needle) > 0 and x.count('Exit') == 0 and x.count('Up') > 0]
    return list(sorted(out))


def run_cmd(cmd: typing.List[str], check=True) -> str:
    print('Executing:', ' '.join(cmd))
    return subprocess.run(cmd, stdout=subprocess.PIPE, check=check).stdout.decode('utf-8')


def namespace_cmd(cmd: typing.List[str], namespace: typing.Optional[str] = None) -> typing.List[str]:
    if namespace:
        cmd = ['ip', 'netns', 'exec', namespace] + cmd
    return cmd


if __name__ == '__main__':
    main()
