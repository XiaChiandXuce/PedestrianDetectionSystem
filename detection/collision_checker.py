# detection/collision_checker.py

import math

class CollisionChecker:
    def __init__(self, distance_threshold=50):
        """
        初始化碰撞检测器
        :param distance_threshold: 判定为碰撞风险的像素距离阈值
        """
        self.threshold = distance_threshold

    def calculate_center(self, bbox):
        """
        计算目标框的中心点坐标
        :param bbox: 边界框 [x1, y1, x2, y2]
        :return: 中心点 (x, y)
        """
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        return (cx, cy)

    def calculate_distance(self, p1, p2):
        """
        欧几里得距离
        """
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    # ✅ 修改前：
    # def check(self, detections):

    # ✅ 修改后：
    def check(self, pedestrians, vehicles):
        """
        判断是否存在行人与车辆之间的碰撞风险
        :param pedestrians: 行人检测结果列表
        :param vehicles: 车辆检测结果列表
        :return: True（有风险） or False（安全）
        """
        for person in pedestrians:
            center_p = self.calculate_center(person["bbox"])
            for vehicle in vehicles:
                center_v = self.calculate_center(vehicle["bbox"])
                dist = self.calculate_distance(center_p, center_v)
                print(f"📏 行人与车辆中心点距离：{dist:.2f}")  # ✅ 添加此行调试打印

                if dist < self.threshold:
                    print(f"⚠️ 检测到碰撞风险！行人与车辆距离为 {dist:.2f}")
                    return True  # 一旦发现就立即返回

        return False  # 所有行人与车都安全

