# detector.py
from ultralytics import YOLO
import numpy as np

class YOLOv8Detector:
    def __init__(self, model_path: str = 'models/yolo_weights/yolov8n.pt', conf_threshold: float = 0.5):
        """
        初始化检测器，加载模型
        :param model_path: 模型权重路径
        :param conf_threshold: 置信度阈值
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.target_class_id = 0  # YOLO中 'person' 的类别编号为 0

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
            if cls_id == self.target_class_id:
                x1, y1, x2, y2 = map(float, box.xyxy[0])
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'conf': conf,
                    'class_name': results.names[cls_id]
                })

        return detections
