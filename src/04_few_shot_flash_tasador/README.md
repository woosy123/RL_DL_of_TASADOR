# 04. Few-shot FLASH TASADOR

This folder adapts the FLASH paper code to a TASADOR-style quota dataset. It is not the main TASADOR Random Forest experiment. It is an extension experiment that asks whether a model can predict CPU quota for a new workload or configuration from only a small support set.

## 1. Experiment Purpose

Random Forest and MLP train from full quota-sweep CSVs. Few-shot FLASH TASADOR treats the support set itself as part of the model input.

```text
support samples:
  K observed samples
  feature + cpu_quota

query sample:
  workload/config feature whose quota is unknown

output:
  cpu_quota for the query sample
```

The core question is whether a model can estimate a quota curve for a new workload or configuration without sweeping every quota value again.

## 2. Difference From The Original FLASH README

The original FLASH README describes MultiCloud resource configuration search. This folder keeps the few-shot regression structure but changes the task to TASADOR quota prediction.

```text
Original FLASH:
  multicloud dataset
  latency/cost prediction
  generic few-shot regression

Adapted TASADOR version:
  tasador dataset
  cpu_quota prediction
  workload/config support-query split
```

## 3. Input Data

The TASADOR few-shot CSV uses more configuration features than the RF/MLP CSV.

```csv
workload,vcpu,cpu_model,mem_gb,nic_gbps,switch_gbps,cpu_quota,message_size,network_throughput,packet_per_sec,vm_cpu_usage
```

The training setup excludes one configuration from the train CSV and places it in the test CSV. Example:

```text
train_csv = tasador_wo_config3_8v.csv
test_csv  = tasador_config3_8v.csv
```

## 4. Model Structure

The representative command uses RNN embedding for few-shot regression.

```bash
python3 train.py --dataset=tasador --rnn --num_shots=5
```

File guide:

```text
train.py            training entrypoint
test.py             evaluation entrypoint; writes pred_vs_true.csv and metrics.txt
eval.py             validation/test helper entrypoint
snail.py            SNAIL/RNN/FC few-shot model definitions
blocks.py           SNAIL building blocks
tasador_dataset.py  converts TASADOR CSV rows into support/query tasks
params.py           TASADOR feature dimensions
utils.py            dataloader construction
rmse.py             summarizes RMSE across experiment folders
```

## 5. Run The Sweep

The default script runs 3, 4, 5, 6, and 7-shot training with both `uniform` and `quota_linspace` support strategies.

```bash
cd src/04_few_shot_flash_tasador
./run_paper_experiment.sh tasador_wo_config3_8v.csv tasador_config3_8v.csv
```

To run on CPU:

```bash
USE_CUDA=0 ./run_paper_experiment.sh tasador_wo_config3_8v.csv tasador_config3_8v.csv
```

Expected outputs:

```text
experiments/exp-<name>/best_model.pth
experiments/exp-<name>/metrics.txt
experiments/exp-<name>/pred_vs_true.csv
```

This command runs without a VM because it only trains from CSV files. It will fail if the required CSVs are missing.

## 6. Single Experiment Command

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

Evaluation:

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
  choose evenly spaced samples from the sorted group

quota_linspace:
  choose samples near evenly spaced CPU quota targets

edge_median:
  mix edge samples with samples near the middle of the group
```

## 8. Cleanup Notes

The following Random Forest-related files were removed from this folder:

```text
generate_modelG_any.py
generate_modelH_any.py
rf_model.py
py_set.sh
```
