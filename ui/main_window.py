import sys
import cv2
import os
import numpy as np
from detection.detector import YOLOv8Detector
from PyQt6.QtCore import QDateTime
from PyQt6.QtWidgets import QMessageBox  # 👈 加到顶部 if 没有
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from managers.sound_manager import SoundManager
from managers.alert_manager import AlertManager
from managers.log_manager import LogManager
from ui.log_viewer import LogViewerWindow
from PyQt6.QtCore import QTimer  # 记得顶部 import
from PyQt6.QtCore import pyqtSignal

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QSlider, QStatusBar, QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class VideoThread(QThread):
    frame_update = pyqtSignal(QImage)  # 发送处理后的视频帧
    detection_result = pyqtSignal(list)  # 👈 用于发送检测信息

    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False
        self.video_source = 0  # 默认使用摄像头
        self.detector = YOLOv8Detector(model_path="models/yolo_weights/yolov8n.pt", conf_threshold=0.5)

    def set_video_source(self, source):
        """ 设置视频来源（摄像头 / 本地视频） """
        self.video_source = source

    def run(self):
        self.cap = cv2.VideoCapture(self.video_source)

        # Step 1：确保视频成功打开
        if not self.cap.isOpened():
            print("❌ 视频无法打开！")
            return

        print("🎥 视频流开始读取...")

        try:
            while self.running and self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()

                # Step 2：读取失败就跳过
                if not ret or frame is None or frame.size == 0:
                    print("⚠️ 读取空帧，跳过...")
                    if isinstance(self.video_source, str):  # 是本地视频
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 回到首帧
                        continue
                    else:
                        break

                # Step 3：检测
                detections = self.detector.detect(frame)

                # Step 4：画框
                for det in detections:
                    x1, y1, x2, y2 = map(int, det["bbox"])
                    conf = det["conf"]
                    label = f"{det['class_name']} {conf:.2f}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # Step 5：转换成 QImage（必须防止 frame 为 None）
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape

                qimg = QImage(frame_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()

                self.frame_update.emit(qimg)
                self.detection_result.emit(detections)

        except Exception as e:
            print(f"❌ 视频线程异常: {e}")


        finally:
            if self.cap:
                self.cap.release()
                self.cap = None  # 防止外部再误用
                print("📤 视频资源已释放")

    def stop(self):
        print("🛑 正在停止视频线程...")
        self.running = False  # 告诉 run() 循环退出
        self.wait()  # 等待线程自然结束
        print("✅ 视频线程已安全退出")


class PedestrianDetectionUI(QWidget):

    trigger_alert_signal = pyqtSignal(list)  # ✅ 新增：主线程中触发报警
    def __init__(self):
        super().__init__()
        self.initUI()
        self.video_thread = VideoThread()
        self.video_thread.frame_update.connect(self.update_video_frame)
        self.video_thread.detection_result.connect(self.update_detection_table)

        self.trigger_alert_signal.connect(self.trigger_alert)  # ✅ 信号连接 trigger_alert



        self.sound_manager = SoundManager()  # ✅ 初始化声音模块
        self.alert_manager = AlertManager(self)  # ✅ 注入当前窗口引用
        self.log_manager = LogManager()  # ✅ 初始化日志模块

        # 控制警报只弹一次（冷却机制）
        self.alert_shown = False

    def initUI(self):
        self.setWindowTitle("基于深度学习的行人检测系统")
        self.setGeometry(100, 100, 900, 600)

        # 1. 视频流显示
        self.video_label = QLabel("视频流窗口", self)
        self.video_label.setStyleSheet("background-color: black; color: white; font-size: 16px;")
        self.video_label.setFixedHeight(300)

        # 2. 控制按钮
        self.load_video_btn = QPushButton("加载视频")
        self.use_camera_btn = QPushButton("使用摄像头")
        self.start_detection_btn = QPushButton("启动检测")
        self.pause_detection_btn = QPushButton("暂停检测")
        self.view_logs_btn = QPushButton("查看日志")
        self.exit_btn = QPushButton("退出")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_video_btn)
        button_layout.addWidget(self.use_camera_btn)
        button_layout.addWidget(self.start_detection_btn)
        button_layout.addWidget(self.pause_detection_btn)
        button_layout.addWidget(self.view_logs_btn)  # ✅ 新增
        button_layout.addWidget(self.exit_btn)

        # 3. 参数调节
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setMinimum(30)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(50)
        self.confidence_slider_label = QLabel("置信度: 0.50", self)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("检测置信度:"))
        slider_layout.addWidget(self.confidence_slider)
        slider_layout.addWidget(self.confidence_slider_label)

        self.confidence_slider.valueChanged.connect(self.update_confidence_label)

        # 4. 检测结果表
        self.result_table = QTableWidget(self)
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["ID", "时间", "行人ID", "置信度"])
        self.result_table.setRowCount(5)

        # 5. 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("系统准备就绪")

        # 总布局
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addLayout(button_layout)
        layout.addLayout(slider_layout)
        layout.addWidget(self.result_table)
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

        # 绑定按钮事件
        self.load_video_btn.clicked.connect(self.load_video)
        self.use_camera_btn.clicked.connect(self.use_camera)
        self.start_detection_btn.clicked.connect(self.start_detection)
        self.pause_detection_btn.clicked.connect(self.pause_detection)
        self.view_logs_btn.clicked.connect(self.view_logs)  # ✅ 新增
        self.exit_btn.clicked.connect(self.close_app)

    def update_video_frame(self, img):
        self.video_label.setPixmap(QPixmap.fromImage(img))

    def update_confidence_label(self):
        value = self.confidence_slider.value() / 100.0
        self.confidence_slider_label.setText(f"置信度: {value:.2f}")
        self.video_thread.detector.set_conf_threshold(value)  # 👈 实时更新检测器阈值

    def update_detection_table(self, detections):
        self.result_table.setRowCount(len(detections))  # 根据检测数调整行数
        for i, det in enumerate(detections):
            self.result_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.result_table.setItem(i, 1, QTableWidgetItem(QDateTime.currentDateTime().toString("hh:mm:ss")))
            self.result_table.setItem(i, 2, QTableWidgetItem(det["class_name"]))
            self.result_table.setItem(i, 3, QTableWidgetItem(f"{det['conf']:.2f}"))

            # ✅ 日志记录：每一次检测
            self.log_manager.log_detection(det["bbox"], det["conf"], det["class_name"])

        # 🚨 添加条件触发预警（行人数量 ≥ 2 或 有人置信度 ≥ 0.8）
        if len(detections) >= 2 or any(det['conf'] >= 0.8 for det in detections):
            self.trigger_alert_signal.emit(detections)  # ✅ 发出信号，由主线程安全触发

    def trigger_alert(self, detections):
        if not self.alert_shown:
            self.alert_shown = True

            self.sound_manager.play_alert()  # ✅ 播放声音
            self.alert_manager.show_warning("⚠️ 安全预警", "检测到多人或高风险目标！请注意安全！")

            # ✅ 日志记录：取置信度最高的一个报警
            if detections:
                top_det = max(detections, key=lambda d: d["conf"])
                self.log_manager.log_alert(top_det["bbox"], top_det["conf"], top_det["class_name"])

            # ⏱ 设置 5 秒后自动解锁
            QTimer.singleShot(5000, self.reset_alert_flag)

    def reset_alert_flag(self):
        self.alert_shown = False
        print("🟢 警报冷却结束，可以再次触发")

    def load_video(self):
        """ 选择本地视频文件作为输入 """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择视频文件", "", "视频文件 (*.mp4 *.avi)")
        if file_path:
            self.video_thread.set_video_source(file_path)
            self.status_bar.showMessage(f"已加载视频: {file_path}")

    def use_camera(self):
        """ 切换回摄像头模式 """
        self.video_thread.set_video_source(0)
        self.status_bar.showMessage("已切换至摄像头模式")

    def start_detection(self):
        """ 启动视频流（摄像头 / 视频） """
        if not self.video_thread.isRunning():
            self.video_thread.running = True
            self.video_thread.start()
            self.status_bar.showMessage("行人检测已启动...")

    def pause_detection(self):
        """ 暂停检测 """
        if self.video_thread.isRunning():
            self.video_thread.stop()
            self.status_bar.showMessage("行人检测已暂停")

    def view_logs(self):
        latest_log_path = self.log_manager.get_latest_log_path()
        print(f"💡 获取日志路径: {latest_log_path}")
        if not os.path.exists(latest_log_path):
            QMessageBox.warning(self, "提示", "未找到日志文件！")
            return

        try:
            self.log_viewer = LogViewerWindow(latest_log_path)
            self.log_viewer.show()
            print("✅ 日志窗口成功弹出")
        except Exception as e:
            print("❌ 弹出失败:", e)

    def close_app(self):
        """ 退出应用 """
        self.status_bar.showMessage("正在退出...")
        if self.video_thread.isRunning():
            self.video_thread.stop()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PedestrianDetectionUI()
    win.show()
    sys.exit(app.exec())
