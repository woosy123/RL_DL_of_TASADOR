#!/bin/bash

vnstat -i ${NET_IFACE} -tr 10 | awk '/tx/' | awk '{print $2, $4}' > net_pps.txt

