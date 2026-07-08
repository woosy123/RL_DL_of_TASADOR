from utils import *
from params import *
from snail import SnailFewShot, SnailFewShotOnSizeless, Sizeless, RNNFewShot
from torchmetrics import MeanAbsolutePercentageError
import argparse
import torch
from torch.autograd import Variable
import torch.nn as nn
import numpy as np
from tqdm import tqdm
import os


mean_abs_percentage_error = MeanAbsolutePercentageError()

def init_model(opt):
    # X-shot regression: num_cls = 1, num_shots = X
    num_features = NUM_FEATURES_PER_SHOT * opt.num_shots + NUM_CONFIG_PARAMS
    print('Total number of features:', num_features)
    if opt.skip_embedding:
        num_features = getattr(opt, 'num_features_override',
                            NUM_FEATURES_PER_SHOT * opt.num_shots + NUM_CONFIG_PARAMS)
        print('Initializing Sizeless model...')
        model = Sizeless(num_features)
    elif opt.sizeless:
        # SNAIL + sizeless
        print('Initializing SNAIL-based meta-learning model on Sizeless...')
        model = SnailFewShotOnSizeless(opt.num_cls, opt.num_shots, opt.dataset, use_cuda=opt.cuda)
    elif opt.rnn:
        # RNN + fully-connected NN
        print('Initializing RNN-based meta-learning model...')
        model = RNNFewShot(opt.num_cls, opt.num_shots, opt.dataset, use_cuda=opt.cuda)
    else:
        # SNAIL + fully-connected NN
        print('Initializing SNAIL-based meta-learning model...')
        model = SnailFewShot(opt.num_cls, opt.num_shots, opt.dataset, use_cuda=opt.cuda)
    model = model.cuda() if opt.cuda else model
    return model

def save_list_to_file(path, thelist):
    with open(path, 'w') as f:
        for item in thelist:
            f.write("%s\n" % item)

def batch_for_few_shot(opt, x, y):
    last_targets = []
    for i in range(opt.batch_size):
        last_targets.append(y[i])
    last_targets = Variable(torch.Tensor(last_targets).float())
    y = torch.Tensor([y.tolist()])
    x, y = Variable(x), Variable(y)
    if opt.cuda:
        x, y = x.cuda(), y.cuda()
        last_targets = last_targets.cuda()
    return x, y, last_targets

def get_mape(last_model, last_targets):
    mape = mean_abs_percentage_error(last_model, last_targets)
    return mape.item()

def train(opt, tr_dataloader, model, optim, val_dataloader=None):
    if opt.cuda:
        mean_abs_percentage_error.to('cuda')
    if val_dataloader is None:
        best_state = None
    train_loss = []
    train_mape = []
    val_loss = []
    val_mape = []
    best_mape = 100

    train_loss_per_epoch = []
    train_mape_per_epoch = []

    best_model_path = os.path.join(opt.exp, 'best_model.pth')
    last_model_path = os.path.join(opt.exp, 'last_model.pth')

    loss_fn = nn.MSELoss()

    for epoch in range(opt.epochs):
        print('=== Epoch: {} ==='.format(epoch))
        tr_iter = iter(tr_dataloader)
        model.train()
        model = model.cuda() if opt.cuda else model
        for batch in tqdm(tr_iter):
            optim.zero_grad()
            x, y = batch
            x, y, last_targets = batch_for_few_shot(opt, x, y)
            model_output = model(x, y)
            last_model = model_output[:, -1, :].squeeze(0)
            loss = loss_fn(last_model, last_targets)
            loss.backward()
            optim.step()
            train_loss.append(loss.item())
            train_mape.append(get_mape(last_model, last_targets))
        avg_loss = np.mean(train_loss[-opt.iterations:])
        avg_mape = np.mean(train_mape[-opt.iterations:])
        print('Avg Train Loss: {}, Avg Train MAPE: {}'.format(avg_loss, avg_mape))
        train_loss_per_epoch.append(avg_loss)
        train_mape_per_epoch.append(avg_mape)

        if val_dataloader is None:
            continue
        val_iter = iter(val_dataloader)
        model.eval()
        for batch in val_iter:
            x, y = batch
            x, y, last_targets = batch_for_few_shot(opt, x, y)
            model_output = model(x, y)
            last_model = model_output[:, -1, :].squeeze(0)
            loss = loss_fn(last_model, last_targets)
            val_loss.append(loss.item())
            val_mape.append(get_mape(last_model, last_targets))
        avg_loss = np.mean(val_loss[-opt.iterations:])
        avg_mape = np.mean(val_mape[-opt.iterations:])
        postfix = ' (Best)' if avg_mape <= best_mape else ' (Best: {})'.format(best_mape)
        print('Avg Val Loss: {}, Avg Val MAPE: {}{}'.format(avg_loss, avg_mape, postfix))
        if avg_mape <= best_mape:
            torch.save(model.state_dict(), best_model_path)
            best_mape = avg_mape
            best_state = model.state_dict()
        for name in ['train_loss', 'train_mape', 'val_loss', 'val_mape', 'train_loss_per_epoch', 'train_mape_per_epoch']:
            save_list_to_file(os.path.join(opt.exp, name + '.txt'), locals()[name])

    torch.save(model.state_dict(), last_model_path)

    return best_state, best_mape, train_loss, train_mape, val_loss, val_mape, train_loss_per_epoch, train_mape_per_epoch

