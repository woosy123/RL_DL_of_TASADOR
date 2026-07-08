# 03. RL DQN

This folder contains the online reinforcement learning experiment where a DQN agent adjusts CPU quota while observing VM workload behavior.

## 1. Experiment Purpose

Random Forest and MLP train from collected CSV data. RL interacts with the workload during the experiment.

```text
state -> DQN -> action -> cgroup quota update -> VM workload measurement -> next state/reward
```

## 2. State

`env_dqn.py` uses a five-dimensional state.

```text
cpu_quota
message_size
network_throughput
packet_per_sec
vm_cpu_usage
```

## 3. Action

`DQN1.py` maps action indices to quota changes.

```text
0 -> keep quota
1 -> quota -1000
2 -> quota +1000
```

The code converts the action with `ch_action = [0, -1, 1]`, and `env_dqn.py` applies `action * 1000`.

## 4. Reward

The target throughput is the `NETWORK` value in `env_dqn.py`.

```text
abs(target - measured) < 20:
  reward = 1000

otherwise:
  reward = -0.3 * abs(target - measured)
```

## 5. Episode Sweep

Each episode has up to 30 steps.

```text
NUM_TIMESTEPS = 30
num_episodes = 100 on CPU
num_episodes = 300 when CUDA is available
```

Recorded values:

```text
episode
reward
training time
network_throughput
vm_cpu_usage
```

The script writes an Excel result file with a timestamped name.

## 6. Run The Experiment

This experiment requires the real host and VM measurement setup. Prepare a private `.env` first.

```bash
cp ../../configs/.env.example ../../.env
```

Terminal 1 starts the quota-application loop:

```bash
cd src/03_rl_dqn
./set_cpu.sh
```

Terminal 2 starts DQN training:

```bash
cd src/03_rl_dqn
./run_paper_experiment.sh
```

This command cannot complete on a machine without the configured VM, cgroup path, workload scripts, and measurement helpers.

## 7. File Guide

```text
DQN1.py          DQN network, replay memory, epsilon-greedy policy, episode loop
env_dqn.py       target bandwidth, state construction, reward calculation, quota action
script2.py       1-vCPU measurement helper
script8vcpu.py   8-vCPU measurement helper
set_cpu.sh       repeatedly applies the quota stored in set_cpu.txt
cpu_usage.sh     records CPU usage with pidstat
kill_vnstat.sh   stops measurement processes
sc_py.sh         historical GPU helper
```

## 8. Cleanup Notes

`gpu_dqn.py` and the old `script/` directory were removed because they duplicated the canonical `DQN1.py`, `script2.py`, and `script8vcpu.py` path.
