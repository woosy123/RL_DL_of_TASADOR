#!/bin/bash
python3 generate_modelG_any.py > modelG.txt
cat modelG.txt | grep CV | awk {'print $9'} > G_time.txt
python3 sum_time_G.py

python3 generate_modelH_any.py > modelH.txt
cat modelH.txt | grep CV | awk {'print $9'} > H_time.txt
python3 sum_time_H.py

