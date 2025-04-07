# detection/detector.py
import os
import numpy as np
from ultralytics import YOLO


class YOLOv8Detector:
    def __init__(self, model_path: str = 'models/yolo_weights/yolov8n.pt', conf_threshold: float = 0.5):
        """
        初始化检测器，加载模型
        :param model_path: 模型权重路径（相对路径）
        :param conf_threshold: 检测置信度阈值
        """
        # 🔧 获取项目根路径（无论从哪个目录运行都不怕）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_model_path = os.path.join(project_root, model_path)
        print(f"[YOLOv8Detector] ✅ 加载模型路径: {abs_model_path}")

        # 🚀 加载模型
        self.model = YOLO(abs_model_path)
        self.conf_threshold = conf_threshold

        # ✅ 自动适配类别：不写死 target_class_ids！
        self.class_names = self.model.names  # e.g., {0: 'person', 1: 'car', 2: 'truck', 3: 'bus'}
        self.target_class_ids = list(self.class_names.keys())  # e.g., [0, 1, 2, 3]
        print(f"[YOLOv8Detector] ✅ 类别映射: {self.class_names}")

    def set_conf_threshold(self, conf):
        self.conf_threshold = conf

    def detect(self, frame: np.ndarray):
        """
        对图像帧进行检测
        :param frame: BGR 格式图像（OpenCV读取）
        :return: list[dict] [{'bbox': [...], 'conf': ..., 'class_id': ..., 'class_name': ...}]
        """
        results = self.model.predict(frame, conf=self.conf_threshold, verbose=False)[0]
        detections = []

        for box in results.boxes:
            cls_id = int(box.cls)
            conf = float(box.conf)

            # ✅ 保留你自己训练的所有类别
            if cls_id in self.target_class_ids:
                x1, y1, x2, y2 = map(float, box.xyxy[0])
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'conf': conf,
                    'class_id': cls_id,
                    'class_name': self.class_names[cls_id]
                })

        return detections


class YOLOv8PoseDetector:
    def __init__(self, model_path: str = 'models/yolo_weights/yolov8x-pose-p6.pt', conf_threshold: float = 0.5):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_model_path = os.path.join(project_root, model_path)
        print(f"[YOLOv8PoseDetector] ✅ 加载姿态模型: {abs_model_path}")

        self.model = YOLO(abs_model_path)
        self.conf_threshold = conf_threshold
        self.class_names = self.model.names
        self.target_class_ids = list(self.class_names.keys())

    def set_conf_threshold(self, conf):
        self.conf_threshold = conf

    def detect(self, frame: np.ndarray):
        """
        返回关键点检测结果，格式为 list[dict] + 可选关键点结构（用于 UI 显示）
        """
        results = self.model.predict(frame, conf=self.conf_threshold, verbose=False)[0]
        detections = []
        keypoints_all = []

        for i, box in enumerate(results.boxes):
            cls_id = int(box.cls)
            conf = float(box.conf)
            if cls_id in self.target_class_ids:
                x1, y1, x2, y2 = map(float, box.xyxy[0])
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'conf': conf,
                    'class_id': cls_id,
                    'class_name': self.class_names[cls_id]
                })

        if results.keypoints is not None:
            keypoints_all = results.keypoints.xy.cpu().numpy()  # shape: (n, 17, 2)

        return detections, keypoints_all
