import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
any = 'web'
v = '1vcpu_mlp'
# 1. 학습 데이터 로드 및 스케일링 (기존 학습 데이터를 사용하여 fit)
dataset = pd.read_csv('1vCPU_performance_metrics_new.csv', names=['CPU Quota', 'Message Size', 'Network Throughput', 'PPS', 'VM CPU Usage'])
X = np.array(dataset.drop(['CPU Quota'], axis=1))

# Min-Max Scaler 정의 및 학습 데이터로 fit
min_max_scalar = MinMaxScaler()
min_max_scalar.fit(X)

# 2. 새로운 입력 데이터 생성
throughput = 750  # 예측하고자 하는 Network Throughput 값
message_size = 64  # 문제에서 주어진 Message Size 값
pps = throughput * 10**6 / (1480 * 8)  # PPS 계산
vm_cpu_usage = 74  # VM CPU Usage를 학습 데이터의 평균값으로 설정

# 새로운 예측 데이터 생성 (Message Size, Network Throughput, PPS, VM CPU Usage)
new_data = np.array([[message_size, throughput, pps, vm_cpu_usage]])

# 3. 새로운 데이터 스케일링
new_data_scaled = min_max_scalar.transform(new_data)

# 4. 저장된 모델 불러오기 (모델 경로가 정확한지 확인)
model_path = "./data/{}/model/m2_{}".format(any, v)
clf_loaded = joblib.load(model_path)

# 5. 예측 수행
predicted_value_ppr = clf_loaded.predict(new_data_scaled)

# 6. 예측된 CPU Quota 값 출력
print(f"Predicted CPU Quota when Network Throughput is {throughput} Mbps:", predicted_value_ppr[0])

