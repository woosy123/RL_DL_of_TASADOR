import csv
import os
import time as t
import numpy as np
import pandas as pd

dataset = pd.read_csv(f'./predict/train_1vcpu_1000_1200_output_cuda.csv', names=['network_SLO', 'message_size', 'cpu_quota'])
q = np.array(dataset['cpu_quota'])
s = np.array(dataset['message_size'])
time = 30
cpu = 1

for i in range(1,q.size):
#    print(q[i])
#   print(s[i])
    # Apply quota to vhost
    quota = int(q[i])
    if quota <1000:
        continue
    msg = int(s[i])
    os.system(f"sudo ./set_cpu.sh {quota}")

    # Execute netperf and record the result
    os.system(f"./netperf.sh {cpu} {time} {msg}")
        
    os.system(f"./get_vnstat.sh {quota}")
        
