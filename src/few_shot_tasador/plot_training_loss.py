import matplotlib.pyplot as plt
import numpy as np
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--exp', type=str, default='default')  # experiment name
opt = parser.parse_args()
opt.exp = 'experiments/exp-' + opt.exp

with open(opt.exp + '/train_loss.txt') as f:
	loss = [float(line.rstrip()) for line in f]

with open(opt.exp + '/train_mape.txt') as f:
	mape = [float(line.rstrip()) for line in f]

i = 0
moving_averages = []
window_size = 10
while i < len(loss) - window_size + 1:
    window_average = round(np.sum(loss[i:i+window_size]) / window_size, 2)

    moving_averages.append(window_average)
    i += 1

plt.plot(loss, label="Loss")
plt.plot(mape, label="MAPE")
plt.plot(moving_averages, label="Loss (moving avg)")
plt.legend()
plt.show()

with open(opt.exp + '/train_loss_per_epoch.txt') as f:
    loss = [float(line.rstrip()) for line in f]

with open(opt.exp + '/train_mape_per_epoch.txt') as f:
    mape = [float(line.rstrip()) for line in f]

plt.plot(loss, label="Loss")
plt.plot(mape, label="MAPE")
plt.legend()
plt.show()