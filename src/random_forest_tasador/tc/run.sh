#!/bin/sh
for M in 64
do
	for i in 200 400 600 800
	do
		sudo ./default.sh $M $i
	done
done
