import os
import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtWidgets import QComboBox  # ← 顶部 import 加上这个

class LogViewerWindow(QWidget):
    def __init__(self, csv_path):
        super().__init__()
        self.setWindowTitle("🚦 日志查看器")
        self.resize(900, 500)

        # 筛选器
        self.filter_label = QLabel("筛选事件类型:")
        self.filter_box = QComboBox()
        self.filter_box.addItems(["全部", "检测记录", "报警记录"])
        self.filter_box.currentIndexChanged.connect(self.apply_filter)

        self.table = QTableWidget(self)

        # 分页参数
        self.current_page = 1
        self.rows_per_page = 20
        self.total_pages = 1
        self.csv_data = []  # 所有日志行（去掉表头）
        self.filtered_data = []  # 筛选后的数据

        # 底部分页控件
        self.prev_btn = QPushButton("⬅ 上一页")
        self.next_btn = QPushButton("下一页 ➡")
        self.page_label = QLabel("")

        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)

        # 布局
        layout = QVBoxLayout()

        # 顶部筛选布局
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_box)

        layout.addLayout(filter_layout)  # 添加到主 layout

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

        self.filtered_data = self.csv_data.copy()  # 初始时不过滤
        self.total_pages = max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page)
        self.update_table()
        print(f"✅ 加载的日志文件路径: {csv_path}")
        print(f"📌 表头字段: {self.headers}")
        for i in range(min(3, len(self.csv_data))):  # 只打印前3行日志内容看看结构
            print(f"📄 第 {i + 1} 行数据: {self.csv_data[i]}")

    def update_table(self):
        self.table.clearContents()  # ✅ 放在这里，清除旧内容

        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        page_data = self.filtered_data[start:end]


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

    def apply_filter(self):
        self.table.clearContents()  # ← 每次刷新页面都清空原有内容

        filter_text = self.filter_box.currentText()
        try:
            event_index = self.headers.index("事件类型")  # ← 修正字段名
        except ValueError:
            QMessageBox.warning(self, "错误", "日志文件中未找到 ‘事件类型’ 字段")
            return

        if filter_text == "全部":
            self.filtered_data = self.csv_data
        elif filter_text == "检测记录":
            self.filtered_data = [row for row in self.csv_data if row[event_index] == "检测"]
        elif filter_text == "报警记录":
            self.filtered_data = [row for row in self.csv_data if row[event_index] == "报警"]
        else:
            self.filtered_data = self.csv_data

        self.current_page = 1
        self.total_pages = max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page)
        self.table.clearContents()  # ← 切页/筛选前清空旧数据
        self.update_table()


