#!/bin/bash
quota=$1
network=$(vnstat -i ${NET_IFACE} -tr 25 | awk '/tx/' | awk '{print $2}')
echo $quota $network >> ./predict/result.txt
sleep 10

