#!/usr/bin/env bash
set -euo pipefail

# Sanitized collection template.
# Requires a private .env file or exported environment variables.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -f "$repo_root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$repo_root/.env"
  set +a
fi

: "${VM_HOST:?VM_HOST is required}"
: "${VM_USER:?VM_USER is required}"
: "${VM_SSH_KEY:?VM_SSH_KEY is required}"
: "${TARGET_HOST:?TARGET_HOST is required}"
: "${MESSAGE_SIZE:=64}"
: "${WORKLOAD_DURATION_SEC:=30}"
: "${CPU_QUOTA_MIN:=1000}"
: "${CPU_QUOTA_MAX:=100000}"
: "${CPU_QUOTA_STEP:=1000}"
: "${MEASUREMENT_REPEAT:=3}"
: "${NET_IFACE:?NET_IFACE is required}"
: "${DATA_DIR:=./data}"

mkdir -p "$DATA_DIR"
out="$DATA_DIR/quota_sweep.csv"

if [[ ! -f "$out" ]]; then
  echo "cpu_quota,message_size,network_throughput,packet_per_sec,vm_cpu_usage" > "$out"
fi

for quota in $(seq "$CPU_QUOTA_MIN" "$CPU_QUOTA_STEP" "$CPU_QUOTA_MAX"); do
  "$repo_root/scripts/collect/apply_cpu_quota.sh" "$quota"
  sleep 2

  for _ in $(seq 1 "$MEASUREMENT_REPEAT"); do
    ssh -i "$VM_SSH_KEY" -p "${VM_SSH_PORT:-22}" \
      -o StrictHostKeyChecking=accept-new \
      "$VM_USER@$VM_HOST" \
      "netperf -H '$TARGET_HOST' -l '$WORKLOAD_DURATION_SEC' -- -m '$MESSAGE_SIZE'" &

    # Replace these parsers with the exact local format used by your host.
    network_throughput="$(vnstat -i "$NET_IFACE" -tr 5 | awk '/tx/ {print $2; exit}')"
    packet_per_sec="$(vnstat -i "$NET_IFACE" -tr 5 | awk '/tx/ {print $4; exit}')"
    vm_cpu_usage="$(pidstat 1 1 | awk '/qemu|vhost/ {sum += $8} END {print sum + 0}')"

    echo "$quota,$MESSAGE_SIZE,$network_throughput,$packet_per_sec,$vm_cpu_usage" >> "$out"
    sleep 2
  done
done

echo "wrote $out"

