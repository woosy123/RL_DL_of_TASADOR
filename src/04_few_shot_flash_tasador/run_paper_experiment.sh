#!/usr/bin/env bash
set -euo pipefail

train_csv="${1:-tasador_wo_config3_8v.csv}"
test_csv="${2:-tasador_config3_8v.csv}"
use_cuda="${USE_CUDA:-1}"
cuda_flag=()

if [[ "$use_cuda" == "1" ]]; then
  cuda_flag=(--cuda)
fi

run_train() {
  local shots="$1"
  local strategy="$2"
  local exp_name="$3"

  python3 train.py \
    --dataset=tasador \
    --rnn \
    --num_shots="$shots" \
    --support_strategy="$strategy" \
    --exp="$exp_name" \
    "${cuda_flag[@]}" \
    --train_csv "$train_csv" \
    --test_csv "$test_csv"
}

for shots in 3 4 5 6 7; do
  run_train "$shots" uniform "tasador-uniform-${shots}s-config3"
done

for shots in 3 4 5 6 7; do
  run_train "$shots" quota_linspace "tasador-qlin-${shots}s-config3"
done

echo "training done. run ./test.sh for evaluation sweep, or run test.py for one exp."
