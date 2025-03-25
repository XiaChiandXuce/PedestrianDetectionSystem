# managers/alert_manager.py
from PyQt6.QtWidgets import QMessageBox

class AlertManager:
    def __init__(self, parent=None):
        """
        初始化警报管理器
        :param parent: UI 窗口对象（用于显示弹窗）
        """
        self.parent = parent

    def show_warning(self, title: str, message: str):
        """
        显示警告弹窗
        :param title: 弹窗标题
        :param message: 弹窗内容
        """
        QMessageBox.warning(self.parent, title, message)
