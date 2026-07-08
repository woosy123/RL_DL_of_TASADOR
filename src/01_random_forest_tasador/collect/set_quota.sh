#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
if [[ -f "$repo_root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$repo_root/.env"
  set +a
fi

quota="${1:?usage: ./set_quota.sh <quota>}"
period="${CPU_CFS_PERIOD_US:-100000}"
: "${CPU_CGROUP_PATH:?CPU_CGROUP_PATH is required}"

printf "%s %s\n" "$quota" "$period" | sudo tee "$CPU_CGROUP_PATH" >/dev/null
