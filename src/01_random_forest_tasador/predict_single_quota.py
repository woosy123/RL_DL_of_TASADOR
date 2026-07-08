import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
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

any = 'web'
v = '1vcpu_tasador'
# 1. Load and split training data
dataset = pd.read_csv('1vCPU_performance_metrics_new_tasador.csv', names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
y = np.array(dataset['CPU Quota'])  # Target data
X = np.array(dataset.drop(['CPU Quota'], axis=1))  # Input data with four features

# 2. Use separate MinMaxScaler instances
scaler_X = MinMaxScaler()  # Input scaler
scaler_y = MinMaxScaler()

# 3. Fit scalers from each dataset
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.20, random_state=42)
train_X_ppr = scaler_X.fit_transform(train_X)  # Scale input features
test_X_ppr = scaler_X.transform(test_X)        # Scale test input features
train_y_ppr = scaler_y.fit_transform(train_y.reshape(-1, 1))  # Scale target values
test_y_ppr = scaler_y.transform(test_y.reshape(-1, 1))        # Scale test target values

# 4. Train model
clf = RandomForestRegressor(random_state=40)
n_estimators = list(range(10, 100, 10))
parameters = {'n_estimators': n_estimators, 'max_features': [1, 2, 'sqrt', 'log2']}
clf_grid = GridSearchCV(clf, parameters, cv=3)
clf_grid.fit(train_X_ppr, train_y_ppr.ravel())

# 5. Load saved model
clf = joblib.load("./data/{}/model/m2_{}".format(any, v))

# 6. Create new input data
throughput = 750  # Throughput to predict
message_size = 64  # Given message size
pps = throughput * 10**6 / (1480 * 8)  # Calculate PPS
vm_cpu_usage = 74  # Given VM CPU usage

new_input_data = np.array([[message_size, throughput, pps, vm_cpu_usage]])

# 7. Scale input data with scaler_X
new_input_data_scaled = scaler_X.transform(new_input_data)  # Scale input features

# 8. Run prediction
new_pred_y_ppr = clf.predict(new_input_data_scaled)

# 9. Inverse-transform predicted value with scaler_y
new_pred_y = scaler_y.inverse_transform(new_pred_y_ppr.reshape(-1, 1))

# 10. Print prediction result
print(f"Predicted CPU Quota when throughput is {throughput}: {new_pred_y[0][0]}")

