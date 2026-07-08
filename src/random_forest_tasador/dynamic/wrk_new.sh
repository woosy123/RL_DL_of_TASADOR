#!/bin/sh

cmd="sh ${REMOTE_EXPERIMENT_ROOT}"
wrk -t12 -c400 -d30s --latency http://${VM_OR_TARGET_HOST}/index.lighttpd.html >> wrk_1st.log &
ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o StrictHostKeyChecking=no -T -p "${REMOTE_SSH_PORT:-22}" ${REMOTE_USER}@${REMOTE_HOST} $cmd &
sleep 30
wrk -t1 -c1 -d30s --latency http://${VM_OR_TARGET_HOST}/index.lighttpd.html >> wrk_2nd.log
sleep 30
wrk -t1 -c1 -d30s --latency http://${VM_OR_TARGET_HOST}/index.lighttpd.html >> wrk_3rd.log
wrk -t12 -c400 -d30s --latency http://${VM_OR_TARGET_HOST}/index.lighttpd.html >> wrk_4th.log
