#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -f "$repo_root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$repo_root/.env"
  set +a
fi

: "${CPU_CGROUP_PATH:?CPU_CGROUP_PATH is required}"
period="${CPU_CFS_PERIOD_US:-100000}"
state_file="${1:-set_cpu.txt}"

if [[ ! -f "$state_file" ]]; then
  echo "100000" > "$state_file"
fi

while true; do
  quota="$(cat "$state_file")"
  echo "$quota"
  printf "%s %s\n" "$quota" "$period" | sudo tee "$CPU_CGROUP_PATH" >/dev/null
  sleep 1
done
