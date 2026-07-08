# Source Script Structure

This directory contains sanitized source scripts from the original experiments. Datasets, checkpoints, raw logs, virtual environments, and generated result files are intentionally excluded.

## Directory Map

```text
src/
├── random_forest_tasador/
│   ├── generate_modelG_any.py
│   ├── generate_modelH_any.py
│   ├── evaluate_modelG_any.py
│   ├── evaluate_modelH_any.py
│   ├── run_model.sh
│   ├── test/
│   ├── share/
│   ├── tc/
│   ├── dynamic/
│   └── legacy/supporting scripts
├── mlp_regression/
│   ├── regression_dl.py
│   ├── predict_cpu_quota.py
│   ├── predict_netperf.py
│   ├── netperf.py
│   ├── set_cpu.sh
│   ├── netperf.sh
│   └── get_vnstat.sh
├── rl_dqn/
│   ├── DQN1.py
│   ├── env_dqn.py
│   ├── script2.py
│   ├── script8vcpu.py
│   ├── set_cpu.sh
│   ├── cpu_usage.sh
│   └── script/
└── few_shot_tasador/
    ├── train.py
    ├── test.py
    ├── eval.py
    ├── tasador_dataset.py
    ├── snail.py
    ├── blocks.py
    ├── params.py
    └── reproduce.sh
```

## Sanitization

The copied scripts were sanitized before publication:

- real host/IP values were replaced with placeholders such as `${VM_HOST}` and `${VM_OR_TARGET_HOST}`
- usernames were replaced with `${VM_USER}` or `${REMOTE_USER}`
- private filesystem paths were replaced with `${EXPERIMENT_ROOT}` or `${LOCAL_WORKSPACE}`
- cgroup paths were replaced with `${CPU_CGROUP_PATH}`
- password-based SSH commands were converted to SSH-key placeholders where practical

These scripts preserve the original experiment flow, but they may not run directly without adapting `.env` and local infrastructure paths.

## Relationship To `scripts/`

- `src/`: historical/sanitized experiment scripts, kept for transparency.
- `scripts/`: cleaned templates intended as safer starting points for reproduction.

