#!/bin/bash
VM=`pgrep qemu`
VHOST=`pgrep vhost`
Q=$1
sudo ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" ${VM_USER}@${VM_HOST} "${VM_WORKLOAD_SCRIPT:-~/test.sh} 160 64" &
VN="vn_$Q"
PID="pid_$Q"

sudo ./set_quota.sh $Q
sleep 5
for i in $(seq 1 5)
do
	vnstat -i ${NET_IFACE} -tr 10 >> $VN.txt &
	pidstat -p $VM,$VHOST -I 10 1 >> $PID.txt
done
