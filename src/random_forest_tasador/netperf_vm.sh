#!/bin/bash

num_runs=$1
duration=$2
message_size=$3

for ((i=1; i<=$num_runs; i++)); do
    cmd="netperf -H ${VM_OR_TARGET_HOST} -p 1000$i -l $duration -- -m $message_size"
    ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -o StrictHostKeyChecking=no v2@${VM_OR_TARGET_HOST} $cmd >>netperf_result.txt &
done
