#!/bin/bash
M=$1
S=$2
VM=`pgrep qemu`
VHOST=`pgrep vhost`
PERF=`expr $S \* 1024`

#sudo tcset virbr0 --rate "$S"Mbps --src-network ${VM_OR_TARGET_HOST}/32 --direction incoming
sudo ${EXPERIMENT_ROOT} -a virbr0 -d $PERF
for i in $(seq 1 5)
do
	sudo ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o stricthostkeychecking=no ${VM_USER}@${VM_HOST} "/home/v1/test.sh 8 $M" &
	vnstat -i ${NET_IFACE} -tr 5 >> vn_"$M"_"$S".txt &
	mpstat 5 1 >> mp_"$M"_"$S".txt &
	pidstat -p $VM,$VHOST -I 5 1 >> pid_"$M"_"$S".txt
	sleep 5
done
#sudo tcdel virbr0 --all
sudo ${EXPERIMENT_ROOT} -c -a virbr0
