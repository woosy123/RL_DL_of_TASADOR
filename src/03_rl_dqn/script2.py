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
        self.pid = self.get_pid()


    def start_netperf(self):
        subprocess.run(['ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} "netperf -H ${VM_OR_TARGET_HOST} -l 6000 -- -m $M"'], shell=True)
    
    def stop_netperf(self):
        subprocess.run(['ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} "sudo pkill netperf"'], shell=True)
        return
    
    def reset_state(self):
        with open('set_cpu.txt','w') as f:
            f.write(str(100000))        
        time.sleep(1)
        return 100000
    
    def get_pid(self):
        with open('../pid.txt') as f:
            pid = f.read()
        return int(pid)
    
    def get_net_pps(self):
        subprocess.run([f'parallel ::: ../np_get.sh \'../cpu_get.sh {self.pid}\''],shell=True)

        while os.path.getsize("get_net.txt") == 0:
            subprocess.run(['../np_get.sh'],shell=True)
        with open('get_net.txt','r') as f:
            bps, net, pps = (f.read()).split()
        if bps == 'Gbit/s':
            net = float(net)*1000    
        return float(net),int(pps)

    def get_cpu_usage(self):
        with open('get_cpu.txt','r') as f:
            cpu = f.read()
        return float(cpu)
