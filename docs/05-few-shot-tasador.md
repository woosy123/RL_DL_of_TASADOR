# Few-Shot / Meta-Learning Extension

The few-shot experiments use a separate TASADOR case-study code path. This is not the original Random Forest TASADOR pipeline. It is an exploratory meta-learning extension that uses TASADOR-style collected data to test whether CPU quota prediction can be done from only a few support measurements.

## Why This Is Not Random Forest TASADOR

Random Forest TASADOR learns a fixed supervised regression model from a collected dataset:

```text
message_size, throughput, PPS, VM CPU usage -> CPU quota
```

Few-shot learning asks a different question:

```text
Given only K support measurements from a new workload/config,
can the model infer the CPU quota for another query point?
```

In other words, the support set becomes part of the input. A standard Random Forest does not naturally adapt to a new support set at inference time. It can be forced into a baseline by flattening support samples into a long feature vector, but that makes the model sensitive to support order, fixed K, and weak at context adaptation. That is why this experiment uses sequence/context models such as SNAIL and RNN/GRU.

## Extended Dataset

```csv
workload,vcpu,cpu_model,mem_gb,nic_gbps,switch_gbps,cpu_quota,message_size,network_throughput,packet_per_sec,vm_cpu_usage
```

## Grouping

Rows are grouped by:

```text
workload
vcpu
cpu_model
mem_gb
nic_gbps
switch_gbps
message_size
```

Within each group, rows are sorted by `cpu_quota`.

## Support And Query Construction

For each group:

1. Select `K` support samples.
2. Remove support samples from the query candidates.
3. For each query row, build one supervised training example.

Each support sample contributes:

```text
message_size
network_throughput
packet_per_sec
vm_cpu_usage
vcpu
cpu_model_id
mem_gb
nic_gbps
switch_gbps
support_cpu_quota
```

The query contributes the same features except `cpu_quota`. The target is the query row's CPU quota.

## Models

- `SnailFewShot`: attention + temporal convolution + fully connected layers
- `RNNFewShot`: bidirectional GRU + fully connected layers
- `Sizeless`: plain fully connected baseline

## Important Distinction

This experiment does not directly control a VM during training. It is an offline regression/meta-learning experiment over previously collected CSV data. Its goal is to reduce future data collection cost, not to replace the main Random Forest TASADOR pipeline directly.
