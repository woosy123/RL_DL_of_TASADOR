# Few-Shot TASADOR Experiments

The few-shot experiments use a separate TASADOR case-study code path. This is separate from the original Random Forest TASADOR pipeline. It studies whether a model can infer the CPU quota for a query point after seeing only a few support samples from the same workload/hardware/message-size group.

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

This experiment does not directly control a VM during training. It is an offline regression/meta-learning experiment over previously collected CSV data.