def test(opt, test_dataloader, model):
    avg_mape = list()
    for epoch in range(10):
        test_iter = iter(test_dataloader)
        for batch in test_iter:
            x, y = batch
            x, y, last_targets = batch_for_few_shot(opt, x, y)
            model_output = model(x, y)
            last_model = model_output[:, -1, :].squeeze(0)
            avg_mape.append(get_mape(last_model, last_targets))
    avg_mape = np.mean(avg_mape)
    print('Test Avg MAPE: {}'.format(avg_mape))

    return avg_mape

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', type=str, default='default')  # experiment name
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--iterations', type=int, default=10000)
    parser.add_argument('--dataset', type=str, default='tasador')
    parser.add_argument('--num_cls', type=int, default=1)
    parser.add_argument('--num_shots', type=int, default=5)
    parser.add_argument('--lr', type=float, default=0.0001)
    parser.add_argument('--decay', type=float, default=0)
    parser.add_argument('--batch_size', type=int, default=1)
    parser.add_argument('--sizeless', action='store_true')
    parser.add_argument('--rnn', action='store_true')
    parser.add_argument('--skip_embedding', action='store_true')
    parser.add_argument('--cuda', action='store_true')

    parser.add_argument('--data_root', type=str, default='.')
    parser.add_argument('--train_csv', type=str, default='tasador_dataset.csv')
    parser.add_argument('--test_csv', type=str, default='tasador_config2.csv')

    parser.add_argument(
        '--support_strategy',
        type=str,
        default='uniform',
        choices=['uniform', 'quota_linspace', 'edge_median'],
        help="Support selection within each group. 'uniform' = evenly spaced in sorted order."
    )
    parser.add_argument(
        '--query_strategy',
        type=str,
        default='uniform',
        choices=['uniform', 'random'],
        help="Query selection strategy among non-support samples."
    )
    parser.add_argument(
        '--max_queries_per_group',
        type=int,
        default=None,
        help="Limit number of query samples per group (None = use all)."
    )

    options = parser.parse_args()

    print("[INFO] support_strategy:", options.support_strategy,
          "| query_strategy:", options.query_strategy,
          "| max_queries_per_group:", options.max_queries_per_group)

    options.exp = 'experiments/exp-' + options.exp

    if not os.path.exists(options.exp):
        os.makedirs(options.exp)
    else:
        print('Experiment exist! Please rename the experiment name.')
        exit()

    if torch.cuda.is_available() and not options.cuda:
        print("WARNING: You have a CUDA device, so you should probably run with --cuda")

    print('Initializing the', options.dataset, 'dataset...')
    tr_dataloader, val_dataloader, test_dataloader, _ = init_dataset(options)
    print('Dataset initialized!')

    if options.dataset == 'tasador' and options.skip_embedding:
        sample_x, _ = next(iter(tr_dataloader))
        options.num_features_override = int(sample_x.shape[-1])

    model = init_model(options)
    optim = torch.optim.Adam(params=model.parameters(), lr=options.lr, weight_decay=options.decay)
    res = train(opt=options,
                tr_dataloader=tr_dataloader,
                val_dataloader=val_dataloader,
                model=model,
                optim=optim)

    best_state, best_mape, train_loss, train_mape, val_loss, val_mape, train_loss_per_epoch, train_mape_per_epoch = res
    print('Testing with last model..')
    test(opt=options,
         test_dataloader=test_dataloader,
         model=model)

    if best_state is not None:
        model.load_state_dict(best_state)
        print('Testing with best model..')
        test(opt=options,
             test_dataloader=test_dataloader,
             model=model)
    else:
        print("[WARN] best_state is None (val_dataloader is None). Skipping best-model test.")

if __name__ == '__main__':
    main()