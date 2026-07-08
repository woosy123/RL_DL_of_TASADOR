import joblib
from openpyxl import Workbook,load_workbook
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_log_error
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.preprocessing import MinMaxScaler
import csv

v='8vcpu_tasador'
any='web'
#dataset = pd.read_csv('../data/{}/m2_train_{}.csv'.format(any, v), names=['thread_quota', 'packet_size', 'bandwidth_tx', 'pps_tx', 'cpu_usage'])
#y = np.array(dataset['thread_quota'])
#X = np.array(dataset.drop('thread_quota', axis=1))
#dataset = pd.read_csv('1vCPU_performance_metrics_change_pps.csv'.format(any, v), names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
dataset = pd.read_csv('m2_train_8vcpu_5000_config1_webserver.csv'.format(any, v), names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
y = np.array(dataset['CPU Quota'])
X = np.array(dataset.drop(['CPU Quota'], axis=1))
#X = np.array(dataset.drop(['CPU Quota'], axis=1))
#X = np.array(dataset.drop(['thread_quota', 'pps_tx'], axis=1))
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.20, random_state=42)

min_max_scalar = MinMaxScaler()
train_X_ppr = min_max_scalar.fit_transform(train_X)
test_X_ppr = min_max_scalar.transform(test_X)
train_y_ppr = min_max_scalar.fit_transform(train_y.reshape(-1, 1))
test_y_ppr = min_max_scalar.transform(test_y.reshape(-1, 1))

clf = RandomForestRegressor(random_state=40)
n_estimators = list(range(10, 100, 10))
parameters = {'n_estimators': n_estimators,
'max_features': [1,2, 'sqrt', 'log2']}
clf_grid = GridSearchCV(clf, parameters, cv=3)
clf_grid.fit(train_X_ppr, train_y_ppr.ravel())
    #    clf.fit(train_X_ppr, train_y_ppr.ravel())
    #joblib.dump(clf_grid, "./model_%s/m2_1000" %v)

    # Test
#    for i in 1000, 5000, 10000, 20000:
clf = joblib.load("./data/{}/model/m2_{}".format(any,v))
        #clf = joblib.load("../data/{}/model/m2_{}".format(v, i))
pred_y_ppr = clf.predict(test_X_ppr)
pred_y = min_max_scalar.inverse_transform(pred_y_ppr.reshape(-1, 1))
score = np.sqrt(mean_squared_log_error(test_y, pred_y))
print(v,'msle :', score)
score_rmse = np.sqrt(mean_squared_error(test_y, pred_y))
print('rmse :',score_rmse)

    # Save
#wb = load_workbook("./{}/m2_{}.xlsx".format(any, v))

# 새로운 엑셀 파일 생성
output_file = "./data/{}/m2_{}.xlsx".format(any, v)
wb = Workbook()
ws = wb.active
ws.title = v

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

wb.save("./data/{}/m2_{}.xlsx".format(any, v))
