import argparse
import os
import torch
import pandas as pd
import math
import numpy as np

from utils import init_dataset
from train import init_model, batch_for_few_shot  # train.py의 함수 재사용


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

    # ===== 추가: 샘플링 옵션 =====
    parser.add_argument(
        '--support_strategy',
        type=str,
        default='uniform',
        choices=['uniform', 'quota_linspace', 'edge_median'],
    )
    parser.add_argument(
        '--query_strategy',
        type=str,
        default='uniform',
        choices=['uniform', 'random'],
    )
    parser.add_argument(
        '--max_queries_per_group',
        type=int,
        default=None,
    )

    # ===== (선택) tasador K=5 강제 토글(기존 호환) =====
    parser.add_argument('--force_tasador_k5', action='store_true')

    opt = parser.parse_args()

    if opt.dataset == 'tasador' and opt.force_tasador_k5 and opt.num_shots != 5:
        print(f"[WARN] force tasador num_shots=5. overriding {opt.num_shots} -> 5")
        opt.num_shots = 5

    # train.py와 저장 경로 규칙을 맞추기 (train.py: experiments/exp-<name>)
    opt.exp = 'experiments/exp-' + opt.exp
    best_model_path = os.path.join(opt.exp, 'best_model.pth')
    print('Loading the best model from:', best_model_path)
    if not os.path.exists(best_model_path):
        raise FileNotFoundError(best_model_path)

    # test dataloader
    test_dataloader = init_dataset(opt, validation_only=True)

    # skip_embedding이면 input dim 맞추기(학습과 동일하게)
    if opt.dataset == 'tasador' and opt.skip_embedding:
        # train loader로 x_dim을 맞추는 게 가장 안전
        ret2 = init_dataset(opt, validation_only=False)
        tr_dataloader = ret2[0] if isinstance(ret2, tuple) else ret2
        sample_x, _ = next(iter(tr_dataloader))
        opt.num_features_override = int(sample_x.shape[-1])
        print('[INFO] num_features_override:', opt.num_features_override)

    model = init_model(opt)
    map_loc = 'cuda' if opt.cuda else 'cpu'
    weights = torch.load(best_model_path, map_location=map_loc)
    model.load_state_dict(weights)
    model = model.cuda() if opt.cuda else model
    model.eval()

    # ===== 핵심: y_scale은 dataset에서 가져온다(하드코딩 100000 제거) =====
    y_scale = float(getattr(test_dataloader.dataset, "y_scale", 1.0))
    print("[INFO] y_scale(from dataset):", y_scale)

    preds = []
    trues = []

    with torch.no_grad():
        for batch in test_dataloader:
            x, y = batch
            x, y, last_targets = batch_for_few_shot(opt, x, y)

            model_output = model(x, y)
            last_model = model_output[:, -1, :].squeeze(0)

            pred_np = last_model.detach().cpu().view(-1).numpy() * y_scale
            pred_np = np.maximum(pred_np, 1000)
            true_np = last_targets.detach().cpu().view(-1).numpy() * y_scale

            # 정수 quota: 반올림 후 int
            pred_i = np.rint(pred_np).astype(int)
            true_i = np.rint(true_np).astype(int)

            preds.extend(pred_i.tolist())
            trues.extend(true_i.tolist())

    df = pd.DataFrame({
        'cpu_quota_true': trues,
        'cpu_quota_pred': preds,
        'abs_error': [abs(a-b) for a, b in zip(trues, preds)],
        'ape': [abs(a-b)/a if a != 0 else float('nan') for a, b in zip(trues, preds)],
    })

    rmse = math.sqrt(sum((a - b) ** 2 for a, b in zip(trues, preds)) / len(trues))
    print('[RMSE]', rmse)

    metrics_path = os.path.join(opt.exp, 'metrics.txt')
    with open(metrics_path, 'w') as f:
        f.write(f'RMSE,{rmse}\n')

    print('[Saved]', metrics_path)

    out_path = os.path.join(opt.exp, 'pred_vs_true.csv')
    df.to_csv(out_path, index=False)
    print('[Saved]', out_path)
    print(df.head(10))


if __name__ == '__main__':
    main()