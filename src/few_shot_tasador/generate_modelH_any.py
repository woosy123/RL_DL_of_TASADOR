import os
import sys
import joblib
import numpy as np
import pandas as pd
import json
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.metrics import mean_squared_log_error, r2_score
from sklearn.metrics import mean_squared_error
import csv
import time
v = '8vcpu_tasador'
any = 'web'
#dataset = pd.read_csv('1vCPU_performance_metrics_tasador.csv'.format(any, v), names=['thread_quota', 'packet_size', 'bandwidth_tx', 'pps_tx', 'cpu_usage'])
#dataset = pd.read_csv('8vCPU_performance_metrics_change_pps.csv'.format(any, v), names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
dataset = pd.read_csv('m2_train_8vcpu_5000_config1_webserver.csv'.format(any, v), names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
#dataset = pd.read_csv('train_8vcpu_1000.csv'.format(any, v), names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
    #daataset.fillna(0)
    #    pd.set_option('display.max_rows', None)
    #print(dataset.isnull())
y = np.array(dataset['CPU Quota'])
X = np.array(dataset.drop(['CPU Quota'], axis=1))
#X = np.array(dataset.drop(['CPU Quota'], axis=1))
#X = np.array(dataset.drop(['thread_quota', 'pps_tx'], axis=1))

min_max_scalar = MinMaxScaler()
#train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.20, random_state=40)

train_X_ppr = min_max_scalar.fit_transform(X)
#test_X_ppr = min_max_scalar.transform(test_X)
train_y_ppr = min_max_scalar.fit_transform(y.reshape(-1, 1))
#test_y_ppr = min_max_scalar.transform(test_y.reshape(-1, 1))


n_estimators = list(range(100, 1000, 10))
max_features = [1, 2, 3, 4]
min_samples_split = [2, 5, 10]
min_samples_leaf = [1, 2, 4]
random_grid = {'n_estimators': n_estimators,
                'max_features': max_features,
                'min_samples_split': min_samples_split,
                'min_samples_leaf': min_samples_leaf}
start = time.time()
clf = RandomForestRegressor(random_state=40)
clf_random_cv = RandomizedSearchCV(estimator=clf, param_distributions=random_grid, n_iter=100, cv=5, scoring='neg_root_mean_squared_error', verbose=2, n_jobs=-1, random_state=40)
clf_random_cv.fit(train_X_ppr, train_y_ppr.ravel())
print("training time :",time.time()-start)
best_params = clf_random_cv.best_params_
print("Best n_estimators:", best_params['n_estimators'])
joblib.dump(clf_random_cv, "./data/{}/model/m2_{}".format(any, v))
