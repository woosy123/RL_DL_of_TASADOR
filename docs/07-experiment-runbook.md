# Experiment Runbook

This page explains what each experiment was for and how the scripts were run conceptually. Commands are sanitized and use placeholders from `configs/.env.example`.

## 0. Common Setup

All experiments assume a KVM VM running a network workload and a host machine that can control the VM-related CPU quota.

```bash
cp configs/.env.example .env
# Fill .env on the private experiment host.
```

Typical private environment variables:

```bash
export VM_HOST=<vm-ip-or-hostname>
export VM_USER=<vm-user>
export VM_SSH_KEY=~/.ssh/id_rsa
export TARGET_HOST=<netperf-server-or-peer-host>
export NET_IFACE=<host-network-interface>
export CPU_CGROUP_PATH=<host-cgroup-cpu.max-path>
export DATA_DIR=./data
export RESULT_DIR=./results
```

Do not commit `.env`, raw datasets, result logs, model checkpoints, or machine-specific paths.

## 1. Quota Sweep Data Collection

### Purpose

Collect the relationship between CPU quota and network performance. This is the base dataset for Random Forest, MLP, and few-shot experiments.

### What It Measures

For each CPU quota and message size:

```text
cpu_quota
message_size
network_throughput
packet_per_sec
vm_cpu_usage
```

### How It Was Run

The original experiments used shell scripts that repeatedly:

1. Applied a CPU quota to the host-side cgroup.
2. Started a workload in the VM through SSH.
3. Measured throughput with `vnstat`.
4. Measured CPU usage with `pidstat` or `mpstat`.
5. Appended the measurement to CSV.

Sanitized template:

```bash
source .env
bash scripts/collect/collect_quota_sweep.sh
```

Equivalent original-code locations:

```text
src/random_forest_tasador/test/collect.sh
src/random_forest_tasador/test/run.sh
src/random_forest_tasador/share/default.sh
src/random_forest_tasador/tc/default.sh
src/mlp_regression/netperf.py
src/mlp_regression/netperf.sh
src/mlp_regression/get_vnstat.sh
```

### Outputs

```text
data/quota_sweep.csv
```

Expected schema:

```csv
cpu_quota,message_size,network_throughput,packet_per_sec,vm_cpu_usage
```

## 2. Random Forest TASADOR Experiment

### Purpose

Reproduce the TASADOR-style bandwidth-to-CPU translation with Random Forest regression. This experiment checks whether a supervised model can predict the CPU allocation needed for a target bandwidth SLO.

### Models

Model-G:

```text
[message_size, target_network_throughput] -> vm_cpu_usage
```

Model-H:

```text
[message_size, target_network_throughput, packet_per_sec, vm_cpu_usage] -> cpu_quota
```

In TASADOR's concatenated prediction, Model-G first predicts VM CPU usage. Model-H then uses that value to predict Host CPU quota.

### How It Was Run

Original script flow:

```bash
cd src/random_forest_tasador
python3 generate_modelG_any.py
python3 generate_modelH_any.py
python3 evaluate_modelG_any.py
python3 evaluate_modelH_any.py
```

Convenience wrapper in the original script tree:

```bash
cd src/random_forest_tasador
bash run_model.sh
```

File-level meaning:

| File | What it does |
|---|---|
| `generate_modelG_any.py` | Trains Model-G, which predicts VM CPU usage from message size and target throughput |
| `generate_modelH_any.py` | Trains Model-H, which predicts Host CPU quota from message size, throughput, PPS, and VM CPU usage |
| `evaluate_modelG_any.py` | Evaluates the trained Model-G against held-out or split measurement data |
| `evaluate_modelH_any.py` | Evaluates the trained Model-H and reports CPU quota prediction error |
| `run_model.sh` | Runs Model-G and Model-H training and extracts training-time logs |
| `test/collect.sh` | Collects raw quota-sweep measurement logs before model training |
| `test/set_quota.sh` | Applies a quota to the host cgroup path |
| `tc/run.sh`, `tc/default.sh` | Runs traffic-control baseline experiments |
| `share/run.sh`, `share/default.sh` | Runs vCPU-share/priority baseline experiments |

Sanitized template:

