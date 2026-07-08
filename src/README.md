# Source Experiment Order

`src/` contains the cleaned, sanitized experiment folders. Each folder has its own `README.md`, so the execution flow can be read next to the code.

```text
src/
├── 01_random_forest_tasador/
├── 02_mlp_regression/
├── 03_rl_dqn/
└── 04_few_shot_flash_tasador/
```

## 1. `01_random_forest_tasador`

TASADOR 논문 방식에 가장 가까운 Random Forest 실험이다. Quota sweep CSV를 이용해 Model-G와 Model-H를 학습한다.

```bash
cd src/01_random_forest_tasador
./run_paper_experiment.sh ../../data/quota_sweep.csv
```

자세한 실행 순서: [01_random_forest_tasador/README.md](01_random_forest_tasador/README.md)

## 2. `02_mlp_regression`

Random Forest 대신 PyTorch MLP로 CPU quota를 예측하는 deep learning baseline이다. hidden layer 수와 epoch 수를 바꾸어가며 RMSE와 training time을 비교했다.

```bash
cd src/02_mlp_regression
./run_paper_experiment.sh ../../data/quota_sweep.csv 1200
```

자세한 실행 순서: [02_mlp_regression/README.md](02_mlp_regression/README.md)

## 3. `03_rl_dqn`

CSV로 미리 학습하는 방식이 아니라, VM workload를 실행한 상태에서 DQN agent가 CPU quota를 step 단위로 조절하는 online control 실험이다.

```bash
cd src/03_rl_dqn
./run_paper_experiment.sh
```

자세한 실행 순서: [03_rl_dqn/README.md](03_rl_dqn/README.md)

## 4. `04_few_shot_flash_tasador`

FLASH 논문 GitHub 코드를 TASADOR quota dataset 형태로 수정한 few-shot/meta-learning 확장 실험이다. Random Forest TASADOR 본 실험은 아니고, 적은 support sample로 새로운 workload/config의 quota curve를 예측할 수 있는지 보는 비교 후보이다.

```bash
cd src/04_few_shot_flash_tasador
./run_paper_experiment.sh tasador_wo_config3_8v.csv tasador_config3_8v.csv
```

자세한 실행 순서: [04_few_shot_flash_tasador/README.md](04_few_shot_flash_tasador/README.md)

## Sanitization

- datasets, checkpoints, raw logs, virtual environments, generated results are excluded
- hostnames, IP addresses, usernames, private paths, and cgroup paths are replaced with environment variables
- `.env` must stay private; use `configs/.env.example` as a template
