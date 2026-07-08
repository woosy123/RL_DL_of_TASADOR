#!/bin/bash
while true :
do
	set=$(cat set_cpu.txt)
	echo $set
	echo "$set 100000" > ${CPU_CGROUP_PATH}
	sleep 1
done
