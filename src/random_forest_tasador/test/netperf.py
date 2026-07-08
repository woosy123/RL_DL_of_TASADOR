import csv
import os
import numpy as np
import pandas as pd

dataset = pd.read_csv('./m2_test.csv', names=['quota', 'size', 'goal', 'vm'])
q = np.array(dataset['quota'])
s = np.array(dataset['size'])
g = np.array(dataset['goal'])
time = 155
cpu = 1
for i in range(0, 4):
    # Apply quota to vhost
    quota = int(q[i])
    msg = int(s[i])
    goal = int(g[i])
#    print(quota, msg)
    os.system("sudo ./set_quota.sh %s" %quota)
    # Execute netperf and record the result
    cmd = '"/home/v1/test.sh {} {}" &'.format(time, msg)
    os.system("sudo ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" ${VM_USER}@${VM_HOST} " +cmd)
    for j in range(0, 5):
        os.system("sudo vnstat -i ${NET_IFACE} -tr 30 >> vn_{}_{}.txt &".format(msg, goal))
        os.system("sudo pidstat -I -p 44118,44125 30 1 >> pid_{}_{}.txt &".format(msg, goal))
        os.system("sudo mpstat 30 1 >> mp_{}_{}.txt".format(msg, goal))
    os.system("sleep 10")

