#!/usr/bin/env bash

printf ">>> TASADOR training sweep\n"

printf "\n>>> support_strategy = uniform, netperf only(config3 8v), original \n"
printf "\n3-shot training:\n"
python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=uniform --exp=tasador-uniform-3s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv
printf "\n4-shot training:\n"
python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=uniform --exp=tasador-uniform-4s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv
printf "\n5-shot training:\n"
python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=uniform --exp=tasador-uniform-5s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv
printf "\n6-shot training:\n"
python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=uniform --exp=tasador-uniform-6s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv
printf "\n7-shot training:\n"
python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=uniform --exp=tasador-uniform-7s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv

printf "\n>>> support_strategy = quota_linspace,  netperf only(config3 8v), original \n"
printf "\n3-shot training:\n"
python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=quota_linspace --exp=tasador-qlin-3s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv
printf "\n4-shot training:\n"
python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=quota_linspace --exp=tasador-qlin-4s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv
printf "\n5-shot training:\n"
python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=quota_linspace --exp=tasador-qlin-5s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv
printf "\n6-shot training:\n" 
python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=quota_linspace --exp=tasador-qlin-6s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv
printf "\n7-shot training:\n"
python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=quota_linspace --exp=tasador-qlin-7s-config3 --cuda --train_csv tasador_wo_config3_8v.csv --test_csv tasador_config3_8v.csv

# printf "\n>>> support_strategy = uniform, netperf only, trimmed \n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=uniform --exp=tasador-uniform-3s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=uniform --exp=tasador-uniform-4s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=uniform --exp=tasador-uniform-5s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv
# printf "\n6-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=uniform --exp=tasador-uniform-6s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=uniform --exp=tasador-uniform-7s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv

# printf "\n>>> support_strategy = quota_linspace, netperf only, trimmed \n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=quota_linspace --exp=tasador-qlin-3s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=quota_linspace --exp=tasador-qlin-4s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=quota_linspace --exp=tasador-qlin-5s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv
# printf "\n6-shot training:\n" 
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=quota_linspace --exp=tasador-qlin-6s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=quota_linspace --exp=tasador-qlin-7s-trimmed --cuda --train_csv tasador_dataset_trimmed.csv --test_csv tasador_config2.csv


# printf "\n>>> support_strategy = uniform, netperf only, notrimmed \n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=uniform --exp=tasador-uniform-3s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=uniform --exp=tasador-uniform-4s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=uniform --exp=tasador-uniform-5s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv
# printf "\n6-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=uniform --exp=tasador-uniform-6s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=uniform --exp=tasador-uniform-7s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv

# printf "\n>>> support_strategy = quota_linspace, netperf only, notrimmed \n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=quota_linspace --exp=tasador-qlin-3s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=quota_linspace --exp=tasador-qlin-4s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=quota_linspace --exp=tasador-qlin-5s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv
# printf "\n6-shot training:\n" 
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=quota_linspace --exp=tasador-qlin-6s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=quota_linspace --exp=tasador-qlin-7s-notrimmed --cuda --train_csv tasador_dataset_notrimmed.csv --test_csv tasador_config2.csv

# printf "\n>>> support_strategy = uniform, netperf only, original \n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=uniform --exp=tasador-uniform-3s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=uniform --exp=tasador-uniform-4s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=uniform --exp=tasador-uniform-5s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv
# printf "\n6-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=uniform --exp=tasador-uniform-6s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=uniform --exp=tasador-uniform-7s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv

# printf "\n>>> support_strategy = quota_linspace, netperf only, original \n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=quota_linspace --exp=tasador-qlin-3s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=quota_linspace --exp=tasador-qlin-4s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=quota_linspace --exp=tasador-qlin-5s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv
# printf "\n6-shot training:\n" 
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=quota_linspace --exp=tasador-qlin-6s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=quota_linspace --exp=tasador-qlin-7s-original --cuda --train_csv tasador_dataset_original.csv --test_csv tasador_config2.csv


# printf "\n>>> support_strategy = uniform, netperf + memcached(tasador_wo_web) \n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=uniform --exp=tasador-uniform-3s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=uniform --exp=tasador-uniform-4s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=uniform --exp=tasador-uniform-5s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv
# printf "\n6-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=uniform --exp=tasador-uniform-6s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=uniform --exp=tasador-uniform-7s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv

# printf "\n>>> support_strategy = quota_linspace, netperf + memcached(tasador_wo_web) \n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=quota_linspace --exp=tasador-qlin-3s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=quota_linspace --exp=tasador-qlin-4s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=quota_linspace --exp=tasador-qlin-5s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv
# printf "\n6-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=quota_linspace --exp=tasador-qlin-6s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=quota_linspace --exp=tasador-qlin-7s-noweb --cuda --train_csv tasador_wo_web.csv --test_csv tasador_web.csv

# printf "\n>>> support_strategy = uniform, netperf + memcached(tasador_wo_web) + original\n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=uniform --exp=tasador-uniform-3s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=uniform --exp=tasador-uniform-4s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=uniform --exp=tasador-uniform-5s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv
# printf "\n6-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=uniform --exp=tasador-uniform-6s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=uniform --exp=tasador-uniform-7s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv

# printf "\n>>> support_strategy = quota_linspace, netperf + memcached(tasador_wo_web) + original\n"
# printf "\n3-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=3 --support_strategy=quota_linspace --exp=tasador-qlin-3s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv
# printf "\n4-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=4 --support_strategy=quota_linspace --exp=tasador-qlin-4s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv
# printf "\n5-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=5 --support_strategy=quota_linspace --exp=tasador-qlin-5s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv
# printf "\n6-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=6 --support_strategy=quota_linspace --exp=tasador-qlin-6s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv
# printf "\n7-shot training:\n"
# python3 train.py --dataset=tasador --rnn --num_shots=7 --support_strategy=quota_linspace --exp=tasador-qlin-7s-noweb-original --cuda --train_csv tasador_wo_web_original.csv --test_csv tasador_web.csv