#!/usr/bin/env python3
"""Train sanitized TASADOR-style Random Forest models.

This script trains either:
- Model-G: [message_size, network_throughput] -> vm_cpu_usage
- Model-H: [message_size, network_throughput, packet_per_sec, vm_cpu_usage] -> cpu_quota
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Input CSV path")
    parser.add_argument("--model", choices=["G", "H"], required=True)
    parser.add_argument("--out", required=True, help="Output joblib path")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.csv)

    if args.model == "G":
        features = ["message_size", "network_throughput"]
        target = "vm_cpu_usage"
    else:
        features = ["message_size", "network_throughput", "packet_per_sec", "vm_cpu_usage"]
        target = "cpu_quota"

    missing = [col for col in [*features, target] if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    x = df[features]
    y = df[target]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=args.test_size, random_state=args.random_state
    )

    pipe = Pipeline(
        steps=[
            ("scale", MinMaxScaler()),
            ("rf", RandomForestRegressor(n_estimators=100, random_state=args.random_state)),
        ]
    )
    pipe.fit(x_train, y_train)
    pred = pipe.predict(x_test)
    rmse = mean_squared_error(y_test, pred, squared=False)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": pipe, "features": features, "target": target, "rmse": rmse}, out)

    print(f"model={args.model} rmse={rmse:.4f} saved={out}")


if __name__ == "__main__":
    main()

