import torch.utils.data as data
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np

used_features = [
    "message_size",
    "network_throughput",
    "packet_per_sec",
    "vm_cpu_usage",
    "vcpu",
    "cpu_model_id",
    "mem_gb",
    "nic_gbps",
    "switch_gbps",
]

group_cols = [
    "workload",
    "vcpu",
    "cpu_model",
    "mem_gb",
    "nic_gbps",
    "switch_gbps",
    "message_size",
]

REQ_COLS = [
    "workload", "vcpu", "cpu_model", "mem_gb", "nic_gbps", "switch_gbps",
    "cpu_quota", "message_size", "network_throughput", "packet_per_sec", "vm_cpu_usage",
]


def _load_and_clean_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path).reset_index(drop=True)

    missing = [c for c in REQ_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in {path}: {missing}. Expected {REQ_COLS}")

    numeric_cols = [
        "vcpu", "mem_gb", "nic_gbps", "switch_gbps",
        "cpu_quota", "message_size", "network_throughput", "packet_per_sec", "vm_cpu_usage",
    ]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=REQ_COLS).reset_index(drop=True)
    return df


def _build_cpu_model_mapping(train_df: pd.DataFrame) -> dict:
    cpu_models = sorted(train_df["cpu_model"].unique().tolist())
    return {m: i for i, m in enumerate(cpu_models)}


def _encode_cpu_model_id(df: pd.DataFrame, cpu_model_to_id: dict) -> pd.DataFrame:
    unknown_id = len(cpu_model_to_id)
    df = df.copy()
    df["cpu_model_id"] = df["cpu_model"].map(cpu_model_to_id).fillna(unknown_id).astype(int)
    return df


def _pick_nearest_unused_index(target_pos: int, used: set[int], n: int) -> int | None:
    """Helper function."""
    for d in range(0, n):
        for cand in (target_pos - d, target_pos + d):
            if 0 <= cand < n and cand not in used:
                return cand
    return None


def _pick_nearest_unused_index_by_quota(
    target_quota: float,
    quotas_sorted: np.ndarray,
    used: set[int],
) -> int | None:
    """


    """
    n = len(quotas_sorted)
    pos = int(np.searchsorted(quotas_sorted, target_quota, side="left"))
    left, right = pos - 1, pos

    while left >= 0 or right < n:
        cands = []
        if left >= 0 and left not in used:
            cands.append(left)
        if right < n and right not in used:
            cands.append(right)

        if cands:
            return min(cands, key=lambda i: abs(float(quotas_sorted[i]) - float(target_quota)))

        left -= 1
        right += 1

    return None


def _select_support_indices_by_quota(
    gdf_sorted: pd.DataFrame,
    k: int,
    strategy: str = "uniform",
) -> list[int]:
    """


    strategy:



    """
    n = len(gdf_sorted)
    if n <= k:
        return []

    quotas = gdf_sorted["cpu_quota"].to_numpy(dtype=np.float64)

    if strategy == "uniform":
        used: set[int] = set()
        positions = np.linspace(0, n - 1, k)
        for pos in positions:
            cand = _pick_nearest_unused_index(int(round(pos)), used, n)
            if cand is None:
                return []
            used.add(cand)
        return sorted(used) if len(used) == k else []

    if strategy == "quota_linspace":
        used: set[int] = set()
        q_min, q_max = float(quotas[0]), float(quotas[-1])
        targets = np.linspace(q_min, q_max, k, dtype=np.float64)
        for t in targets:
            idx = _pick_nearest_unused_index_by_quota(float(t), quotas, used)
            if idx is None:
                return []
            used.add(idx)
        return sorted(used) if len(used) == k else []

    if strategy == "edge_median":
        med = float(np.median(quotas))
        used: set[int] = set()

        if k == 1:
            order = np.argsort(np.abs(quotas - med))
            used.add(int(order[0]))
            return sorted(used)

        if k == 2:
            used.update([0, n - 1])
            return sorted(used)

        if k == 3:
            used.update([0, n - 1])
            order = np.argsort(np.abs(quotas - med))
            for i in order:
                i = int(i)
                if i not in used:
                    used.add(i)
                    break
            return sorted(used) if len(used) == 3 else []

        if k == 4:
            positions = np.linspace(0, n - 1, k)
            for pos in positions:
                cand = _pick_nearest_unused_index(int(round(pos)), used, n)
                if cand is not None:
                    used.add(cand)
            return sorted(used) if len(used) == 4 else []

        used.update([0, 1, n - 2, n - 1])
        order = np.argsort(np.abs(quotas - med))
        for i in order:
            i = int(i)
            if i not in used:
                used.add(i)
                break

        if len(used) < k:
            positions = np.linspace(0, n - 1, k)
            for pos in positions:
                if len(used) >= k:
                    break
                cand = _pick_nearest_unused_index(int(round(pos)), used, n)
                if cand is not None:
                    used.add(cand)

        return sorted(used) if len(used) == k else []

    raise ValueError(f"Unknown support strategy: {strategy}")


