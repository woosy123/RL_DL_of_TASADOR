import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import time
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
import random

# 데이터 로드 및 전처리
def load_and_preprocess_data(filepath):
    dataset = pd.read_csv(filepath, names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
    y = np.array(dataset['VM CPU Usage'])
    X = np.array(dataset.drop(['CPU Quota', 'PPS', 'VM CPU Usage'], axis=1))

    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

    return torch.tensor(X_scaled, dtype=torch.float32), torch.tensor(y_scaled, dtype=torch.float32), scaler_X, scaler_y

# 결정 트리 구현
class DecisionTreeNode:
    def __init__(self, depth, max_depth, min_samples_split):
        self.depth = depth
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.is_leaf = False
        self.threshold = None
        self.feature_idx = None
        self.left = None
        self.right = None
        self.value = None

    def fit(self, X, y):
        if self.depth >= self.max_depth or len(y) < self.min_samples_split or len(torch.unique(y)) == 1:
            self.is_leaf = True
            self.value = y.mean().item()
            return

        best_feature, best_threshold = self._find_best_split(X, y)
        if best_feature is None:
            self.is_leaf = True
            self.value = y.mean().item()
            return

        self.feature_idx = best_feature
        self.threshold = best_threshold
        left_mask = X[:, best_feature] <= best_threshold
        right_mask = ~left_mask

        self.left = DecisionTreeNode(self.depth + 1, self.max_depth, self.min_samples_split)
        self.right = DecisionTreeNode(self.depth + 1, self.max_depth, self.min_samples_split)

        self.left.fit(X[left_mask], y[left_mask])
        self.right.fit(X[right_mask], y[right_mask])

    def _find_best_split(self, X, y):
        best_feature, best_threshold = None, None
        best_impurity = float('inf')

        for feature_idx in range(X.shape[1]):
            thresholds = torch.unique(X[:, feature_idx])
            for threshold in thresholds:
                left_mask = X[:, feature_idx] <= threshold
                right_mask = ~left_mask

                if left_mask.sum() == 0 or right_mask.sum() == 0:
                    continue

                left_y = y[left_mask]
                right_y = y[right_mask]

                impurity = self._gini_impurity(left_y, right_y)
                if impurity < best_impurity:
                    best_impurity = impurity
                    best_feature = feature_idx
                    best_threshold = threshold

        return best_feature, best_threshold

    def _gini_impurity(self, left_y, right_y):
        def gini(y):
            probs = torch.bincount(y.int()) / len(y)
            return 1.0 - torch.sum(probs ** 2)

        total = len(left_y) + len(right_y)
        return (len(left_y) / total) * gini(left_y) + (len(right_y) / total) * gini(right_y)

    def predict(self, X):
        if self.is_leaf:
            return torch.full((X.shape[0],), self.value)
        mask = X[:, self.feature_idx] <= self.threshold
        preds = torch.zeros(X.shape[0])
        preds[mask] = self.left.predict(X[mask])
        preds[~mask] = self.right.predict(X[~mask])
        return preds

# 랜덤 포레스트 구현
class RandomForestRegressorPyTorch:
    def __init__(self, n_estimators=10, max_depth=10, min_samples_split=2):
        self.n_estimators = n_estimators
        self.trees = [DecisionTreeNode(0, max_depth, min_samples_split) for _ in range(n_estimators)]

    def fit(self, X, y):
        for tree in self.trees:
            bootstrap_idx = torch.randint(0, X.shape[0], (X.shape[0],))
            X_sample, y_sample = X[bootstrap_idx], y[bootstrap_idx]
            tree.fit(X_sample, y_sample)

    def predict(self, X):
        preds = torch.stack([tree.predict(X) for tree in self.trees])
        return preds.mean(dim=0)

# 데이터 경로
filepath = '1vCPU_performance_metrics_new_tasador.csv'

# 데이터 로드
X, y, scaler_X, scaler_y = load_and_preprocess_data(filepath)

# 모델 학습
model = RandomForestRegressorPyTorch(n_estimators=100, max_depth=10, min_samples_split=5)
start = time.time()
model.fit(X, y)
print("Training Time:", time.time() - start)

# 예측
predictions = model.predict(X)

# 역정규화 (원래 값으로 복원)
predictions_original = scaler_y.inverse_transform(predictions.unsqueeze(1).numpy())
print("Predictions:", predictions_original[:10])

# 모델 저장
torch.save(model, "./random_forest_model.pth")


