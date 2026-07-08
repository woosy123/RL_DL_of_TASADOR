#!/bin/bash
while true
do
	pidstat -G python3 | grep python3 | awk '{print $9}' >> $1_cpu_usage.txt
	sleep 3
done
