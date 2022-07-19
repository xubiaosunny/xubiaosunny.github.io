#!/bin/bash

ipaddr=$(ip addr | grep eth0 | grep 'inet ' | awk '{print $2}' |awk -F/ '{print $1}')
# echo "$ipaddr" > wsl2_ip.txt
echo $ipaddr
