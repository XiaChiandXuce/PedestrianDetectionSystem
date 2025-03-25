from ultralytics import YOLO

# 1. 加载模型
model = YOLO("models/yolo_weights/yolov8n.pt")

# 2. 使用绝对路径读取图片并进行预测
image_path = r"D:\备份资料\develop\Pythoncode\PedestrianDetectionSystem\data\test_images\test1.jpg"

# 3. 预测并显示结果
results = model(image_path, show=True)

# 4. （可选）打印结果中的预测框信息
for result in results:
    boxes = result.boxes
    for box in boxes:
        print(f"置信度: {box.conf[0]:.2f}, 类别: {int(box.cls[0])}, 坐标: {box.xyxy[0].tolist()}")
