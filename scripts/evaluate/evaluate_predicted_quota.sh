#!/usr/bin/env bash
set -euo pipefail

# Sanitized evaluation template.
# Reads quota predictions and evaluates them by applying each quota to the VM.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -f "$repo_root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$repo_root/.env"
  set +a
fi

predictions_csv="${1:?usage: evaluate_predicted_quota.sh <predictions.csv>}"

: "${VM_HOST:?VM_HOST is required}"
: "${VM_USER:?VM_USER is required}"
: "${VM_SSH_KEY:?VM_SSH_KEY is required}"
: "${TARGET_HOST:?TARGET_HOST is required}"
: "${NET_IFACE:?NET_IFACE is required}"
: "${RESULT_DIR:=./results}"

mkdir -p "$RESULT_DIR"
out="$RESULT_DIR/evaluation.csv"
echo "target_throughput,message_size,cpu_quota,measured_throughput" > "$out"

tail -n +2 "$predictions_csv" | while IFS=, read -r target_throughput message_size cpu_quota; do
  "$repo_root/scripts/collect/apply_cpu_quota.sh" "$cpu_quota"
  sleep 2

  ssh -i "$VM_SSH_KEY" -p "${VM_SSH_PORT:-22}" \
    -o StrictHostKeyChecking=accept-new \
    "$VM_USER@$VM_HOST" \
    "netperf -H '$TARGET_HOST' -l '${WORKLOAD_DURATION_SEC:-30}' -- -m '$message_size'" &

  measured="$(vnstat -i "$NET_IFACE" -tr 5 | awk '/tx/ {print $2; exit}')"
  echo "$target_throughput,$message_size,$cpu_quota,$measured" >> "$out"
done

echo "wrote $out"

