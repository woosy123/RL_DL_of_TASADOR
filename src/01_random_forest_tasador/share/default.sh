#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
if [[ -f "$repo_root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$repo_root/.env"
  set +a
fi

M=$1
S=$2
VM=`pgrep qemu`
VHOST=`pgrep vhost`
DIR="${EXPERIMENT_ROOT:-.}"
: "${CPU_CGROUP_PATH:?CPU_CGROUP_PATH is required}"
printf "%s %s\n" "$S" "${CPU_CFS_PERIOD_US:-100000}" | sudo tee "$CPU_CGROUP_PATH" >/dev/null
sudo ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o stricthostkeychecking=no ${VM_USER}@${VM_HOST} "${VM_WORKLOAD_SCRIPT:-~/test.sh} 55 $M"     &
for i in $(seq 1 5)
do
	vnstat -i ${NET_IFACE} -tr 10 >> $DIR/vn_"$M"_"$S".txt &
	mpstat 10 1 >> $DIR/mp_"$M"_"$S".txt &
	pidstat -p $VM,$VHOST -I 10 1 >> $DIR/pid_"$M"_"$S".txt
done
sleep 10
