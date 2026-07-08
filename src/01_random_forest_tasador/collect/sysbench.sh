#!/bin/sh
docker exec c2 sysbench --time=120 cpu --cpu-max-prime=100000 run &
docker exec c1 sysbench --time=120 cpu --cpu-max-prime=100000 run
