# Source Experiment Order

`src/` contains the cleaned and sanitized experiment folders. Each numbered folder has its own `README.md`, so the execution flow can be read next to the code.

```text
src/
├── 01_random_forest_tasador/
├── 02_mlp_regression/
├── 03_rl_dqn/
└── 04_few_shot_flash_tasador/
```

## 1. `01_random_forest_tasador`

This is the closest folder to the TASADOR paper workflow. It trains Model-G and Model-H from a quota-sweep CSV.

```bash
cd src/01_random_forest_tasador
./run_paper_experiment.sh ../../data/quota_sweep.csv
```

Runbook: [01_random_forest_tasador/README.md](01_random_forest_tasador/README.md)

## 2. `02_mlp_regression`

This is a PyTorch MLP baseline for CPU quota regression. It compares the effect of hidden-layer structure and epoch count on RMSE and training time.

```bash
cd src/02_mlp_regression
./run_paper_experiment.sh ../../data/quota_sweep.csv 1200
```

Runbook: [02_mlp_regression/README.md](02_mlp_regression/README.md)

## 3. `03_rl_dqn`

This is an online DQN control experiment. Instead of training only from a CSV, the agent interacts with the VM workload and changes CPU quota step by step.

```bash
cd src/03_rl_dqn
./run_paper_experiment.sh
```

Runbook: [03_rl_dqn/README.md](03_rl_dqn/README.md)

## 4. `04_few_shot_flash_tasador`

This folder adapts the FLASH paper code to TASADOR-style quota data. It is not the main Random Forest TASADOR experiment. It is a few-shot/meta-learning extension that tests whether a model can infer a quota curve for a new workload or configuration from a small support set.

```bash
cd src/04_few_shot_flash_tasador
./run_paper_experiment.sh tasador_wo_config3_8v.csv tasador_config3_8v.csv
```

Runbook: [04_few_shot_flash_tasador/README.md](04_few_shot_flash_tasador/README.md)

## Reproducibility Status

The entrypoint scripts are syntactically checked and designed to run when the required private inputs exist:

- quota-sweep CSV datasets are not included in this public repository
- `.env` must be created from `configs/.env.example`
- VM SSH access, cgroup paths, network interface names, and workload scripts must match the local host
- real VM-connected experiments cannot be executed on a machine that does not have the experiment infrastructure

## Sanitization

- datasets, checkpoints, raw logs, virtual environments, and generated results are excluded
- hostnames, IP addresses, usernames, private paths, and cgroup paths are replaced with environment variables
- `.env` must remain private
