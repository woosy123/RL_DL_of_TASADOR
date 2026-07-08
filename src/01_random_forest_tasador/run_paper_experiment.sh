#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"

csv_path="${1:-${TASADOR_DATASET:-}}"
if [[ -z "$csv_path" ]]; then
  echo "usage: ./run_paper_experiment.sh <quota_sweep.csv>"
  echo "example: ./run_paper_experiment.sh ../../data/quota_sweep.csv"
  exit 1
fi

mkdir -p "$script_dir/models"

python3 "$repo_root/scripts/train/train_random_forest.py" \
  --csv "$csv_path" \
  --model G \
  --out "$script_dir/models/model_g.joblib"

python3 "$repo_root/scripts/train/train_random_forest.py" \
  --csv "$csv_path" \
  --model H \
  --out "$script_dir/models/model_h.joblib"

echo "saved:"
echo "  $script_dir/models/model_g.joblib"
echo "  $script_dir/models/model_h.joblib"
