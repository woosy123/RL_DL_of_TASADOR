import csv

# Read data from the text file
with open('result.txt', 'r') as txt_file:
    lines = txt_file.readlines()

# Prepare rows for CSV output
data = []
for line in lines:
    columns = line.strip().split()  # Split by whitespace
    data.append(columns)

# Write to CSV
with open('cuda_result_1vcpu.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(data)
