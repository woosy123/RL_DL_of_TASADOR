import csv

# 텍스트 파일에서 데이터 읽기
with open('result.txt', 'r') as txt_file:
    lines = txt_file.readlines()

# CSV 파일로 저장할 데이터 준비
data = []
for line in lines:
    columns = line.strip().split()  # 띄어쓰기로 분리
    data.append(columns)

# CSV 파일로 저장
with open('cuda_result_1vcpu.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(data)
