# detector.py
import os
from ultralytics import YOLO
import numpy as np

class YOLOv8Detector:
    def __init__(self, model_path: str = 'models/yolo_weights/yolov8n.pt', conf_threshold: float = 0.5):
        """
        初始化检测器，加载模型
        :param model_path: 模型权重路径
        :param conf_threshold: 置信度阈值
        """

        # ✅ 自动定位到项目根目录（当前文件的上两级）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_model_path = os.path.join(project_root, model_path)

        print(f"[YOLOv8Detector] ✅ 加载模型路径: {abs_model_path}")  # 可选调试用

        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

        # ✅ 新增：支持检测多个类别
        # 包括：person（0），bicycle（1），car（2），motorcycle（3），bus（5），truck（7）
        self.target_class_ids = [0, 1, 2, 3, 5, 7]

    def set_conf_threshold(self, conf):
        self.conf_threshold = conf
    def detect(self, frame: np.ndarray):
        """
        对图像帧进行行人检测
        :param frame: 原始图像帧 (numpy array, BGR)
        :return: list of dict: [{'bbox': [...], 'conf': float, 'class_name': str}, ...]
        """
        results = self.model.predict(frame, conf=self.conf_threshold, verbose=False)[0]
        detections = []

        for box in results.boxes:
            cls_id = int(box.cls)
            conf = float(box.conf)
            if cls_id in self.target_class_ids:  # ✅ 多类别判断
                x1, y1, x2, y2 = map(float, box.xyxy[0])
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'conf': conf,
                    'class_id': cls_id,  # ✅ 多加一个 class_id 字段
                    'class_name': results.names[cls_id]     # ✅ 保留 class_name
                })

        return detections
