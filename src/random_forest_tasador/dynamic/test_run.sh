#!/bin/sh

cmd="sh ${REMOTE_EXPERIMENT_ROOT}"
locust --headless -f locustfile.py -u 1024 --processes 24 -H http://${VM_OR_TARGET_HOST} >> locust.log &
ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o StrictHostKeyChecking=no -T -p "${REMOTE_SSH_PORT:-22}" ${REMOTE_USER}@${REMOTE_HOST} $cmd
