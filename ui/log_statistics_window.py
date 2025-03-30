import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox

# ✅ 防止中文乱码
plt.rcParams['font.family'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


class LogStatisticsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 每分钟报警次数趋势图")
        self.setGeometry(200, 200, 700, 450)

        self.layout = QVBoxLayout(self)

        self.canvas = FigureCanvas(plt.Figure())
        self.layout.addWidget(self.canvas)

        self.status_label = QLabel("✅ 成功加载报警趋势图", self)
        self.layout.addWidget(self.status_label)

        self.checkbox = QCheckBox("✔ 显示每分钟报警次数", self)
        self.checkbox.setChecked(True)
        self.checkbox.setEnabled(False)
        self.layout.addWidget(self.checkbox)

        self.plot_alert_statistics()

    def plot_alert_statistics(self):
        try:
            project_root = Path(__file__).resolve().parent.parent
            log_dir = project_root / "logs"
            latest_log_file = self.get_latest_log_file(log_dir)

            if not latest_log_file:
                self.status_label.setText("❌ 未找到日志文件")
                return

            df = pd.read_csv(latest_log_file)
            df["时间"] = pd.to_datetime(df["时间"])
            df["分钟"] = df["时间"].dt.strftime("%H:%M")

            # ✅ 只保留“报警”记录（非“检测”）
            alert_df = df[df["事件类型"] != "检测"]
            if alert_df.empty:
                self.status_label.setText("⚠️ 日志中没有报警记录")
                return

            stats = alert_df.groupby("分钟").size().reset_index(name="报警次数")

            ax = self.canvas.figure.subplots()
            ax.clear()
            ax.plot(stats["分钟"], stats["报警次数"], marker="o", linestyle='-', color='crimson', label="每分钟报警次数")

            ax.set_title("报警次数随时间变化")
            ax.set_xlabel("时间（每分钟）")
            ax.set_ylabel("报警次数")
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend()
            self.canvas.draw()

        except Exception as e:
            self.status_label.setText(f"❌ 绘图失败：{e}")
            print("❌ 绘图出错：", e)

    def get_latest_log_file(self, log_dir):
        try:
            files = [f for f in os.listdir(log_dir) if f.startswith("log_") and f.endswith(".csv")]
            if not files:
                return None
            latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
            return os.path.join(log_dir, latest_file)
        except Exception as e:
            print("❌ 读取日志失败：", e)
            return None