```bash
python3 scripts/train/train_random_forest.py \
  --csv data/quota_sweep.csv \
  --model G \
  --out models/model_g.joblib

python3 scripts/train/train_random_forest.py \
  --csv data/quota_sweep.csv \
  --model H \
  --out models/model_h.joblib
```

### Outputs

```text
models/model_g.joblib
models/model_h.joblib
evaluation RMSE/RMSLE
predicted CPU quota
```

### What Was Compared

The TASADOR paper compares Random Forest with Linear Regression and Support Vector Regression. The local scripts also include legacy comparison scripts under the Random Forest source tree.

## 3. MLP / Deep Learning Regression Experiment

### Purpose

Train a PyTorch MLP to predict CPU quota directly from network and VM metrics. This was used as a deep learning baseline against TASADOR.

### Model

```text
input_dim -> 64 -> 32 -> 32 -> 16 -> 8 -> 1
```

The six-layer structure was selected after comparing different numbers of Linear/ReLU blocks. RMSE was used as the model-selection metric, and the six-linear-layer version produced the lowest RMSE among the tested structures.

Input:

```text
message_size
network_throughput
packet_per_sec
vm_cpu_usage
```

Target:

```text
cpu_quota
```

### How It Was Run

Original script flow:

```bash
cd src/mlp_regression
python3 regression_dl.py
python3 predict_cpu_quota.py
python3 predict_netperf.py
```

The first script trains/evaluates the MLP. The prediction script generates quota predictions for target network SLOs. The netperf evaluation script applies those predicted quotas and measures actual throughput.

The epoch sweep was used to compare model quality and training cost. The experiment notes compare epoch values such as:

```text
200, 400, 600, 800, 1000, 1200
```

The expected output from this sweep is an RMSE/training-time table or plot. In the observed notes, 1200 epochs produced the lowest RMSE among the compared epoch settings, so the 1200-epoch checkpoint was used for actual-performance comparison against TASADOR.

Sanitized training template:

```bash
python3 scripts/train/train_mlp.py \
  --csv data/quota_sweep.csv \
  --out models/mlp_cpu_quota.pth \
  --epochs 800
```

Sanitized evaluation template:

```bash
bash scripts/evaluate/evaluate_predicted_quota.sh results/mlp_predicted_quota.csv
```

### Outputs

```text
MLP checkpoint
RMSE by epoch
predicted quota CSV
measured throughput after applying predicted quota
normalized bandwidth
```

### Why It Matters

The MLP can learn nonlinear relationships, but CPU quota prediction becomes unstable when the same throughput appears at multiple quota values due to saturation or VM/network behavior.

The 1-vCPU case showed this problem more clearly than the 8-vCPU case. Because the maximum network throughput is lower and saturation appears earlier, similar throughput values may correspond to several quota values. This makes direct quota regression harder and explains why the DL baseline can have wider normalized-bandwidth variation than TASADOR.

## 4. RL / DQN Experiment

### Purpose

Test whether an online reinforcement learning agent can adjust CPU quota step by step until measured throughput approaches the target network SLO.

### State

```text
[cpu_quota, message_size, network_throughput, packet_per_sec, vm_cpu_usage]
```

### Action

```text
0 -> keep quota
1 -> decrease quota by 1000
2 -> increase quota by 1000
```

### Reward

```text
reward = 1000                         if throughput is within target +/- 20 Mbps
reward = -0.3 * abs(target - measured) otherwise
```

### How It Was Run

Original script flow:

```bash
cd src/rl_dqn

# Terminal 1: continuously apply quota from set_cpu.txt
bash set_cpu.sh

# Terminal 2: run or keep the workload active in the VM
# Usually netperf was used from the VM side.

# Terminal 3: train DQN
python3 DQN1.py
```

Each episode has up to 30 steps. At every step, the agent chooses whether to keep quota, decrease quota by 1000, or increase quota by 1000. The environment then measures throughput and gives reward based on distance from the target SLO.

Episode-level experiment variables:

```text
number of episodes
initial CPU quota
target network SLO
message size
1-vCPU vs 8-vCPU environment
```

The experiment notes describe 300-episode runs for both 1-vCPU and 8-vCPU settings. The purpose was to observe whether average reward improves over episodes and whether normalized bandwidth approaches 1.0.

Supporting scripts:

```text
env_dqn.py       # DQN environment
script2.py       # 1-vCPU metric collection helper
script8vcpu.py   # 8-vCPU metric collection helper
cpu_usage.sh     # CPU usage logging
kill_vnstat.sh   # cleanup helper
```

