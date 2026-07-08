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

# matplotlib 설정
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display

#plt.ion()

# GPU를 사용할 경우 
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)
Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))

class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """transition 저장"""
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

    # 최적화 중에 다음 행동을 결정하기 위해서 하나의 요소 또는 배치를 이용해 호촐됩니다.
    # ([[left0exp,right0exp]...]) 를 반환합니다.
    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        return self.layer4(x).to(device)

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

# 상태 관측 횟수를 얻습니다.
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
            # t.max (1)은 각 행의 가장 큰 열 값을 반환합니다.
            # 최대 결과의 두번째 열은 최대 요소의 주소값이므로,
            # 기대 보상이 더 큰 행동을 선택할 수 있습니다.
            return policy_net(state).max(1)[1].view(1, 1).to(device)
    else:
        return torch.tensor([[random.randrange(ACTION_SPACE_DIM)]], device=device, dtype=torch.long)

episode_rewards = []
episode_time =[]

import pandas as pd

now = time.strftime('%m_%d_%H_%M')

# 파일명과 시트명 설정
excel_file = f"{now}rt.xlsx"
sheet_name = "episode_rewards"

# 보상을 기록할 데이터프레임 생성 또는 엑셀 파일이 없는 경우 초기화
try:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
except:
    df = pd.DataFrame(columns=["Episode", "Reward","time","network_throughput","vm_cpu_usage"])

# 새로운 보상을 엑셀에 추가하는 함수
def add_reward(episode, reward, time,network_throughput,vm_cpu_usage):
    df.loc[len(df)] = [episode, reward, time,network_throughput,vm_cpu_usage]
    df.to_excel(excel_file, sheet_name=sheet_name, index=False, engine="op${NET_IFACE}")

def optimize_model(time_step):
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)

    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). 이것은 batch-array의 Transitions을 Transition의 batch-arrays로
    # 전환합니다.
    batch = Transition(*zip(*transitions))

    # 최종이 아닌 상태의 마스크를 계산하고 배치 요소를 연결합니다
    # (최종 상태는 시뮬레이션이 종료 된 이후의 상태)
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None]).to(device)
    state_batch = torch.cat(batch.state).to(device)
    action_batch = torch.cat(batch.action).to(device)
    reward_batch = torch.cat(batch.reward).to(device)

    # Q(s_t, a) 계산 - 모델이 Q(s_t)를 계산하고, 취한 행동의 열을 선택합니다.
    # 이들은 policy_net에 따라 각 배치 상태에 대해 선택된 행동입니다.
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # 모든 다음 상태를 위한 V(s_{t+1}) 계산
    # non_final_next_states의 행동들에 대한 기대값은 "이전" target_net을 기반으로 계산됩니다.
    # max(1)[0]으로 최고의 보상을 선택하십시오.
    # 이것은 마스크를 기반으로 병합되어 기대 상태 값을 갖거나 상태가 최종인 경우 0을 갖습니다.
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
        next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
    
    # 기대 Q 값 계산
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Huber 손실 계산
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    # 모델 최적화
    optimizer.zero_grad()
    loss.backward()
    
    # 변화도 클리핑 바꿔치기
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()

if torch.cuda.is_available():
    num_episodes = 600
else:
    num_episodes = 100

for i_episode in range(num_episodes):
    # 환경과 상태 초기화
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

        # 메모리에 변이 저장
        memory.push(state, action, next_state, reward)

        # 다음 상태로 이동
        state = next_state
        
        # (정책 네트워크에서) 최적화 한단계 수행
        optimize_model(t+1)

        # 목표 네트워크의 가중치를 소프트 업데이트
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
