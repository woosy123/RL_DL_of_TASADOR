import joblib
from op${NET_IFACE} import load_workbook
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_log_error
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.preprocessing import MinMaxScaler
import csv

#for v in '1vcpu', '2vcpu', '4vcpu', '8vcpu':
v = '1vcpu_tasador'
any = 'web'
#dataset = pd.read_csv('../data/{}/m2_train_{}.csv'.format(any, v), names=['thread_quota', 'packet_size', 'bandwidth_tx', 'pps_tx', 'cpu_usage'])
#y = np.array(dataset['cpu_usage'])
#X = np.array(dataset.drop(['cpu_usage','thread_quota','pps_tx'], axis=1))
dataset = pd.read_csv('1vCPU_performance_metrics_new_tasador.csv'.format(any, v), names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
y = np.array(dataset['VM CPU Usage'])
X = np.array(dataset.drop(['CPU Quota','PPS', 'VM CPU Usage'], axis=1))
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.40, random_state=40)

min_max_scalar = MinMaxScaler()
train_X_ppr = min_max_scalar.fit_transform(train_X)
test_X_ppr = min_max_scalar.transform(test_X)
train_y_ppr = min_max_scalar.fit_transform(train_y.reshape(-1, 1))
test_y_ppr = min_max_scalar.transform(test_y.reshape(-1, 1))

    # Cross validate
n_estimators = list(range(10, 100, 10))
parameters = {'n_estimators': n_estimators,
'max_features': [1,2, 'sqrt', 'log2']}
clf = RandomForestRegressor(random_state=40)
clf_grid = GridSearchCV(clf, parameters, cv=3)
clf_grid.fit(train_X_ppr, train_y_ppr.ravel())
    # Save model
#joblib.dump(clf_grid, "./memcached/m1_1000" %v)

    # Test
#for i in 1000, 5000, 10000, 20000:
clf = joblib.load("./data/{}/model/m1_{}".format(any, v))
pred_y_ppr = clf.predict(test_X_ppr)
pred_y = min_max_scalar.inverse_transform(pred_y_ppr.reshape(-1, 1))
#    pred_y = min_max_scalar.inverse_transform(pred_y_ppr.reshape(-1, 1))
score = np.sqrt(mean_squared_log_error(test_y, pred_y))
print(v, score)
score_rmse = np.sqrt(mean_squared_error(test_y, pred_y))
print('rmse :',score_rmse)

    # Save
wb = load_workbook('./memcached/m1_%s.xlsx' %v)

ws = wb["%s" %v]
ws.cell(1, 1).value = 'test_y'
ws.cell(1, 2).value = 'pred_y'
ws.cell(1, 3).value = 'packet_size'
ws.cell(1, 4).value = 'throughput'
for j in range(30):
    ws.cell(j+2, 1).value = test_y[j]
for j in range(30):
    ws.cell(j+2, 2).value = pred_y[j][0]
for j in range(30):
    ws.cell(j+2, 3).value = test_X[j][0]
for j in range(30):
    ws.cell(j+2, 4).value = test_X[j][1]

wb.save('./memcached/m1_%s.xlsx' %v)
