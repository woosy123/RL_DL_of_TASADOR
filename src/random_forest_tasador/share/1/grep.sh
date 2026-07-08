#!/bin/sh
M=1024
echo "Network throughput"
for i in 1024 2048 4096 8192
do
	rm f1.txt f2.txt f3.txt
	echo "$i"
	grep rx vn_"$M"_"$i".txt | awk '{ print $2 }' >> f1.txt
	grep "Average:    64055   1836267" pid_"$M"_"$i".txt | awk '{ print $8 }' >> f2.txt
	grep "Average:        0   1836274" pid_"$M"_"$i".txt | awk '{ print $8 }' >> f3.txt
	paste f1.txt f2.txt f3.txt
done
sudo rm f1.txt f2.txt f3.txt
