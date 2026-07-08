# 01. Random Forest TASADOR

이 폴더는 TASADOR 논문 방식에 가장 가까운 실험을 담고 있다. 핵심 아이디어는 VM의 target network throughput을 만족시키기 위해 필요한 host-side CPU quota를 Random Forest로 예측하는 것이다.

## 1. 실험 의미

Random Forest TASADOR는 offline supervised regression이다. 먼저 CPU quota를 여러 값으로 바꾸면서 VM workload를 실행하고, 그 결과를 CSV로 만든다. 그 CSV로 두 모델을 학습한다.

```text
Model-G:
  message_size, network_throughput -> vm_cpu_usage

Model-H:
  message_size, network_throughput, packet_per_sec, vm_cpu_usage -> cpu_quota
```

논문 관점에서는 Model-G가 target bandwidth에서 필요한 VM CPU usage를 추정하고, Model-H가 그 usage와 network feature를 이용해 host CPU quota를 산출한다.

## 2. 입력 데이터

학습 CSV는 다음 컬럼을 가진다.

```csv
cpu_quota,message_size,network_throughput,packet_per_sec,vm_cpu_usage
```

원본 스크립트 일부는 다음처럼 대문자/공백 컬럼명을 사용한다.

```csv
CPU Quota,Message Size,Network Throughput,PPS,VM CPU Usage
```

GitHub 재현용 실행 스크립트는 lowercase snake_case CSV를 기준으로 한다.

## 3. 바로 실행

저장소 루트에서 데이터셋을 준비한 뒤 실행한다.

```bash
cd src/01_random_forest_tasador
./run_paper_experiment.sh ../../data/quota_sweep.csv
```

출력은 이 폴더 아래에 생긴다.

```text
models/model_g.joblib
models/model_h.joblib
```

## 4. 원본 실험 스크립트 실행

원본에 가까운 흐름을 보고 싶을 때는 아래 파일을 확인한다.

```bash
python3 generate_modelG_any.py
python3 generate_modelH_any.py
python3 evaluate_modelG_any.py
python3 evaluate_modelH_any.py
```

`run_model.sh`는 원래 서버에서 Model-G와 Model-H를 연속 실행하기 위해 둔 스크립트다. 현재 GitHub용 구조에서는 `run_paper_experiment.sh`가 더 안전한 재현 entrypoint이다.

## 5. VM과 연결되는 부분

데이터 수집은 `collect/`에 있다.

```text
collect/collect.sh    quota를 바꾸며 VM workload 실행, vnstat/pidstat 로그 수집
collect/run.sh        특정 quota 값에서 반복 측정
collect/set_quota.sh  host cgroup cpu.max에 quota 적용
collect/netperf.py    netperf 기반 측정 보조 코드
```

VM과 연결되는 방식은 다음 순서다.

```text
1. host에서 CPU_CGROUP_PATH에 quota 기록
2. VM에 SSH 접속
3. VM 안에서 netperf 또는 workload script 실행
4. host에서 vnstat/pidstat/mpstat로 throughput, PPS, CPU usage 측정
5. CSV로 정리한 뒤 Model-G/H 학습
```

민감한 값은 `.env`에만 둔다.

```bash
cp ../../configs/.env.example ../../.env
```

필요한 대표 변수:

```text
VM_HOST
VM_USER
VM_SSH_KEY
VM_WORKLOAD_SCRIPT
NET_IFACE
CPU_CGROUP_PATH
```

## 6. Baseline

`tc/`와 `share/`는 TASADOR와 비교하기 위한 baseline 실험이다.

```text
tc/      traffic control로 network bandwidth를 제한하는 baseline
share/   CPU share/priority 계열 baseline
```

이 baseline은 환경 의존성이 강하므로 공개 repo에서는 바로 실행보다 참고용 성격이 크다.

## 7. 정리하면서 제거한 파일

다음 파일/폴더는 논문 실험 재현 흐름과 직접 관련이 낮거나, 외부 repo 복제본/임시 테스트라서 제거했다.

```text
a.py
test.py
test.sh
apply_cpu_quota.sh
netperf_vm.sh
dynamic/
native/
Inferencing-CPU-for-network-performance-in-virtualized-environments-main/
```

`predict_single_quota.py`는 단일 quota 예측 예시였기 때문에 `predict_single_quota.py`로 이름을 바꿨다.
