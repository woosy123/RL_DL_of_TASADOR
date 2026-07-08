#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"

csv_path="${1:-${MLP_DATASET:-}}"
epochs="${2:-${MLP_EPOCHS:-800}}"

if [[ -z "$csv_path" ]]; then
  echo "usage: ./run_paper_experiment.sh <quota_sweep.csv> [epochs]"
  echo "example: ./run_paper_experiment.sh ../../data/quota_sweep.csv 1200"
  exit 1
fi

mkdir -p "$script_dir/models"

python3 "$repo_root/scripts/train/train_mlp.py" \
  --csv "$csv_path" \
  --epochs "$epochs" \
  --out "$script_dir/models/mlp_quota.pt"

echo "saved:"
echo "  $script_dir/models/mlp_quota.pt"