### Outputs

```text
episode reward xlsx
training time
measured throughput per episode
VM CPU usage per episode
```

### Notes

The original RL experiment depends on external processes. The quota loop, workload generator, and metric collection must be running consistently. This makes RL more sensitive to initial quota, target SLO, and timing than the offline RF/MLP experiments.

The main interpretation from the RL runs is that DQN can reach good normalized bandwidth under carefully chosen initial conditions, but it does not consistently outperform the offline TASADOR-style approach. If the initial quota or SLO is poorly chosen, the agent can spend many episodes receiving large negative rewards without finding the correct quota region.

## 5. Few-Shot / Meta-Learning Extension

### Purpose

Evaluate whether a meta-learning/few-shot model can predict CPU quota for a query point after observing only a small number of support samples from the same workload/hardware/message-size group.

This is not the same as the Random Forest TASADOR pipeline. Random Forest TASADOR trains a fixed regression model from full quota-sweep data. The few-shot experiment instead gives the model a small support set at inference/training time and asks it to infer another quota point in that same context.

This distinction is important because a standard Random Forest is not naturally a few-shot adaptation model. The few-shot scripts therefore use SNAIL/RNN-style context models rather than the Random Forest pipeline.

### Input Format

Extended TASADOR schema:

```csv
workload,vcpu,cpu_model,mem_gb,nic_gbps,switch_gbps,cpu_quota,message_size,network_throughput,packet_per_sec,vm_cpu_usage
```

### How It Was Run

Original script flow:

```bash
cd src/few_shot_tasador

python3 train.py \
  --dataset=tasador \
  --rnn \
  --num_shots=5 \
  --support_strategy=quota_linspace \
  --exp=tasador-qlin-5s \
  --train_csv <train_csv> \
  --test_csv <test_csv>

python3 test.py \
  --dataset=tasador \
  --rnn \
  --num_shots=5 \
  --support_strategy=quota_linspace \
  --exp=tasador-qlin-5s \
  --train_csv <train_csv> \
  --test_csv <test_csv>
```

Batch execution was organized through:

```bash
cd src/few_shot_tasador
bash reproduce.sh
bash test.sh
```

### Models

```text
SnailFewShot   attention + temporal convolution + FC
RNNFewShot     bidirectional GRU + FC
Sizeless       plain FC baseline
```

### Outputs

```text
experiments/exp-*/best_model.pth
experiments/exp-*/last_model.pth
experiments/exp-*/metrics.txt
experiments/exp-*/pred_vs_true.csv
train_loss.txt
train_mape.txt
val_loss.txt
val_mape.txt
```

These outputs are intentionally excluded from the public repository.

## 6. Baseline Network Experiments

### Purpose

Compare TASADOR-style CPU quota control against network scheduling or vCPU priority baselines.

### How It Was Run

Traffic control baseline:

```bash
cd src/random_forest_tasador/tc
bash run.sh
```

vCPU share/priority baseline:

```bash
cd src/random_forest_tasador/share
bash run.sh
```

These scripts vary bandwidth limits or CPU weights and record throughput/CPU metrics.

### Outputs

```text
vnstat logs
pidstat logs
mpstat logs
normalized bandwidth
total CPU utilization
```

Raw logs are excluded from the repository.

## 7. Recommended Public Reproduction Order

For a clean rerun on a new private machine:

```bash
# 1. Configure private environment
cp configs/.env.example .env

# 2. Collect quota sweep data
bash scripts/collect/collect_quota_sweep.sh

# 3. Train Random Forest TASADOR models
python3 scripts/train/train_random_forest.py --csv data/quota_sweep.csv --model G --out models/model_g.joblib
python3 scripts/train/train_random_forest.py --csv data/quota_sweep.csv --model H --out models/model_h.joblib

# 4. Train MLP baseline
python3 scripts/train/train_mlp.py --csv data/quota_sweep.csv --out models/mlp_cpu_quota.pth

# 5. Evaluate predicted quota CSVs
bash scripts/evaluate/evaluate_predicted_quota.sh results/predicted_quota.csv

# 6. Run DQN only after collection/evaluation scripts are stable
cd src/rl_dqn
bash set_cpu.sh
python3 DQN1.py
```
