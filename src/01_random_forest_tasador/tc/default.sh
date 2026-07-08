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
PERF=`expr $S \* 1024`
: "${TRAFFIC_SHAPER_CMD:?TRAFFIC_SHAPER_CMD is required for tc baseline}"

#sudo tcset virbr0 --rate "$S"Mbps --src-network ${VM_OR_TARGET_HOST}/32 --direction incoming
sudo "$TRAFFIC_SHAPER_CMD" -a virbr0 -d "$PERF"
for i in $(seq 1 5)
do
	sudo ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o stricthostkeychecking=no ${VM_USER}@${VM_HOST} "${VM_WORKLOAD_SCRIPT:-~/test.sh} 8 $M" &
	vnstat -i ${NET_IFACE} -tr 5 >> vn_"$M"_"$S".txt &
	mpstat 5 1 >> mp_"$M"_"$S".txt &
	pidstat -p $VM,$VHOST -I 5 1 >> pid_"$M"_"$S".txt
	sleep 5
done
#sudo tcdel virbr0 --all
sudo "$TRAFFIC_SHAPER_CMD" -c -a virbr0
