#!/bin/sh
H="${VM_OR_TARGET_HOST}"
for i in 1 2 3 4
do
	netperf -H $H -p $i -l 30 &
done
