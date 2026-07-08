import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import openpyxl
import pandas as pd
import os
import time


csv_data = np.loadtxt('./old/m2_train_1vcpu_1000_.csv', delimiter=',')
split = 0.70
split = int(len(csv_data)*split)
X_train = csv_data[:split, 1:]
y_train = csv_data[:split, :1]
X_test = csv_data[split:, 1:]
y_test = csv_data[split:, :1]
device = (
        "cpu"
    #"cuda"
    #if torch.cuda.is_available()
    #else "mps"
    #if torch.backends.mps.is_available()
    #else "cpu"
)
print(device)

batch_size = 32
num_workers = 4
# Convert NumPy arrays to PyTorch tensors
X_train_tensor = torch.tensor(X_train, dtype=torch.float32, device=device)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32, device=device)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32, device=device)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32, device=device)

# Create a DataLoader for training data
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(train_dataset, batch_size=batch_size,shuffle=True)

class RegressionModel(nn.Module):
    def __init__(self, input_dim):
        super(RegressionModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64).to(device)
        self.fc2 = nn.Linear(64, 32).to(device)
        self.fc3 = nn.Linear(32, 32).to(device)
        self.fc4 = nn.Linear(32, 16).to(device)
        self.fc5 = nn.Linear(16, 8).to(device)
        self.fc6 = nn.Linear(8, 1).to(device)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        x = torch.relu(self.fc5(x))
        x = self.fc6(x)
        return x

model = RegressionModel(input_dim=X_train.shape[1]).to(device)

# 3. Model Architecture
loss_fn = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 4. Model Training
num_epochs = 800
num_batches = len(X_train) // batch_size

start = time.time()
for epoch in range(num_epochs):
    running_loss = 0.0
    for batch_X, batch_y in train_loader:
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = loss_fn(outputs, batch_y)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    if (epoch + 1) % 100 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {torch.sqrt(loss).item():.4f}')
stop = time.time()

# 5. Model Evaluation
with torch.no_grad():
    test_X = torch.tensor(X_test, dtype=torch.float32, device=device)
    test_y = torch.tensor(y_test, dtype=torch.float32, device=device)
    predicted = model(test_X)
    mse = loss_fn(predicted, test_y).item()
    mae = torch.mean(torch.abs(predicted - test_y)).item()
    rmse = torch.sqrt(torch.tensor(mse)).item()

    
print(f"Root Mean Squared Error: {rmse:.4f}")

# Configure file and sheet names
excel_file = f'{num_epochs}_result.xlsx'
sheet_name = f"epoch_loss"

# Create or initialize reward dataframe
try:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
except:
    df = pd.DataFrame(columns=["Epoch", "loss","time"])

# Append a new reward row to Excel
def add_reward(epoch, reward, time):
    df.loc[len(df)] = [epoch, reward, time]
    df.to_excel(excel_file, sheet_name=sheet_name, index=False, engine="openpyxl")

add_reward(num_epochs,round(rmse,4),(stop-start))

print(stop-start)
now_time = time.localtime()

#if not os.path.exists(f'result_{num_epochs}.xlsx'):
#    with pd.ExcelWriter(f'result_{num_epochs}.xlsx', mode='w', engine='openpyxl') as writer:
#        data.to_excel(writer, sheet_name=f'epoch {num_epochs}, {time.strftime("%Y-%m-%d %H%M%S", now_time)}')
#else:
#    with pd.ExcelWriter(f'result_{num_epochs}.xlsx', mode='a', engine='openpyxl') as writer:
#        data.to_excel(writer, sheet_name=f'epoch {num_epochs}, {time.strftime("%Y-%m-%d %H%M%S", now_time)}')
