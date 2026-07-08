# Reproduction Notes

This repository is intended to document and cleanly reproduce the experiment methodology without publishing private infrastructure details.

## Required Local Setup

- Linux host with KVM/libvirt
- VM running the target workload
- host-side permission to update the relevant cgroup CPU quota
- `vnstat`, `pidstat`, `mpstat`
- Python 3.10+
- PyTorch for MLP/RL
- scikit-learn for Random Forest

## Recommended Environment Setup

```bash
cp configs/.env.example .env
# Fill .env locally. Do not commit it.
```

## Recommended Data Policy

Commit only:

- cleaned sample CSVs
- schema documentation
- plotting scripts
- sanitized reproduction scripts

Do not commit:

- raw logs with hostnames or private paths
- VM IPs
- usernames
- passwords
- `.env`
- large generated datasets
- model checkpoints unless intentionally released

## Suggested Experiment Order

For detailed commands, see [07-experiment-runbook.md](07-experiment-runbook.md).

1. Collect quota sweep data.
2. Train Random Forest models.
3. Train MLP regression model.
4. Evaluate predicted quotas on the VM.
5. Run DQN only after the collection/evaluation loop is stable.
6. Compare normalized bandwidth:

```text
normalized_bandwidth = measured_throughput / target_throughput
```

## Known Cleanup Tasks Before Publication

- Replace all hardcoded paths with CLI arguments.
- Replace password SSH with key-based SSH.
- Save scalers with trained models.
- Add a `requirements.txt` or `pyproject.toml`.
- Add small anonymized sample data under `data/sample/`.
- Add plots for RMSE, normalized bandwidth, and training time.