def _select_query_indices(
    n: int,
    support_set: set[int],
    max_queries: int | None,
    strategy: str = "uniform",
) -> list[int]:
    """




    """
    candidates = [i for i in range(n) if i not in support_set]
    if max_queries is None or len(candidates) <= max_queries:
        return candidates

    if max_queries <= 0:
        return []

    if strategy == "uniform":
        pos = np.linspace(0, len(candidates) - 1, max_queries)
        picked = []
        used = set()
        for p in pos:
            idx0 = int(round(p))
            idx0 = max(0, min(idx0, len(candidates) - 1))

            chosen = None
            for d in range(0, len(candidates)):
                for cand in (idx0 - d, idx0 + d):
                    if 0 <= cand < len(candidates) and cand not in used:
                        chosen = cand
                        break
                if chosen is not None:
                    break

            if chosen is None:
                break

            used.add(chosen)
            picked.append(candidates[chosen])

        return picked[:max_queries]

    rng = np.random.default_rng(42)
    return rng.choice(candidates, size=max_queries, replace=False).tolist()


def _build_processed_rows(
    df: pd.DataFrame,
    num_samples: int,
    y_scale: float,
    max_queries_per_group: int | None,
    support_strategy: str,
    query_strategy: str,
) -> tuple[np.ndarray, np.ndarray]:
    """





    """
    grouped = df.groupby(group_cols, sort=True)

    all_cols = []
    for i in range(num_samples):
        for col_name in used_features:
            all_cols.append(f"{col_name}_s{i+1}")
        all_cols.append(f"quota_s{i+1}")
    for col_name in used_features:
        all_cols.append(col_name)
    all_cols.append("quota_to_predict")

    rows = []

    for _, gdf in grouped:
        gdf = gdf.sort_values(["cpu_quota"], ascending=True).reset_index(drop=True)
        n = len(gdf)
        if n <= num_samples:
            continue

        support_idx = _select_support_indices_by_quota(gdf, k=num_samples, strategy=support_strategy)
        if not support_idx:
            continue

        support_df = gdf.iloc[support_idx].sort_values(["cpu_quota"], ascending=True)

        row_to_add = []
        for _, r in support_df.iterrows():
            row_to_add.extend([float(r[c]) for c in used_features])
            row_to_add.append(float(r["cpu_quota"]))

        support_set = set(support_idx)
        query_idx = _select_query_indices(n, support_set, max_queries_per_group, strategy=query_strategy)
        if len(query_idx) == 0:
            continue

        for qi in query_idx:
            q = gdf.iloc[qi]
            full_row = row_to_add + [float(q[c]) for c in used_features] + [float(q["cpu_quota"])]
            rows.append(full_row)

    if len(rows) == 0:
        raise RuntimeError("No samples generated. Check: groups size, support/query selection rules.")

    processed_df = pd.DataFrame(rows, columns=all_cols)

    y_all = processed_df["quota_to_predict"].to_numpy(dtype=np.float32)
    y_all = (y_all / float(y_scale)).astype(np.float32)

    x_all = processed_df.drop(columns=["quota_to_predict"]).to_numpy(dtype=np.float32)
    return x_all, y_all


