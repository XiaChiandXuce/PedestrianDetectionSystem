# managers/log_manager.py

import os
import csv
from datetime import datetime

class LogManager:
    def __init__(self, log_dir=None):
        """
        初始化日志管理器，确保日志目录在项目根目录 logs/
        """
        # 1. 获取当前文件（log_manager.py）的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. 假设当前文件在 managers/，向上返回到项目根目录
        project_root = os.path.abspath(os.path.join(current_dir, ".."))

        # 3. 默认日志目录设为 根目录/logs
        default_log_dir = os.path.join(project_root, "logs")

        # 4. 支持用户自定义路径，否则用默认
        self.log_dir = os.path.abspath(log_dir) if log_dir else default_log_dir

        # 5. 创建目录
        os.makedirs(self.log_dir, exist_ok=True)

        print(f"[LogManager] 初始化成功，日志将保存到：{self.log_dir}")

    def _get_log_path(self):
        """
        根据当前日期返回日志文件路径，例如 log_2025-03-24.csv
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"log_{date_str}.csv")

    def _write_row(self, row):
        """
        向日志文件追加一行数据，自动写入表头（如果是新文件）
        """
        log_path = self._get_log_path()
        is_new_file = not os.path.exists(log_path)

        with open(log_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow(["时间", "事件类型", "边界框", "置信度", "目标类别"])
            writer.writerow(row)

        # ✅ 打印真实路径（可选调试用）
        print(f"[LogManager] ✅ 当前写入文件为：{log_path}")

    def log_detection(self, bbox, confidence, class_name):
        """
        记录一次普通检测事件
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        row = [timestamp, "检测", str(bbox), round(confidence, 3), class_name]
        self._write_row(row)
        print(f"[LogManager] ✅ 检测记录已写入")

    def log_alert(self, bbox, confidence, class_name):
        """
        记录一次报警事件（高风险 / 多人等）
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        row = [timestamp, "报警", str(bbox), round(confidence, 3), class_name]
        self._write_row(row)
        print(f"[LogManager] 🚨 报警记录已写入")
