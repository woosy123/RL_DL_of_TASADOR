import subprocess
import sys
import time
import os
import random
class script:
    def __init__(self):
        self.observation_space_dim = 4
        self.action_space_dim = 3
        self.action_step = 1


    def start_netperf(self):
        subprocess.run(['ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} "netperf -H ${VM_OR_TARGET_HOST} -l 6000 -- -m $M"'], shell=True)
    
    def stop_netperf(self):
        subprocess.run(['ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} "sudo pkill netperf"'], shell=True)
        return
    
    def reset_state(self):
        with open('set_cpu.txt','w') as f:
            f.write(str(20000))
        time.sleep(1.5)
        return
        
        
    def get_net_pps(self):
        subprocess.run(['../np_get.sh'],shell=True)
        with open('get_net.txt','r') as f:
            net, pps = (f.read()).split()
        return float(net),int(pps)

    def get_cpu_usage(self):
        if os.path.getsize("../get_cpu.txt") != 0:
            with open('../get_cpu.txt','r') as f:
                cpu1 = f.readline().rstrip()
                cpu2 = f.readline().rstrip()
        else:
            cpu1, cpu2 = random.randint(5,15), random.randint(5,15)
        cpu = float(cpu1) + float(cpu2)
        return cpu
