#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   CPU_CGROUP_PATH=/sys/fs/cgroup/.../cpu.max ./apply_cpu_quota.sh 50000
#
# This script intentionally contains no real cgroup path.

quota="${1:?usage: apply_cpu_quota.sh <quota>}"
period="${CPU_CFS_PERIOD_US:-100000}"
cgroup_path="${CPU_CGROUP_PATH:?CPU_CGROUP_PATH is required}"

if [[ ! -w "$cgroup_path" ]]; then
  echo "cgroup path is not writable: $cgroup_path" >&2
  exit 1
fi

printf "%s %s\n" "$quota" "$period" > "$cgroup_path"
echo "applied quota=$quota period=$period to $cgroup_path"

