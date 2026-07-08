import joblib
from op${NET_IFACE} import load_workbook
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_log_error
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.preprocessing import MinMaxScaler
import csv
import time
v='8vcpu_tasador'
any='web'
dataset = pd.read_csv('m2_train_8vcpu_5000_config1_webserver.csv'.format(any, v), names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
#dataset = pd.read_csv('8vCPU_performance_metrics_tasador.csv'.format(any, v), names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
#dataset = pd.read_csv('train_8vcpu_1000.csv'.format(any, v), names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
y = np.array(dataset['VM CPU Usage'])
X = np.array(dataset.drop(['CPU Quota','PPS', 'VM CPU Usage'], axis=1))
#train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.20, random_state=40)


min_max_scalar = MinMaxScaler()
train_X_ppr = min_max_scalar.fit_transform(X)
#test_X_ppr = min_max_scalar.transform(test_X.reshape(-1, 1))
train_y_ppr = min_max_scalar.fit_transform(y.reshape(-1, 1))
#test_y_ppr = min_max_scalar.transform(test_y)

n_estimators = list(range(100, 1000, 10))
max_features = [1, 2]
min_samples_split = [2, 5, 10]
min_samples_leaf = [1, 2, 4]
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf}

clf = RandomForestRegressor(random_state=40)
start = time.time()
clf_random_cv = RandomizedSearchCV(estimator=clf, param_distributions=random_grid, n_iter=100, cv=5, scoring='neg_root_mean_squared_error', verbose=2, n_jobs=8, random_state=40)
clf_random_cv.fit(train_X_ppr, train_y_ppr.ravel())
print('training time :',time.time()-start)
best_params = clf_random_cv.best_params_
print("Best n_estimators:", best_params['n_estimators'])
# Save model
joblib.dump(clf_random_cv, "./data/{}/model/m1_{}".format(any, v))
