# pip install --upgrade pip
# pip install op${NET_IFACE}
# pip install pandas
# generate data: input.csv [cpu quota]
PATH=~/Desktop/Inferencing-CPU-for-network-performance-in-virtualized-environments/user-level-cpu-quota-control
python3 $PATH/code/input.py

while read quota
do
    # sudo apt install cgroup-tools
    # quota > cpu.cfs_quota_us
    echo $quota
    #cd ${CPU_CGROUP_PATH}
    cd ${CPU_CGROUP_PATH}
    sudo echo "$quota 100000" > cpu.max
    #sudo cgset -r cpu.cfs_quota_us=$quota machine/qemu-5-test.libvirt-qemu/emulator
    #sed -i "1s/.*/$quota/g" ${CPU_CGROUP_PATH}

    # sudo ssh-keygen -f "/root/.ssh/known_hosts" -R "${VM_OR_TARGET_HOST}"
    # install an SSH helper only if your private environment requires it 
    # netperf command result > output_full.txt
    #ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -oStrictHostKeyChecking=no storage@${VM_OR_TARGET_HOST} "netperf -H ${VM_OR_TARGET_HOST} -l 120 -- -m 1024" > $PATH/data/output_full.txt
    ssh -i "${VM_SSH_KEY:-~/.ssh/id_rsa}" -oStrictHostKeyChecking=no v2@${VM_OR_TARGET_HOST} "netperf -H ${VM_OR_TARGET_HOST} -l 120 -- -m 1024" > $PATH/data/output_full.txt
    # generate data: output.csv [cpu quota, network throughput]
    python3 $PATH/code/output.py $quota
    sleep 1s
done < $PATH/data/input.csv

# graph : output.csv [cpu quota / network throughput]
