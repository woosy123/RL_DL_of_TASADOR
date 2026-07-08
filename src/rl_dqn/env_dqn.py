import pandas as pd
import time
import subprocess
from script2 import script
#from script8vcpu import script
NUM_EPISODES = 600
MESSAGE_SIZE = 64
NETWORK = 900

class Environment:
    def __init__(self):
        # Define your environment properties here
        # For example, observation space, action space, etc.
        self.observation_space_dim = 5
        self.action_space_dim = 3
        self.action_step = 1
        self.get_state = script()
        # Initialize any other variables or parameters specific to your environment
        # For example, network throughput target, CPU usage target, etc.

    def reset(self):
        # Reset the environment and return the initial state
        self.cpu_quota = self.get_state.reset_state()
        self.network_throughput, self.pps = self.get_state.get_net_pps()
        print(self.network_throughput)
        self.message_size = MESSAGE_SIZE
        self.VM_cpu_usage = self.get_state.get_cpu_usage()
        current_state = [
            self.cpu_quota,
            self.message_size,
            self.network_throughput,
            self.pps,
            self.VM_cpu_usage
        ]
        info = {}
        return current_state, info

    def step(self, action):
        self.action = action
        self.cpu_quota = self.CPU_quota_action(self.action)
        self.message_size = MESSAGE_SIZE
        self.network_throughput, self.pps = self.get_state.get_net_pps()
        print(self.network_throughput)
        self.VM_cpu_usage = self.get_state.get_cpu_usage()
        #add_reward(self.network_throughput,self.VM_cpu_usage)
        next_state = [
            self.cpu_quota,
            self.message_size,
            self.network_throughput,
            self.pps,
            self.VM_cpu_usage
        ]
        
        #if NETWORK+5 > self.network_throughput > NETWORK-5:
        #    reward = 50
        #elif NETWORK+15 > self.network_throughput > NETWORK-15:
        #    reward = 20
        #elif NETWORK+25 > self.network_throughput > NETWORK-25:
        #    reward = 5
        #elif NETWORK+50> self.network_throughput > NETWORK-50:
        #    reward = 2
        #elif NETWORK+100 > self.network_throughput > NETWORK-100:
        #    reward = 1
        #else:
        #    reward = 0

        if NETWORK + 20 > self.network_throughput > NETWORK - 20:
            reward = 1000
        else:
            reward = int(-0.3*abs(NETWORK - self.network_throughput))

        done = False
        info = {}
        return next_state, reward, done, info
    
   
    def CPU_quota_action(self,action):
        self.cpu_quota += int(action)*1000
        if self.cpu_quota > 100000:
            self.cpu_quota = 100000
        elif self.cpu_quota < 1000:
            self.cpu_quota = 1000
        with open('set_cpu.txt','w') as f:
            f.write(str(self.cpu_quota))
        return self.cpu_quota
        
