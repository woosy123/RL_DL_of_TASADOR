#!/bin/sh
M=$1
for i in $(seq 1 4)
do
	S=`expr $i \* 200`
	grep rx vn_"$M"_"$S".txt | awk '{ print $2 }' > "$S".txt
#	grep "Average:     all" mp_"$M"_"$S".txt | awk '{ print $3,$5,$8,$10 }'
#	grep "Average:    64055      5657" pid_"$M"_"$S".txt | awk '{ print $8 }' > "$S".txt
#	grep "Average:        0      5664" pid_"$M"_"$S".txt | awk '{ print $8 }' > "$S".txt
done
paste 200.txt 400.txt 600.txt 800.txt
rm 200.txt 400.txt 600.txt 800.txt
