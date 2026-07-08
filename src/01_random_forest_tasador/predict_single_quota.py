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
# 1. 학습 데이터 로드 및 분리
dataset = pd.read_csv('1vCPU_performance_metrics_new_tasador.csv', names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
y = np.array(dataset['CPU Quota'])  # 타깃 데이터
X = np.array(dataset.drop(['CPU Quota'], axis=1))  # 입력 데이터 (4개 피처)

# 2. 각 데이터에 대해 별도의 MinMaxScaler 사용
scaler_X = MinMaxScaler()  # 입력 데이터용 스케일러
scaler_y = MinMaxScaler()  # 타깃 데이터용 스케일러

# 3. 각 데이터로 스케일러 학습
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.20, random_state=42)
train_X_ppr = scaler_X.fit_transform(train_X)  # 입력 피처 스케일링
test_X_ppr = scaler_X.transform(test_X)        # 테스트 입력 피처 스케일링
train_y_ppr = scaler_y.fit_transform(train_y.reshape(-1, 1))  # 타깃 값 스케일링
test_y_ppr = scaler_y.transform(test_y.reshape(-1, 1))        # 테스트 타깃 값 스케일링

# 4. 모델 학습
clf = RandomForestRegressor(random_state=40)
n_estimators = list(range(10, 100, 10))
parameters = {'n_estimators': n_estimators, 'max_features': [1, 2, 'sqrt', 'log2']}
clf_grid = GridSearchCV(clf, parameters, cv=3)
clf_grid.fit(train_X_ppr, train_y_ppr.ravel())

# 5. 저장된 모델 불러오기
clf = joblib.load("./data/{}/model/m2_{}".format(any, v))

# 6. 새로운 입력 데이터 생성
throughput = 750  # 예측하려는 throughput 값
message_size = 64  # 주어진 message size 값
pps = throughput * 10**6 / (1480 * 8)  # PPS 계산
vm_cpu_usage = 74  # 주어진 VM CPU Usage 값

# 새로운 입력 데이터 생성
new_input_data = np.array([[message_size, throughput, pps, vm_cpu_usage]])

# 7. 입력 데이터 스케일링 (`scaler_X` 사용)
new_input_data_scaled = scaler_X.transform(new_input_data)  # 입력 피처 스케일링

# 8. 예측 수행
new_pred_y_ppr = clf.predict(new_input_data_scaled)

# 9. 예측된 값 복원 (`scaler_y` 사용)
new_pred_y = scaler_y.inverse_transform(new_pred_y_ppr.reshape(-1, 1))

# 10. 예측 결과 출력
print(f"Predicted CPU Quota when throughput is {throughput}: {new_pred_y[0][0]}")

