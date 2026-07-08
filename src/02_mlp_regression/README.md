# 02. MLP Regression

이 폴더는 Random Forest 대신 PyTorch MLP로 CPU quota를 예측하는 deep learning baseline 실험이다.

## 1. 실험 의미

Random Forest TASADOR와 같은 quota sweep CSV를 사용하지만, 모델을 neural network로 바꿔서 비교한다.

```text
input:
  message_size
  network_throughput
  packet_per_sec
  vm_cpu_usage

output:
  cpu_quota
```

## 2. 모델 구조

실험에서는 Linear layer 수를 바꾸어가며 비교했고, 최종적으로 다음 구조가 대표 구조로 사용되었다.

```text
input_dim -> 64 -> 32 -> 32 -> 16 -> 8 -> 1
```

각 hidden layer 뒤에는 ReLU가 들어간다. 출력 1개는 predicted CPU quota이다.

## 3. Epoch 실험

epoch 수를 바꾸어 RMSE와 training time을 비교했다.

```text
200, 400, 600, 800, 1000, 1200 epochs
```

관찰 목적은 다음과 같다.

```text
1. epoch 증가에 따라 RMSE가 얼마나 줄어드는지
2. training time이 얼마나 증가하는지
3. 1-vCPU와 8-vCPU에서 quota regression 난이도가 어떻게 달라지는지
```

1-vCPU 환경에서는 bandwidth가 saturation되면서 같은 throughput에 여러 quota가 대응될 수 있어 8-vCPU보다 예측이 더 흔들릴 수 있다.

## 4. 바로 실행

```bash
cd src/02_mlp_regression
./run_paper_experiment.sh ../../data/quota_sweep.csv 1200
```

두 번째 인자는 epoch 수다. 생략하면 800 epoch로 실행된다.

```bash
./run_paper_experiment.sh ../../data/quota_sweep.csv
```

출력:

```text
models/mlp_quota.pt
```

## 5. 원본 실험 파일

```text
regression_dl.py       MLP 학습, RMSE 계산, epoch별 결과 기록
predict_cpu_quota.py   학습 데이터로 MLP를 학습한 뒤 target quota 예측 실험
predict_netperf.py     예측 quota를 host cgroup에 적용하고 netperf 측정
netperf.py             netperf 실행 보조 코드
netperf.sh             VM에서 netperf를 여러 개 실행하는 helper
set_cpu.sh             host cgroup cpu.max에 quota 적용
get_vnstat.sh          vnstat 측정값 저장
predict/to_csv.py      예측 결과를 CSV로 변환하는 보조 코드
```

## 6. VM과 연결되는 부분

MLP 학습 자체는 CSV만 있으면 offline으로 수행된다. VM과 다시 연결되는 시점은 `predict_netperf.py`다.

```text
1. predict_cpu_quota.py 또는 학습 모델로 target SLO별 quota 예측
2. predict_netperf.py가 set_cpu.sh로 host cgroup에 quota 적용
3. netperf.sh가 VM에 SSH 접속해서 netperf workload 실행
4. get_vnstat.sh로 실제 throughput 측정
```

## 7. 정리하면서 제거한 파일

다음 파일은 대표 실험과 중복되는 테스트/변형 파일이라 제거했다.

```text
test1.py
regression_test.py
cuda_predict_cpu_quota.py
```
