import gymnasium as gym
import math
import random
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count
import os
import time
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from env_dqn import Environment

env = Environment()

# matplotlib setup
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display

#plt.ion()

# Use GPU when available
# "cuda:0" if torch.cuda.is_available() else 
device = torch.device("cpu" if torch.cuda.is_available() else "cpu")
print(device)
Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))

class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Store a transition."""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class DQN(nn.Module):

    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 128)
        self.layer2 = nn.Linear(128, 64)
        self.layer3 = nn.Linear(64, 32)
        self.layer4 = nn.Linear(32, n_actions)

    # Called with one element or batch to choose the next action during optimization.
    # Returns action values for each candidate action.
    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        return self.layer4(x)

OBSERVATION_SPACE_DIM = 5
ACTION_SPACE_DIM = 3
BATCH_SIZE = 128
GAMMA = 0.99
MEMORY_SIZE = 10000
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 500
NUM_TIMESTEPS = 30
TAU = 0.005
LR = 1e-5

# Get the initial state observation.
state, info = env.reset()

policy_net = DQN(OBSERVATION_SPACE_DIM, ACTION_SPACE_DIM).to(device)
target_net = DQN(OBSERVATION_SPACE_DIM, ACTION_SPACE_DIM).to(device)
target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.Adam(policy_net.parameters(), lr=LR, amsgrad=True)
memory = ReplayMemory(MEMORY_SIZE)

steps_done = 0

def select_action(state):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            # t.max(1) returns the largest column value for each row.
            # The second returned column is the argmax index,
            # so it selects the action with the larger expected reward.
            return policy_net(state).max(1)[1].view(1, 1).to(device)
    else:
        return torch.tensor([[random.randrange(ACTION_SPACE_DIM)]], device=device, dtype=torch.long)


episode_rewards = []
episode_time =[]

# def plot_rewards(show_result=False):
#     plt.figure(1)
#     durations_t = torch.tensor(episode_rewards,device=device, dtype=torch.float)
#     if show_result:
#         plt.title('Result')
#     else:
#         plt.clf()
#         plt.title('Training...')
#     plt.xlabel('Episode')
#     plt.ylabel('rewards')
#     plt.plot(durations_t.numpy())
#     plt.xlabel('Episode')
#     plt.ylabel('rewards')
#     plt.plot(durations_t.numpy())
#     # Plot the rolling mean over 100 episodes
#     if len(durations_t) >= 100:
#         means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
#         means = torch.cat((torch.zeros(99), means))
#         plt.plot(means.numpy())

#     plt.pause(0.001)  # Pause briefly so the plot can update
#     if is_ipython:
#         if not show_result:
#             display.display(plt.gcf())
#             display.clear_output(wait=True)
#         else:
#             display.display(plt.gcf())

import pandas as pd

now = time.strftime('%m_%d_%H_%M')

# Configure file and sheet names
excel_file = f"{now}rt.xlsx"
sheet_name = "episode_rewards"

# Create or initialize reward dataframe
try:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
except:
    df = pd.DataFrame(columns=["Episode", "Reward","time","network_throughput","vm_cpu_usage"])

# Append a new reward row to Excel
def add_reward(episode, reward, time,network_throughput,vm_cpu_usage):
    df.loc[len(df)] = [episode, reward, time,network_throughput,vm_cpu_usage]
    df.to_excel(excel_file, sheet_name=sheet_name, index=False, engine="openpyxl")

def optimize_model(time_step):
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)

    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). This converts a batch-array of Transitions
    # into Transition arrays grouped by field.
    batch = Transition(*zip(*transitions))

    # Compute the non-final-state mask and concatenate batch elements
    # Final states are states after the simulation terminates
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None])
    state_batch = torch.cat(batch.state).to(device)
    action_batch = torch.cat(batch.action).to(device)
    reward_batch = torch.cat(batch.reward).to(device)

    # Compute Q(s_t, a): the model computes Q(s_t), then selects the taken action column.
    # These are the actions selected by policy_net for each batch state.
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # Compute V(s_{t+1}) for all next states
    # Expected values for non_final_next_states are computed from the previous target_net.
    # Select the best reward with max(1)[0].
    # Values are merged by mask, using zero for final states.
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
        next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
    
    # Compute expected Q values
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Compute Huber loss
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    
    # Clip gradients
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()

if torch.cuda.is_available():
    num_episodes = 300
else:
    num_episodes = 100

for i_episode in range(num_episodes):
    # Reset environment and state
    state, info = env.reset()
    state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    episode_reward = 0
    
    start_time = time.time()
    for t in range(NUM_TIMESTEPS):
        action = select_action(state)
        ch_action = [0,-1,1]
        observation, reward, terminated, truncated = env.step(ch_action[action.item()])
        reward = torch.tensor([reward], device=device)
        
        if t == NUM_TIMESTEPS -1:
            terminated = True
        done = terminated or truncated
        
        if terminated:
            next_state = None
        else:
            next_state = torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)

        # Store transition in replay memory
        memory.push(state, action, next_state, reward)

        # Move to the next state
        state = next_state
        
        # Run one optimization step on the policy network
        optimize_model(t+1)

        # Soft-update target network weights
        # θ′ ← τ θ + (1 −τ )θ′
        target_net_state_dict = target_net.state_dict()
        policy_net_state_dict = policy_net.state_dict()
        for key in policy_net_state_dict:
            target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
            target_net.load_state_dict(target_net_state_dict)
        episode_reward += reward
        if done or reward == 1000:
            end_time = time.time()
            network,cpu_usage = observation[2],observation[4]
            os.system('./kill_vnstat.sh')
            break
    
    print("Episodes",i_episode + 1,"Total reward",float(episode_reward))
    add_reward(i_episode + 1, float(episode_reward), end_time-start_time,network,cpu_usage)
episode_range = list(range(1,num_episodes+1))

print('Complete')
#plot_rewards(show_result=True)

#plt.ioff()
