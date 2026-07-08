import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import math, csv, time

# GPU 사용 가능 여부 확인
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

file_name = "./m2_train_8vcpu_5000_config1_webserver"
# file_name = "1vCPU_performance_metrics"
# 데이터 로드
data = pd.read_csv(f"{file_name}.csv") 

# 입력 특성과 목표 값 분리
X = data.drop(["cpu_quota"], axis=1).values
y = data["cpu_quota"].values
# X = data.drop(["cpu_quota","pps","VM_CPU_usage"], axis=1).values
# y = data["cpu_quota"].values
#X = data.drop(["CPU Quota","pps","VM CPU Usage"], axis=1).values
#y = data["CPU Quota"].values
# 특성 스케일링
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 딥러닝 모델 정의
class RegressionModel(nn.Module):
    def __init__(self, input_dim):
        super(RegressionModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 32)
        self.fc4 = nn.Linear(32, 16)
        self.fc5 = nn.Linear(16, 8)
        self.fc6 = nn.Linear(8, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        x = torch.relu(self.fc5(x))
        x = self.fc6(x)
        return x

# 모델을 GPU로 이동
model = RegressionModel(input_dim=X_train.shape[1]).to(device)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)


batch_size = 16
num_batches = len(X_train) // batch_size

num_epochs = 800
start=time.time()
for epoch in range(num_epochs):
    total_loss = 0.0
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = (i + 1) * batch_size
        inputs = torch.tensor(X_train[start_idx:end_idx], dtype=torch.float32, device=device)
        targets = torch.tensor(y_train[start_idx:end_idx], dtype=torch.float32, device=device).unsqueeze(1)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
      
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / num_batches
    if (epoch + 1)% 100 == 0:
        print(f"Epoch [{epoch+1}/{num_epochs}], Avg Loss: {math.sqrt(avg_loss):.4f}")
end = time.time()
with torch.no_grad():
    test_X = torch.tensor(X_test, dtype=torch.float32,device=device)
    test_y = torch.tensor(y_test, dtype=torch.float32,device=device).unsqueeze(1)
    predicted = model(test_X)
    mse =  criterion(predicted, test_y).item()
    mae = torch.mean(torch.abs(predicted - test_y)).item()
    rmse = torch.sqrt(torch.tensor(mse)).item()
    
print(f"Root Mean Squared Error: {rmse:.4f},Running time: {(end-start):.4f}")

# # 파일명과 시트명 설정
# excel_file = '1vcpu_result.xlsx'
# sheet_name = "episode_rewards"

# # 보상을 기록할 데이터프레임 생성 또는 엑셀 파일이 없는 경우 초기화
# try:
#     df = pd.read_excel(excel_file, sheet_name=sheet_name)
# except:
#     df = pd.DataFrame(columns=["Epoch", "loss","time"])

# # 새로운 보상을 엑셀에 추가하는 함수
# def add_reward(epoch, reward, time):
#     df.loc[len(df)] = [epoch, reward, time]
#     df.to_excel(excel_file, sheet_name=sheet_name, index=False, engine="op${NET_IFACE}")

# add_reward(num_epochs,round(rmse,4),(end-start))


# # 목표 CPU Quota 값을 예측하는 함수
# def predict_cpu_quota(network_throughput, message_size):
#     input_data = np.array([[message_size, network_throughput]])
#     scaled_input = scaler.transform(input_data)
#     scaled_input_tensor = torch.tensor(scaled_input, dtype=torch.float32, device=device)
#     predicted_cpu_quota = model(scaled_input_tensor).item()
#     return predicted_cpu_quota

# # 목표 CPU Quota 값 예측
# p_cpu_quota = []  
# target_message_size = 64
# for i in range(5):
#     for target_network_throughput in range(100, 2001, 50): # 목표 network_throughput 값 설정
#         predicted_cpu_quota = predict_cpu_quota(target_network_throughput, target_message_size)
#         p_cpu_quota.append([target_network_throughput,target_message_size,int(predicted_cpu_quota)])
#     target_message_size *= 2 # 목표 message_size 값 설정
# df = pd.DataFrame(p_cpu_quota, columns=["network_SLO", "message_size", "cpu_quota"])
# csv_file_path = f"{file_name}_{num_epochs}_output.csv"
# df.to_csv(csv_file_path, index=False)


