import os
import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
)

class LogViewerWindow(QWidget):
    def __init__(self, csv_path):
        super().__init__()
        self.setWindowTitle("🚦 日志查看器")
        self.resize(900, 500)

        self.table = QTableWidget(self)
        self.load_csv(csv_path)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_csv(self, csv_path):
        if not os.path.exists(csv_path):
            QMessageBox.warning(self, "错误", f"找不到日志文件: {csv_path}")
            return

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            QMessageBox.information(self, "提示", "日志文件为空")
            return

        self.table.setRowCount(len(rows) - 1)
        self.table.setColumnCount(len(rows[0]))
        self.table.setHorizontalHeaderLabels(rows[0])

        for i, row in enumerate(rows[1:]):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(val))
