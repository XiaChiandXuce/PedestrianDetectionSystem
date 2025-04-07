import sys
import cv2
import os
import numpy as np
from detection.detector import YOLOv8Detector
from PyQt6.QtCore import QDateTime
from PyQt6.QtWidgets import QMessageBox  # 👈 加到顶部 if 没有
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QComboBox  # ✅ 添加模型选择下拉框组件
from managers.sound_manager import SoundManager
from managers.alert_manager import AlertManager
from managers.log_manager import LogManager
from ui.log_viewer import LogViewerWindow
from PyQt6.QtCore import QTimer  # 记得顶部 import
from PyQt6.QtCore import pyqtSignal
from detection.collision_checker import CollisionChecker  # ✅ 加入碰撞检测模块
from detection.detector import YOLOv8Detector, YOLOv8PoseDetector
from utils.config import KEYPOINT_COLOR





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
        self.video_writer = None  # 🎥 视频写入器
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

        # 🎥 设置视频保存参数（确保放在 cap 成功打开之后）
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_writer = cv2.VideoWriter("output_pose.mp4", fourcc, fps, (width, height))

        print("🎥 视频流开始读取...")
        print(f"🎯 当前检测器类型: {type(self.detector).__name__}")

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
                if isinstance(self.detector, YOLOv8PoseDetector):
                    detections, keypoints_all = self.detector.detect(frame)
                else:
                    detections = self.detector.detect(frame)

                # Step 4：画框 & 画关键点（如果有）
                for det in detections:
                    x1, y1, x2, y2 = map(int, det["bbox"])
                    conf = det["conf"]
                    label = f"{det['class_name']} {conf:.2f}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # ✅ 如果是姿态模型，画关键点骨架
                if isinstance(self.detector,YOLOv8PoseDetector) and keypoints_all is not None and keypoints_all.size > 0:
                    self.draw_keypoints(frame, keypoints_all)

                # Step 5：转换成 QImage（必须防止 frame 为 None）
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape

                qimg = QImage(frame_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()

                if self.video_writer:
                    self.video_writer.write(frame)

                self.frame_update.emit(qimg)
                self.detection_result.emit(detections)

        except Exception as e:
            print(f"❌ 视频线程异常: {e}")


        finally:
            if self.cap:
                self.cap.release()
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None  # 清理
                self.cap = None  # 防止外部再误用
                print("📤 视频资源已释放")

    def draw_keypoints(self, frame, keypoints_all):
        SKELETON = [
            (5, 7), (7, 9), (6, 8), (8, 10),
            (11, 13), (13, 15), (12, 14), (14, 16),
            (5, 6), (11, 12), (5, 11), (6, 12)
        ]

        for keypoints in keypoints_all:
            keypoints = keypoints.tolist()  # ✅ numpy 转 list 更安全

        for keypoints in keypoints_all:
            # ✅ 画关键点
            for keypoints in keypoints_all:
                keypoints = keypoints.tolist()  # 保证 keypoints 是 list 而不是 numpy
                for point in keypoints:
                    if len(point) >= 2:
                        x, y = point[:2]
                        cv2.circle(frame, (int(x), int(y)), 3, KEYPOINT_COLOR, -1)

            # ✅ 画骨架连接线
            for i, j in SKELETON:
                if i < len(keypoints) and j < len(keypoints):
                    pt1 = tuple(map(int, keypoints[i][:2]))
                    pt2 = tuple(map(int, keypoints[j][:2]))
                    cv2.line(frame, pt1, pt2, (255, 0, 0), 2)

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

        # 添加这一行：
        self.collision_checker = CollisionChecker(distance_threshold=200)  # 默认阈值 50，可调

        # 控制警报只弹一次（冷却机制）
        self.alert_shown = False

        # ✅ 控制台提示当前模型路径和类别映射
        print(f"[UI初始化] ✅ 当前使用模型路径: {self.video_thread.detector.model.model.args['model']}")
        print(f"[UI初始化] ✅ 当前模型类别映射: {self.video_thread.detector.class_names}")

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
        self.view_statistics_btn = QPushButton("查看统计图")  # 新增
        # ✅ 模型选择下拉框：yolov8n.pt vs merged_model.pt
        self.model_selector = QComboBox()
        self.model_selector.addItems([
            "原始模型 yolov8n.pt",
            "融合模型 merged_model.pt",
            "姿态模型 yolov8x-pose-p6.pt"  # ✅ 新增
        ])
        self.exit_btn = QPushButton("退出")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_video_btn)
        button_layout.addWidget(self.use_camera_btn)
        button_layout.addWidget(self.start_detection_btn)
        button_layout.addWidget(self.pause_detection_btn)
        button_layout.addWidget(self.view_logs_btn)  # ✅ 新增
        button_layout.addWidget(self.view_statistics_btn)  # 新增
        button_layout.addWidget(self.model_selector)
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

        # 👉 添加碰撞阈值滑块
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setMinimum(10)
        self.threshold_slider.setMaximum(300)
        self.threshold_slider.setValue(200)  # 默认值，建议和初始化 collision_checker 的值一致
        self.threshold_slider_label = QLabel("碰撞阈值: 200 像素")

        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("碰撞阈值:"))
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_slider_label)

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
        layout.addLayout(threshold_layout)  # ✅ 把阈值滑块加入主界面布局

        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        self.setLayout(layout)

        # 绑定按钮事件
        self.load_video_btn.clicked.connect(self.load_video)
        self.use_camera_btn.clicked.connect(self.use_camera)
        self.start_detection_btn.clicked.connect(self.start_detection)
        self.pause_detection_btn.clicked.connect(self.pause_detection)
        self.view_logs_btn.clicked.connect(self.view_logs)  # ✅ 新增
        self.view_statistics_btn.clicked.connect(self.view_statistics)
        self.exit_btn.clicked.connect(self.close_app)

    def update_video_frame(self, img):
        self.video_label.setPixmap(QPixmap.fromImage(img))

    def update_confidence_label(self):
        value = self.confidence_slider.value() / 100.0
        self.confidence_slider_label.setText(f"置信度: {value:.2f}")
        self.video_thread.detector.set_conf_threshold(value)  # 👈 实时更新检测器阈值

    def update_threshold_label(self):
        value = self.threshold_slider.value()
        self.threshold_slider_label.setText(f"碰撞阈值: {value} 像素")
        self.collision_checker.threshold = value  # ✅ 实时同步到碰撞检测模块
        print(f"📏 实时更新碰撞阈值为：{value} 像素")

    def update_detection_table(self, detections):
        self.result_table.setRowCount(len(detections))  # 根据检测数调整行数
        for i, det in enumerate(detections):
            self.result_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.result_table.setItem(i, 1, QTableWidgetItem(QDateTime.currentDateTime().toString("hh:mm:ss")))
            self.result_table.setItem(i, 2, QTableWidgetItem(det["class_name"]))
            self.result_table.setItem(i, 3, QTableWidgetItem(f"{det['conf']:.2f}"))

            # ✅ 日志记录：每一次检测
            self.log_manager.log_detection(det["bbox"], det["conf"], det["class_name"])


        # 🚨 条件 1：碰撞预警（人车距离过近）
        # 分离出行人与车辆（class_id: 0 = person, 2/5/7 = car/bus/truck）
        pedestrians = [d for d in detections if d.get("class_id") == 0]
        vehicles = [d for d in detections if d.get("class_id") in [2, 5, 7]]

        # ⚠️ 判断人车是否有可能碰撞（像素距离小于阈值）
        # ✅ 正确写法（使用 self.collision_checker）：
        collision_risk = self.collision_checker.check(pedestrians, vehicles)

        # ✅ 新触发逻辑：只有在存在碰撞风险时，才发出预警
        if collision_risk:
            print("⚠️⚠️⚠️ 人车接近，触发预警！")
            self.trigger_alert_signal.emit(detections)

        # ✅ 未来这里将是碰撞预警主逻辑入口
        # print(f"🚶 行人数量: {len(pedestrians)}，🚗 车辆数量: {len(vehicles)}")

    def trigger_alert(self, detections):
        if not self.alert_shown:
            self.alert_shown = True

            self.sound_manager.play_alert()  # ✅ 播放声音
            self.alert_manager.show_warning("⚠️ 安全预警", "检测到多人或高风险目标！请注意安全！")

            # ✅ 日志记录：取置信度最高的一个报警
            if detections:
                top_det = max(detections, key=lambda d: d["conf"])

                # 🚶‍♀️ 抽取行人与车辆
                pedestrians = [d for d in detections if d.get("class_id") == 0]
                vehicles = [d for d in detections if d.get("class_id") in [2, 5, 7]]

                # 🧠 判断报警类型
                if self.collision_checker.check(pedestrians, vehicles):
                    event_type = "碰撞预警"
                else:
                    event_type = top_det["class_name"]

                # ✅ 日志记录
                self.log_manager.log_alert(top_det["bbox"], top_det["conf"], event_type)

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
        if not self.video_thread.isRunning():
            selected_model = self.model_selector.currentText()

            # 1. 决定模型路径
            if "融合" in selected_model:
                model_path = "models/yolo_weights/merged_model.pt"
            elif "姿态" in selected_model:
                model_path = "models/yolo_weights/yolov8x-pose-p6.pt"
            else:
                model_path = "models/yolo_weights/yolov8n.pt"

            # 2. 决定使用哪个类
            if "姿态" in selected_model:
                DetectorClass = YOLOv8PoseDetector
            else:
                DetectorClass = YOLOv8Detector

            # ✅ 只写一次实例化！
            self.video_thread.detector = DetectorClass(
                model_path=model_path,
                conf_threshold=self.confidence_slider.value() / 100.0
            )

            self.video_thread.running = True
            self.video_thread.start()
            self.status_bar.showMessage(f"✅ 使用模型：{selected_model}，检测已启动...")

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

    def view_statistics(self):
        from ui.log_statistics_window import LogStatisticsWindow
        self.statistics_window = LogStatisticsWindow()
        self.statistics_window.show()

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
