#!/bin/bash
VM=`pgrep qemu`
VHOST=`pgrep vhost`
DIR="${EXPERIMENT_ROOT}"
for k in 64 128 256 512 1024
do
	sudo ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" ${VM_USER}@${VM_HOST} "/home/v1/test.sh 330 $k" &
	VN="vn_$k"
	PID="pid_$k"
	for i in $(seq 1 9)
	do
		QUOTA=`expr $i \* 1000`
		echo "vhost quota = $QUOTA" >> $DIR/$VN.txt
		echo "vhost quota = $QUOTA" >> $DIR/$PID.txt
		sudo ./set_quota.sh $QUOTA
		sleep 5
		for j in 1 2 3
		do
			vnstat -i ${NET_IFACE} -tr 10 >> $DIR/$VN.txt &
			pidstat -p $VM,$VHOST -I 10 1 >> $DIR/$PID.txt
		done
	done
done
