import socket
import time
import random

HOST = '127.0.0.1'
PORT = 9999

def generate_data():
    temperature = random.uniform(20, 100)
    voltage = random.uniform(210, 230)
    return f"{temperature:.2f},{voltage:.2f}"

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("已连接接收端，开始发数据")
        while True:
            data = generate_data()
            s.sendall(data.encode())
            print(f"发送: {data}")
            time.sleep(1)
except ConnectionRefusedError:
    print(f"Error：无法连接 {HOST}:{PORT}")
except Exception as e:
    print(f"Error: {e}")