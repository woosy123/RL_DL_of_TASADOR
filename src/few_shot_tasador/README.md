# Case Study 1: Resource Config Search for MultiCloud

Category: Meta-learning for Supervised Learning in Regression Tasks

## MultiCloud Dataset

Path: `../training-data-multi-cloud-config-search/dataset_normalized.csv`

This dataset consists of the runtime resource metrics, appilcation metrics, and costs for 30 datacenter applications deployed in different cloud providers.
Each of the 30 workloads was deployed on a variety of different configurations across three different cloud providers: Amazon Web Services (AWS), Microsoft Azure and Google Cloud Platform (GCP).
For AWS, the authors generated 24 different configurations by varying the cluster size, together with the family and size options.
For Azure, they varied family, `cpu_size` together with the cluster size to generate 16 different configurations.
Finally, for GCP, they generated 48 different configurations by varying the cluster size, family, type and vcpu.
This resulted in a total of 88 different multi-cloud configurations.

## Requirement

- Python 3.8.8
- Packages listed in `requirements.txt`

## Training

To start training:

```
# embedding + fully-connected neural network -> latency
python3 train.py --dataset=multicloud                # default: 2-shots/samples
python3 train.py --dataset=multicloud --num_shots=6  # 6-shots/samples

# embedding + sizeless neural network architecture -> latency
python3 train.py --dataset=multicloud --sizeless --decay=0.01

# embedding + fully-connected neural network (with L2 regularization) -> latency
python3 train.py --dataset=multicloud --decay=0.01

# embedding + sizeless neural network architecture (without L2 regularization) -> latency
python3 train.py --dataset=multicloud --sizeless

# RNN embedding (with 4 samples) + fully-connected neural network -> latency
python3 train.py --dataset=multicloud --rnn --num_shots=4
```

## Evaluation

To evaluated the trained model on a new dataset with the same other flags used in the training:

```
# use --exp to specify the folder where the trained model is located at
python3 eval.py [--dataset=multicloud --rnn --num_shots=4] --exp=experiment-name
```

## Visualization

To visualize the training process:

```
# use --exp to specify the folder where the training loss log data is located at
python3 plot_training_loss.py --exp=experiment-name
```