class TasadorDatasetXSamplesDifferentAppsForTrainTestValidate(data.Dataset):
    def __init__(
        self,
        num_samples: int,
        mode: str = "train",
        root: str = ".",
        train_filename: str = "tasador_dataset.csv",
        test_filename: str = "tasador_config2.csv",
        transform=None,
        target_transform=None,
        normalize_x: bool = True,

        normalize_y: bool = True,
        y_scale: float | None = None,
        support_strategy: str = "uniform",   # 'uniform' / 'quota_linspace' / 'edge_median'
        max_queries_per_group: int | None = None,
        query_strategy: str = "uniform",     # 'uniform' or 'random'
    ):
        super().__init__()
        self.root = root
        self.transform = transform
        self.target_transform = target_transform
        self.mode = mode

        if mode not in ["train", "test"]:
            raise ValueError(f"mode must be 'train' or 'test', got {mode}")

        if not isinstance(num_samples, int) or num_samples <= 0:
            raise ValueError(f"num_samples must be a positive int, got {num_samples}")

        train_path = f"{self.root}/{train_filename}"
        train_df = _load_and_clean_csv(train_path)
        cpu_model_to_id = _build_cpu_model_mapping(train_df)
        train_df = _encode_cpu_model_id(train_df, cpu_model_to_id)

        if normalize_y:
            if y_scale is None:
                y_scale = float(train_df["cpu_quota"].max())
            if y_scale <= 0:
                raise ValueError(f"Invalid y_scale={y_scale}")
        else:
            y_scale = 1.0
        self.y_scale = float(y_scale)

        x_train_raw, y_train = _build_processed_rows(
            train_df,
            num_samples=num_samples,
            y_scale=self.y_scale,
            max_queries_per_group=max_queries_per_group,
            support_strategy=support_strategy,
            query_strategy=query_strategy,
        )

        self.scaler = None
        if normalize_x:
            self.scaler = MinMaxScaler(clip=True)
            x_train = self.scaler.fit_transform(x_train_raw).astype(np.float32)
        else:
            x_train = x_train_raw

        if self.mode == "train":
            self.x_train = x_train
            self.y_train = y_train
            self.x_test = np.zeros((0, x_train.shape[1]), dtype=np.float32)
            self.y_test = np.zeros((0,), dtype=np.float32)
        else:
            test_path = f"{self.root}/{test_filename}"
            test_df = _load_and_clean_csv(test_path)
            test_df = _encode_cpu_model_id(test_df, cpu_model_to_id)

            x_test_raw, y_test = _build_processed_rows(
                test_df,
                num_samples=num_samples,
                y_scale=self.y_scale,
                max_queries_per_group=max_queries_per_group,
                support_strategy=support_strategy,
                query_strategy=query_strategy,
            )

            if normalize_x:
                x_test = self.scaler.transform(x_test_raw).astype(np.float32)
            else:
                x_test = x_test_raw

            self.x_test = x_test
            self.y_test = y_test
            self.x_train = np.zeros((0, x_test.shape[1]), dtype=np.float32)
            self.y_train = np.zeros((0,), dtype=np.float32)

        print("[TasadorDataset] mode:", self.mode,
              "| K(num_samples):", num_samples,
              "| X_dim:", (self.x_train.shape[1] if self.mode == "train" else self.x_test.shape[1]),
              "| y_scale:", self.y_scale,
              "| train_rows:", len(self.y_train),
              "| test_rows:", len(self.y_test),
              "| support_strategy:", support_strategy,
              "| query_strategy:", query_strategy)

    def __getitem__(self, idx):
        if self.mode == "train":
            x, y = self.x_train[idx], self.y_train[idx]
        else:
            x, y = self.x_test[idx], self.y_test[idx]

        if self.transform:
            x = self.transform(x)
        if self.target_transform:
            y = self.target_transform(y)

        return x, y

    def __len__(self):
        return len(self.y_train) if self.mode == "train" else len(self.y_test)


if __name__ == "__main__":
    tr = TasadorDatasetXSamplesDifferentAppsForTrainTestValidate(
        num_samples=5,
        mode="train",
        root=".",
        train_filename="tasador_dataset.csv",
        test_filename="tasador_config2.csv",
        normalize_x=True,
        normalize_y=True,
        max_queries_per_group=10,
        support_strategy="uniform",
        query_strategy="uniform",
    )
    te = TasadorDatasetXSamplesDifferentAppsForTrainTestValidate(
        num_samples=5,
        mode="test",
        root=".",
        train_filename="tasador_dataset.csv",
        test_filename="tasador_config2.csv",
        normalize_x=True,
        normalize_y=True,
        max_queries_per_group=10,
        support_strategy="uniform",
        query_strategy="uniform",
    )

    print("train:", len(tr), "test:", len(te))
    x0, y0 = tr[0]
    print("x_dim:", x0.shape, "y(norm):", y0, "y(orig):", y0 * tr.y_scale)

    # support_strategy="quota_linspace"