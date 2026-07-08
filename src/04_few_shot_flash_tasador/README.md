# 04. Few-shot FLASH TASADOR

이 폴더는 FLASH 논문의 GitHub 코드를 가져와 TASADOR quota dataset에 맞게 수정한 실험이다. TASADOR 논문의 Random Forest 본 실험은 아니며, 적은 수의 support sample만 보고 새로운 workload/config의 CPU quota를 예측할 수 있는지 확인하는 확장 실험이다.

## 1. 실험 의미

Random Forest와 MLP는 전체 quota sweep CSV를 학습한다. Few-shot FLASH TASADOR는 support set 자체가 입력에 포함된다.

```text
support samples:
  K개의 관측값
  feature + cpu_quota

query sample:
  quota를 알고 싶은 workload/config feature

output:
  query sample의 cpu_quota
```

즉, "새로운 VM/workload/config에 대해 quota sweep을 전부 다시 하지 않고, K개 샘플만으로 quota curve를 추정할 수 있는가?"를 보는 실험이다.

## 2. FLASH 원본 README에서 달라진 점

원본 README는 MultiCloud resource configuration search 예시를 설명한다. 현재 폴더는 그 구조를 TASADOR 데이터셋에 맞게 바꿨다.

```text
원본 FLASH:
  multicloud dataset
  latency/cost 예측
  generic few-shot regression

수정된 TASADOR 버전:
  tasador dataset
  cpu_quota 예측
  workload/config별 support/query split
```

## 3. 입력 데이터

TASADOR few-shot CSV는 일반 RF/MLP CSV보다 config feature가 더 많다.

```csv
workload,vcpu,cpu_model,mem_gb,nic_gbps,switch_gbps,cpu_quota,message_size,network_throughput,packet_per_sec,vm_cpu_usage
```

학습에서는 특정 config를 train CSV에서 제외하고, test CSV에 둔다. 예를 들어:

```text
train_csv = tasador_wo_config3_8v.csv
test_csv  = tasador_config3_8v.csv
```

## 4. 모델 구조

대표 실행은 RNN embedding 기반 few-shot regression이다.

```bash
python3 train.py --dataset=tasador --rnn --num_shots=5
```

관련 파일:

```text
train.py            학습 entrypoint
test.py             학습된 모델 평가, pred_vs_true.csv와 metrics.txt 저장
eval.py             validation/test 평가용 보조 entrypoint
snail.py            SNAIL/RNN/FC few-shot model 정의
blocks.py           SNAIL block 구성요소
tasador_dataset.py  TASADOR CSV를 support/query task로 변환
params.py           TASADOR feature 차원 설정
utils.py            dataloader 생성
rmse.py             여러 experiment의 RMSE 요약
```

## 5. 바로 실행

기본 실행은 3, 4, 5, 6, 7-shot을 `uniform`과 `quota_linspace` support strategy로 반복한다.

```bash
cd src/04_few_shot_flash_tasador
./run_paper_experiment.sh tasador_wo_config3_8v.csv tasador_config3_8v.csv
```

CUDA를 끄고 CPU에서 돌리려면:

```bash
USE_CUDA=0 ./run_paper_experiment.sh tasador_wo_config3_8v.csv tasador_config3_8v.csv
```

출력:

```text
experiments/exp-<name>/best_model.pth
experiments/exp-<name>/metrics.txt
experiments/exp-<name>/pred_vs_true.csv
```

## 6. 단일 실험 명령어

```bash
python3 train.py \
  --dataset=tasador \
  --rnn \
  --num_shots=5 \
  --support_strategy=quota_linspace \
  --exp=tasador-qlin-5s-config3 \
  --train_csv tasador_wo_config3_8v.csv \
  --test_csv tasador_config3_8v.csv
```

평가:

```bash
python3 test.py \
  --dataset=tasador \
  --rnn \
  --num_shots=5 \
  --support_strategy=quota_linspace \
  --exp=tasador-qlin-5s-config3 \
  --train_csv tasador_wo_config3_8v.csv \
  --test_csv tasador_config3_8v.csv
```

## 7. Support Strategy

```text
uniform:
  group 안에서 정렬된 sample을 균등하게 선택

quota_linspace:
  CPU quota 범위를 기준으로 균등한 지점의 sample 선택

edge_median:
  가장자리와 중앙부 sample을 섞어 선택
```

## 8. 정리하면서 제거한 파일

Random Forest TASADOR와 섞여 있던 파일은 제거했다.

```text
generate_modelG_any.py
generate_modelH_any.py
rf_model.py
py_set.sh
```
