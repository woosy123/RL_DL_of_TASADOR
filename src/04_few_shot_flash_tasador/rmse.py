import os
import csv
import re
import argparse

def extract_rmse(metrics_path):
    with open(metrics_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()

    m = re.search(r'RMSE\s*,\s*([0-9.eE+-]+)', text)
    if m:
        return float(m.group(1))

    m = re.search(r'\[RMSE\]\s*([0-9.eE+-]+)', text)
    if m:
        return float(m.group(1))

    raise ValueError(f'RMSE not found in {metrics_path}')


def collect_rmse(root_dir):
    rows = []

    for current_root, _, files in os.walk(root_dir):
        if 'metrics.txt' in files:
            metrics_path = os.path.join(current_root, 'metrics.txt')
            exp_name = os.path.basename(current_root)

            try:
                rmse = extract_rmse(metrics_path)
                rows.append({
                    'exp_name': exp_name,
                    'rmse': rmse,
                    'metrics_path': metrics_path,
                })
            except Exception as e:
                rows.append({
                    'exp_name': exp_name,
                    'rmse': '',
                    'metrics_path': metrics_path,
                    'error': str(e),
                })

    rows.sort(key=lambda x: (x['rmse'] == '', x['rmse'] if x['rmse'] != '' else float('inf')))
    return rows


def save_csv(rows, out_csv):
    fieldnames = ['exp_name', 'rmse', 'metrics_path', 'error']
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            if 'error' not in row:
                row['error'] = ''
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str, default='experiments')
    parser.add_argument('--out', type=str, default='rmse_summary.csv')
    args = parser.parse_args()

    rows = collect_rmse(args.root)
    save_csv(rows, args.out)

    print(f'[Saved] {args.out}')
    print(f'[Found] {len(rows)} experiment folders')


if __name__ == '__main__':
    main()