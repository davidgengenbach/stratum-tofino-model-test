# Multiple tofino-model + Stratum instances 

**Work-in-progress!**

## Instructions

```
sudo docker-compose rm
sudo docker-compose up --force-recreate --abort-on-container-exit
```

## Linking tofino-model veth ports to host

This is only a rough sketch on how to achive it:
1) Create `n` tofino-model + Stratum instances
1) Create the veth pair (`stratumveth000` , `stratumveth001`) for every tofino-model port for the `n` instances.
1) Leave `stratumveth000` in the "root" namespace in the host system, the other one `stratumveth001` in the Docker container network namespace
1) Bridge the `stratumveth001` inside container to `veth0` (= the first port of tofino-model)

Now, the `stratumveth000` in the root namespace is connected with `veth0` inside the first tofino-model container!

```
sudo ./link_ports.py
```

Voilá, the first port of the tofino-model switch is linked from within the Docker container into a host "root" namespace veth named `stratumveth000`.

The `stratumvethXXX` interfaces are deleted after you stop the Docker containers.

[This](https://dev.to/polarbit/how-docker-container-networking-works-mimic-it-using-linux-network-namespaces-9mj) is a very nice explanation/guide-through of network namespaces, especially for Docker.
