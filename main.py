# detector.py
from ultralytics import YOLO
import numpy as np
import cv2

class PedestrianDetector:
    def __init__(self, model_path="models/yolo_weights/yolov8n.pt", confidence=0.5):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence

    def set_confidence(self, conf):
        self.confidence_threshold = conf

    def detect(self, frame: np.ndarray):
        """对单帧图像进行检测，返回检测结果"""
        results = self.model(frame)[0]
        detections = []
        for r in results.boxes:
            cls = int(r.cls[0].item())
            conf = float(r.conf[0].item())
            if conf < self.confidence_threshold:
                continue
            xyxy = r.xyxy[0].cpu().numpy().astype(int)  # 坐标
            detections.append({
                "class_id": cls,
                "confidence": conf,
                "bbox": xyxy  # [x1, y1, x2, y2]
            })
        return detections
