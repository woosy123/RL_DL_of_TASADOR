#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"

if [[ -f "$repo_root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$repo_root/.env"
  set +a
fi

if [[ ! -f "$script_dir/set_cpu.txt" ]]; then
  echo "100000" > "$script_dir/set_cpu.txt"
fi

cd "$script_dir"
python3 DQN1.py
