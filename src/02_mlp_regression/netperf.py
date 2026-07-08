import csv
import os
import numpy as np
import pandas as pd

for g in 1, 8:
    dataset = pd.read_csv(f'./predict/m2_train_{g}vcpu_1000__1200_output.csv', names=['network_SLO', 'Message_size', 'cpu_quota'])
    q = np.array(dataset['cpu_quota'])
    print(q.size)
    s = np.array(dataset['Message_size'])
    time = 10
    cpu = 8
    for i in range(1,q.size+1):
    #    print(q[i])
    #   print(s[i])
        # Apply quota to vhost
        quota = int(q[i])
        if quota <1000:
            continue
        msg = int(s[i])
        os.system(f"sudo ./set_cpu.sh {quota}")
        os.system("sleep 2")
        # Execute netperf and record the result
        os.system(f"./netperf.sh {cpu} {time} {msg}")

        os.system(f"echo \"{quota}\" >> ./predict/{g}_SLO.txt")
        os.system("vnstat -i ${NET_IFACE} -tr 5 >> ./predict/{}_SLO.txt ".format(g,'SLO'))

        os.system("sleep 5")
