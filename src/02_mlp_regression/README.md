# 02. MLP Regression

This folder contains the deep learning baseline that predicts CPU quota with a PyTorch MLP instead of Random Forest.

## 1. Experiment Purpose

The MLP uses the same quota-sweep data as the TASADOR-style Random Forest workflow, but replaces the regression model with a neural network.

```text
input:
  message_size
  network_throughput
  packet_per_sec
  vm_cpu_usage

output:
  cpu_quota
```

## 2. Model Structure

The experiment compared multiple Linear/ReLU layer configurations. The representative final structure is:

```text
input_dim -> 64 -> 32 -> 32 -> 16 -> 8 -> 1
```

The output is the predicted CPU quota.

## 3. Epoch Sweep

The experiment varied epoch count to compare RMSE and training time.

```text
200, 400, 600, 800, 1000, 1200 epochs
```

The comparison checks:

```text
1. whether RMSE decreases as epochs increase
2. how much training time increases
3. whether 1-vCPU and 8-vCPU settings differ in regression difficulty
```

The 1-vCPU case can be harder because throughput may saturate, causing multiple quota values to map to similar throughput.

## 4. Run The Reproduction Entrypoint

```bash
cd src/02_mlp_regression
./run_paper_experiment.sh ../../data/quota_sweep.csv 1200
```

The second argument is the epoch count. If omitted, the script uses 800 epochs.

```bash
./run_paper_experiment.sh ../../data/quota_sweep.csv
```

Expected output:

```text
models/mlp_quota.pt
```

This command runs without a VM because it only trains from a CSV. It will fail if the CSV is missing or does not contain the required columns.

## 5. Historical Files

```text
regression_dl.py       trains the MLP and records RMSE/training time
predict_cpu_quota.py   trains the MLP and generates quota predictions
predict_netperf.py     applies predicted quota values and measures netperf throughput
netperf.py             netperf helper
netperf.sh             starts netperf workloads through SSH
set_cpu.sh             writes quota to host cgroup cpu.max
get_vnstat.sh          stores vnstat measurements
predict/to_csv.py      converts prediction text output to CSV
```

## 6. VM Connection

MLP training itself is offline. The VM is used when validating predicted quota values.

```text
1. train or load an MLP quota predictor
2. generate target-SLO quota predictions
3. apply each quota with set_cpu.sh
4. run netperf through SSH
5. record actual throughput with get_vnstat.sh
```

## 7. Cleanup Notes

The following duplicate or temporary variants were removed:

```text
test1.py
regression_test.py
cuda_predict_cpu_quota.py
```
