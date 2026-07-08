# 03. RL DQN

이 폴더는 DQN agent가 VM과 상호작용하면서 CPU quota를 조절하는 online reinforcement learning 실험이다.

## 1. 실험 의미

Random Forest와 MLP는 CSV를 학습한 뒤 quota를 예측한다. RL은 실험 중에 workload를 계속 측정하면서 action을 선택한다.

```text
state -> DQN -> action -> cgroup quota 변경 -> VM workload 측정 -> next state/reward
```

## 2. State

`env_dqn.py`에서 사용하는 state는 5차원이다.

```text
cpu_quota
message_size
network_throughput
packet_per_sec
vm_cpu_usage
```

## 3. Action

`DQN1.py`에서 action index를 quota 변화량으로 바꾼다.

```text
0 -> quota 유지
1 -> quota -1000
2 -> quota +1000
```

실제 코드에서는 `ch_action = [0, -1, 1]`로 바꾼 뒤 `env_dqn.py`에서 `action * 1000`을 더한다.

## 4. Reward

target throughput은 `env_dqn.py`의 `NETWORK` 값이다.

```text
abs(target - measured) < 20:
  reward = 1000

otherwise:
  reward = -0.3 * abs(target - measured)
```

## 5. Episode 실험

한 episode는 최대 30 step이다.

```text
NUM_TIMESTEPS = 30
num_episodes = 100 on CPU
num_episodes = 300 when CUDA is available
```

실험에서 기록하는 값:

```text
episode
reward
training time
network_throughput
vm_cpu_usage
```

결과는 실행 시각이 들어간 Excel 파일로 저장된다.

## 6. 바로 실행

RL은 VM과 host 측정 스크립트가 동시에 필요하다. 먼저 private `.env`를 준비한다.

```bash
cp ../../configs/.env.example ../../.env
```

Terminal 1에서 quota 적용 loop를 켠다.

```bash
cd src/03_rl_dqn
./set_cpu.sh
```

Terminal 2에서 DQN 학습을 실행한다.

```bash
cd src/03_rl_dqn
./run_paper_experiment.sh
```

## 7. 파일 설명

```text
DQN1.py          DQN network, replay memory, epsilon-greedy action, episode loop
env_dqn.py       target bandwidth, state 구성, reward 계산, quota action 적용
script2.py       1-vCPU 계열 측정 helper
script8vcpu.py   8-vCPU 계열 측정 helper
set_cpu.sh       set_cpu.txt 값을 읽어 host cgroup cpu.max에 반복 적용
cpu_usage.sh     pidstat 기반 CPU usage 기록
kill_vnstat.sh   측정 프로세스 정리
sc_py.sh         오래된 GPU 실행 helper
```

## 8. 정리하면서 제거한 파일

`gpu_dqn.py`와 `script/` 폴더는 `DQN1.py`, `script2.py`, `script8vcpu.py`와 중복되는 오래된 변형이라 제거했다.
