import os
import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtWidgets import QComboBox  # ← 顶部 import 加上这个
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QDateEdit
from PyQt6.QtCore import QDate


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

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 输入关键词搜索日志")
        self.search_input.textChanged.connect(self.apply_filter)  # 实时触发过滤

        # 时间范围筛选
        self.start_date_edit = QDateEdit()
        self.end_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.end_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDate(QDate.currentDate())

        # 筛选按钮
        self.date_filter_btn = QPushButton("📆 时间筛选")
        self.date_filter_btn.clicked.connect(self.apply_date_filter)

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

        filter_layout.addWidget(QLabel("关键词搜索:"))
        filter_layout.addWidget(self.search_input)

        # 日期筛选布局
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("起始日期:"))
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("结束日期:"))
        date_layout.addWidget(self.end_date_edit)
        date_layout.addWidget(self.date_filter_btn)
        layout.addLayout(date_layout)

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
        self.table.clearContents()  # 清空旧内容

        filter_text = self.filter_box.currentText()
        keyword = self.search_input.text().lower().strip()

        try:
            event_index = self.headers.index("事件类型")
        except ValueError:
            QMessageBox.warning(self, "错误", "日志文件中未找到 ‘事件类型’ 字段")
            return

        # 第一步：事件类型筛选
        if filter_text == "全部":
            temp_data = self.csv_data
        elif filter_text == "检测记录":
            temp_data = [row for row in self.csv_data if row[event_index] == "检测"]
        elif filter_text == "报警记录":
            temp_data = [row for row in self.csv_data if row[event_index] == "报警"]
        else:
            temp_data = self.csv_data

        # 第二步：关键词搜索（模糊匹配所有字段）
        if keyword:
            temp_data = [
                row for row in temp_data
                if any(keyword in str(cell).lower() for cell in row)
            ]

        self.filtered_data = temp_data
        self.current_page = 1
        self.total_pages = max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page)
        self.update_table()

    def apply_date_filter(self):
        try:
            time_index = self.headers.index("时间")  # 日志的时间字段列名
        except ValueError:
            QMessageBox.warning(self, "错误", "日志文件中未找到 '时间' 字段")
            return

        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        filtered = []
        for row in self.csv_data:
            row_date = row[time_index][:10]  # 截取前10位日期，如 2025-03-26
            if start_date <= row_date <= end_date:
                filtered.append(row)

        self.filtered_data = filtered
        self.current_page = 1
        self.total_pages = max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page)
        self.update_table()





