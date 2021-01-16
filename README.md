# Multiple tofino-model + Stratum instances 

**Work-in-progress!**

## Instructions

```
sudo docker-compose -f docker-compose.yaml rm
sudo docker-compose -f docker-compose.yaml up --force-recreate --abort-on-container-exit
```

## Linking tofino-model veth ports to host

This is only a rough sketch on how to achive it:
1) Create `n` tofino-model + Stratum instances
1) Create the veth pair (`stratumveth0_0` , `stratumveth0_1`) for every tofino-model port for the n  instances.
1) Leave `stratumveth0_0` in the "root" namespace in the host system, the other one `stratumveth0_1` in the Docker container network namespace
1) Bridge the `stratumveth0_1` inside container to `veth0` (= the first port of tofino-model)

Now, the `stratumveth0_0` in the root namespace is connected with `veth0` inside the first tofino-model container!

```
sudo docker ps

# Strangely enough, the network namespaces for Docker are not "linked" by default, meaning they can not be seen with ipnetns list
sudo ip netns list

# For each container, find the PID and link the network namespace so that the "ip" suite can find them
sudo docker inspect stratum-tofino-model-test_tofino_model_1 -f '{{.State.Pid}}'
# 1701 is the PID returned by the last command
sudo ln -s /proc/1701/ns/net /var/run/netns/stratum-tofino-model-test_tofino_model_1

# From now on, a "stratum-tofino-model-test_tofino_model_1" namespace should be present
sudo ip netns list

# Define veth from host => Stratum-tofino-model container
sudo ip link add stratumtofino0_1 type veth peer name stratumtofino0_2
sudo ip link set stratumtofino0_1 up

# Move second veth to container network namespace and activate
sudo ip link set stratumtofino0_2 netns stratum-tofino-model-test_tofino_model_1
sudo ip netns exec stratum-tofino-model-test_tofino_model_1 ip link set stratumtofino0_2 up

# Create a bridge inside container to bridge veth0 (= tofino-model port 0) to stratumtofino0_2 veth
sudo ip netns exec stratum-tofino-model-test_tofino_model_1 ip link add name veth0bridge type bridge
sudo ip netns exec stratum-tofino-model-test_tofino_model_1 ip link set stratumtofino0_2 master veth0bridge
sudo ip netns exec stratum-tofino-model-test_tofino_model_1 ip link set veth0 master veth0bridge
sudo ip netns exec stratum-tofino-model-test_tofino_model_1 ip link set veth0bridge up
```

Voilá, the first port of the tofino-model switch is linked from within the Docker container into a host "root" namespace veth named `stratumtofino0_1`.

[This](https://dev.to/polarbit/how-docker-container-networking-works-mimic-it-using-linux-network-namespaces-9mj) is a very nice explanation/guide-through of network namespaces, especially for Docker.
