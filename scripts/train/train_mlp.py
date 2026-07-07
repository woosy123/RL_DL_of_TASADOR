#!/usr/bin/env python3
"""Train a sanitized PyTorch MLP for CPU quota regression."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


class RegressionMLP(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--epochs", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.csv)
    features = ["message_size", "network_throughput", "packet_per_sec", "vm_cpu_usage"]
    target = "cpu_quota"

    missing = [col for col in [*features, target] if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    x = df[features].to_numpy(dtype="float32")
    y = df[[target]].to_numpy(dtype="float32")

    scaler = MinMaxScaler()
    x = scaler.fit_transform(x).astype("float32")

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = RegressionMLP(input_dim=x_train.shape[1]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()

    x_train_t = torch.tensor(x_train, device=device)
    y_train_t = torch.tensor(y_train, device=device)

    for epoch in range(args.epochs):
        perm = torch.randperm(x_train_t.shape[0], device=device)
        for start in range(0, x_train_t.shape[0], args.batch_size):
            idx = perm[start : start + args.batch_size]
            pred = model(x_train_t[idx])
            loss = loss_fn(pred, y_train_t[idx])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 100 == 0:
            print(f"epoch={epoch + 1} train_rmse={loss.sqrt().item():.4f}")

    x_test_t = torch.tensor(x_test, device=device)
    y_test_t = torch.tensor(y_test, device=device)
    with torch.no_grad():
        rmse = loss_fn(model(x_test_t), y_test_t).sqrt().item()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "features": features,
            "target": target,
            "scaler_min": scaler.min_,
            "scaler_scale": scaler.scale_,
            "rmse": rmse,
        },
        out,
    )
    print(f"rmse={rmse:.4f} saved={out}")


if __name__ == "__main__":
    main()

