import subprocess
import sys
import time
import os

class script:
    def __init__(self):
        self.observation_space_dim = 4
        self.action_space_dim = 2
        self.action_step = 1
        self.current_state = None

    def start_netperf(self):
        subprocess.run(['ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} "netperf -H ${VM_OR_TARGET_HOST} -l 10000 -- -m 64 &"'], shell=True)
    
    def stop_netperf(self):
        subprocess.run(['ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} "sudo pkill netperf"'], shell=True)
        return
    
    def reset_state(self):
        with open('set_cpu.txt','w') as f:
            f.write(str(20000))
        time.sleep(1)
        return

    def get_net_pps(self):
        time.sleep(0.3)
        if os.path.getsize("../get_net.txt") != 0:
            with open("../get_net.txt", "r") as file:
                lines = file.readlines()

            # Initialize lists to store the values in each column
            column1 = []
            column2 = []

            # Process each line and store the values
            for line in lines:
                values = line.strip().split(" ")
                column1.append(values[0])
                column2.append(values[1])

            pps = abs(int(column1[1]) - int(column1[0]))
            net = abs(int(column2[1]) - int(column2[0])) / 1 * 8 / 1000000 
        else :
            net = 60
            pps = 3000
        return float(net),int(pps)


    def get_cpu_usage(self0):
        if os.path.getsize("../get_cpu.txt") != 0:
            with open('../get_cpu.txt','r') as f:
   
                cpu1 = f.readline().rstrip()
                cpu2 = f.readline().rstrip()
        else: 
            cpu1, cpu2 = 5, 5
        cpu = float(cpu1) + float(cpu2)
        return cpu


