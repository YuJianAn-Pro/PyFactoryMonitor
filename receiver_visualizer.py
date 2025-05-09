import socket
import threading
import matplotlib.pyplot as plt
from collections import deque
import matplotlib
import pymysql

# 连接数据库
db = pymysql.connect(
    host='localhost',
    user='root',              # 输入用户名
    password='*********',     # 填密码
    database='device_monitor',# 选择你的数据库
    charset='utf8mb4'
)
cursor = db.cursor()
matplotlib.use('TkAgg')  # 明确指定后端 选TkAgg/Qt5Agg

# 数据容器
temps = deque(maxlen=50)
voltages = deque(maxlen=50)

# 初始化图表
plt.ion()
fig, ax = plt.subplots()
line1, = ax.plot([0] * 50, label='Temp (°C)')
line2, = ax.plot([0] * 50, label='Voltage (V)')
ax.legend()
ax.set_ylim(0, 120)

# 通信线程
def start_server():
    HOST = '127.0.0.1'
    PORT = 9999
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("等待连接")
        conn, addr = s.accept()
        with conn:
            print(f"来自 {addr} 的连接")
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                try:
                    temp, volt = map(float, data.strip().split(","))
                    temps.append(temp)
                    voltages.append(volt)
                    print(f"接收数据 -> 温度: {temp:.2f}°C, 电压: {volt:.2f}V")

                    # 写入数据库
                    sql = "INSERT INTO device_data (device_id, temperature, voltage) VALUES (%s, %s, %s)"
                    cursor.execute(sql, ("dev01", temp, volt))
                    db.commit()

                    if temp > 70:
                        print("警告：温度过高")
                except Exception as e:
                    print(f"解析数据失败: {e}")


# 主线程更新图表
def update_plot():
    while True:
        if temps:  # 有数据时才更新
            line1.set_ydata(list(temps) + [0] * (50 - len(temps)))
            line2.set_ydata(list(voltages) + [0] * (50 - len(voltages)))
            fig.canvas.draw()
            fig.canvas.flush_events()
        plt.pause(0.1)


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    update_plot()


