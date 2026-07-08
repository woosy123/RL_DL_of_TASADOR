#!/bin/sh
for M in 64 1024
do
	for i in 100 200 400 800
	do
		sudo ./default.sh $M $i
	done
done
