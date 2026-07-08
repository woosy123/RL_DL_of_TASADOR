#!/bin/bash

output_file="throughput_750_tasador.csv"

echo "Time(sec),Throughput,PPS" > $output_file

for time in $(seq 0 30 3000)
do
  ./vnstat.sh
  
  if [ -f "net_pps.txt" ]; then
    last_line=$(tail -n 1 net_pps.txt)
    throughput=$(echo $last_line | awk '{print $1}') 
    pps=$(echo $last_line | awk '{print $2}')         

    echo "$time,$throughput,$pps" >> $output_file

    echo "Time $time seconds: Throughput = $throughput, PPS = $pps"
  else
    echo "no file"
  fi
  sleep 20
done
