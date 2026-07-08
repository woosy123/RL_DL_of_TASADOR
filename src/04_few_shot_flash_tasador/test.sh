#!/usr/bin/env bash
set -euo pipefail

mkdir -p test_logs

printf ">>> TASADOR test sweep\n"

run_test () {
  local num_shots="$1"
  local support_strategy="$2"
  local exp_name="$3"
  local train_csv="$4"
  local test_csv="$5"

  printf "\n>>> TEST | exp=%s | shots=%s | strategy=%s\n" \
    "$exp_name" "$num_shots" "$support_strategy"
  printf "    train_csv=%s | test_csv=%s\n" "$train_csv" "$test_csv"

  python3 test.py \
    --dataset=tasador \
    --rnn \
    --num_shots="$num_shots" \
    --support_strategy="$support_strategy" \
    --exp="$exp_name" \
    --cuda \
    --train_csv "$train_csv" \
    --test_csv "$test_csv" \
    2>&1 | tee "test_logs/${exp_name}.log"
}
for shots in 3 4 5 6 7; do
  run_test "$shots" uniform         "tasador-uniform-${shots}s-config3"         "tasador_wo_config3_8v.csv"      "tasador_config3_8v.csv"
done
for shots in 3 4 5 6 7; do
  run_test "$shots" quota_linspace         "tasador-qlin-${shots}s-config3"         "tasador_wo_config3_8v.csv"      "tasador_config3_8v.csv"
done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" uniform         "tasador-uniform-${shots}s-trimmed"         "tasador_dataset_trimmed.csv"      "tasador_config2.csv"
# done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" quota_linspace  "tasador-qlin-${shots}s-trimmed"            "tasador_dataset_trimmed.csv"      "tasador_config2.csv"
# done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" uniform         "tasador-uniform-${shots}s-notrimmed"       "tasador_dataset_notrimmed.csv"    "tasador_config2.csv"
# done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" quota_linspace  "tasador-qlin-${shots}s-notrimmed"          "tasador_dataset_notrimmed.csv"    "tasador_config2.csv"
# done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" uniform         "tasador-uniform-${shots}s-original"        "tasador_dataset_original.csv"     "tasador_config2.csv"
# done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" quota_linspace  "tasador-qlin-${shots}s-original"           "tasador_dataset_original.csv"     "tasador_config2.csv"
# done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" uniform         "tasador-uniform-${shots}s-noweb"           "tasador_wo_web.csv"               "tasador_web.csv"
# done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" quota_linspace  "tasador-qlin-${shots}s-noweb"              "tasador_wo_web.csv"               "tasador_web.csv"
# done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" uniform         "tasador-uniform-${shots}s-noweb-original"  "tasador_wo_web_original.csv"      "tasador_web.csv"
# done

# for shots in 3 4 5 6 7; do
#   run_test "$shots" quota_linspace  "tasador-qlin-${shots}s-noweb-original"     "tasador_wo_web_original.csv"      "tasador_web.csv"
# done

printf "\n>>> all tests done\n"