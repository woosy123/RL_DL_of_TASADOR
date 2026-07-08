# 01. Random Forest TASADOR

This folder contains the experiment flow closest to the TASADOR paper. The core idea is to translate a target VM network throughput into the host-side CPU quota required to satisfy it.

## 1. Experiment Purpose

Random Forest TASADOR is an offline supervised regression workflow. First, the host sweeps CPU quota values while the VM runs a workload. The resulting measurements are converted into a CSV dataset. Two models are then trained from that dataset.

```text
Model-G:
  message_size, network_throughput -> vm_cpu_usage

Model-H:
  message_size, network_throughput, packet_per_sec, vm_cpu_usage -> cpu_quota
```

Model-G estimates the VM CPU usage needed for a target bandwidth. Model-H uses that estimated usage together with network features to predict the host CPU quota.

## 2. Input Data

The cleaned reproduction entrypoint expects this CSV schema:

```csv
cpu_quota,message_size,network_throughput,packet_per_sec,vm_cpu_usage
```

Some original scripts use historical column names:

```csv
CPU Quota,Message Size,Network Throughput,PPS,VM CPU Usage
```

Use the lowercase snake_case schema for `run_paper_experiment.sh`.

## 3. Run The Reproduction Entrypoint

Prepare the dataset from the repository root, then run:

```bash
cd src/01_random_forest_tasador
./run_paper_experiment.sh ../../data/quota_sweep.csv
```

Expected outputs:

```text
models/model_g.joblib
models/model_h.joblib
```

This command runs without a VM because it only trains from a CSV. It will fail if the CSV is missing or does not contain the required columns.

## 4. Original Experiment Scripts

The historical scripts are kept for provenance:

```bash
python3 generate_modelG_any.py
python3 generate_modelH_any.py
python3 evaluate_modelG_any.py
python3 evaluate_modelH_any.py
```

Those scripts still contain original dataset/model path assumptions. For a public reproducible entrypoint, prefer `run_paper_experiment.sh`.

## 5. VM Connection

Quota sweep and measurement helpers are under `collect/`.

```text
collect/collect.sh    sweeps quota values and collects vnstat/pidstat logs
collect/run.sh        runs one quota-specific measurement sequence
collect/set_quota.sh  writes the quota to host cgroup cpu.max
collect/netperf.py    helper for netperf-based evaluation
```

The VM-connected workflow is:

```text
1. Write a CPU quota to CPU_CGROUP_PATH on the host
2. SSH into the VM
3. Run netperf or the configured workload script inside the VM
4. Measure throughput, PPS, and CPU usage from the host
5. Convert the measurements into a CSV and train Model-G/Model-H
```

Private values must live in `.env` only.

```bash
cp ../../configs/.env.example ../../.env
```

Required variables usually include:

```text
VM_HOST
VM_USER
VM_SSH_KEY
VM_WORKLOAD_SCRIPT
NET_IFACE
CPU_CGROUP_PATH
```

## 6. Baselines

`tc/` and `share/` are baseline experiment helpers.

```text
tc/      traffic-control bandwidth limiting baseline
share/   CPU share/priority baseline
```

These baselines depend strongly on the host configuration and should be treated as environment-specific scripts.

## 7. Cleanup Notes

The following files or folders were removed because they were temporary tests, duplicated code, external repository copies, or unrelated to the paper reproduction path:

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

`b.py` was renamed to `predict_single_quota.py`.
