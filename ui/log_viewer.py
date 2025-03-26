import os
import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QPushButton, QLabel, QHBoxLayout
)

class LogViewerWindow(QWidget):
    def __init__(self, csv_path):
        super().__init__()
        self.setWindowTitle("🚦 日志查看器")
        self.resize(900, 500)

        self.table = QTableWidget(self)

        # 分页参数
        self.current_page = 1
        self.rows_per_page = 20
        self.total_pages = 1
        self.csv_data = []  # 所有日志行（去掉表头）

        # 底部分页控件
        self.prev_btn = QPushButton("⬅ 上一页")
        self.next_btn = QPushButton("下一页 ➡")
        self.page_label = QLabel("")

        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.table)

        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        layout.addLayout(pagination_layout)

        self.setLayout(layout)

        # 加载日志
        self.load_csv(csv_path)

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

        self.headers = rows[0]
        self.csv_data = rows[1:]

        self.total_pages = max(1, (len(self.csv_data) + self.rows_per_page - 1) // self.rows_per_page)
        self.update_table()

    def update_table(self):
        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        page_data = self.csv_data[start:end]

        self.table.setRowCount(len(page_data))
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)

        for i, row in enumerate(page_data):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(val))

        self.page_label.setText(f"第 {self.current_page} 页 / 共 {self.total_pages} 页")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_table()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_table()
