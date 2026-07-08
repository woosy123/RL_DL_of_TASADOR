#!/bin/sh
mpstat -P ALL 5 3 >> mp.txt &
for i in 1 2 3
do
	vnstat -tr 5 -i ${NET_IFACE} >> vn.txt
done
