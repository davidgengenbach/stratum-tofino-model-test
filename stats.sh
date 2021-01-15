#!/usr/bin/env bash

set -eux 

sudo docker stats --no-stream
sudo docker ps
nmap localhost -p28000-28010