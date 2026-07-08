import argparse
import os
import torch

from utils import init_dataset
from train import init_model, test


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', type=str, default='default')
    parser.add_argument('--dataset', type=str, default='tasador')
    parser.add_argument('--num_cls', type=int, default=1)

    parser.add_argument('--num_shots', type=int, default=5)

    parser.add_argument('--batch_size', type=int, default=1)
    parser.add_argument('--rnn', action='store_true')
    parser.add_argument('--sizeless', action='store_true')
    parser.add_argument('--skip_embedding', action='store_true')
    parser.add_argument('--cuda', action='store_true')

    parser.add_argument('--data_root', type=str, default='.')
    parser.add_argument('--train_csv', type=str, default='tasador_dataset.csv')
    parser.add_argument('--test_csv', type=str, default='tasador_config2.csv')

    opt = parser.parse_args()

    if opt.dataset == 'tasador' and opt.num_shots != 5:
        print(f"[WARN] tasador requires num_shots=5. overriding {opt.num_shots} -> 5")
        opt.num_shots = 5

    opt.exp = 'experiments/exp-' + opt.exp

    best_model_path = os.path.join(opt.exp, 'best_model.pth')
    print('Loading the best model from:', best_model_path)

    if not os.path.exists(best_model_path):
        raise FileNotFoundError(
            f"best_model.pth not found: {best_model_path}\n"
            f"Check exp name and train output directory."
        )

    try:
        ret = init_dataset(opt, validation_only=True)
    except TypeError:
        ret = init_dataset(opt)

    if isinstance(ret, tuple):
        if len(ret) >= 3:
            tr_dataloader, val_dataloader, test_dataloader = ret[0], ret[1], ret[2]
        else:
            tr_dataloader, val_dataloader, test_dataloader = ret[0], None, ret[0]
    else:
        tr_dataloader, val_dataloader, test_dataloader = None, None, ret

    if opt.dataset == 'tasador' and opt.skip_embedding:
        if tr_dataloader is None:
            ret2 = init_dataset(opt)
            if isinstance(ret2, tuple) and len(ret2) >= 1:
                tr_dataloader = ret2[0]

        sample_x, _ = next(iter(tr_dataloader))
        opt.num_features_override = int(sample_x.shape[-1])
        print('[INFO] num_features_override:', opt.num_features_override)

    model = init_model(opt)

    map_loc = 'cuda' if opt.cuda else 'cpu'
    weights = torch.load(best_model_path, map_location=map_loc)
    model.load_state_dict(weights)

    model = model.cuda() if opt.cuda else model

    print('Dataset initialized!')
    print('Testing with best model..')
    test(opt=opt, test_dataloader=test_dataloader, model=model)


if __name__ == '__main__':
    main()