# **🚀 Pedestrian Detection System - README**

> **"一个好的 README，不是告诉你‘代码怎么运行’，而是告诉你‘为什么这样设计’。"**  
> —— **徐策**
>  
> **"如果 README 不能让人 5 分钟内理解系统核心，那它就是失败的。"**  
> —— **夏驰**

---

## **📌 项目介绍**
本项目 **Pedestrian Detection System** 是一个 **基于深度学习** 的行人检测系统，具备 **多尺度检测、姿态不变性、复杂背景适应、碰撞预警** 等核心功能。  
系统采用 **PyQt6** 作为前端界面，**YOLOv8** 作为行人检测模型，并支持 **实时视频流、用户交互与数据管理**。

---

## **📌 目录结构**
```plaintext
pedestrian_detection_system/  
│── main.py                # 入口文件，启动 PyQt6 界面
│
├── logs/                 # 🧾 日志记录（系统检测 & 报警行为）日志记录目录，自动保存每次检测与报警事件，便于后期排查与溯源
│  
├── ui/                    # 🎨 界面模块
│   ├── layout/            # 存放 .ui 文件
│   │    ├── main_window.ui  # 主窗口 UI
│   ├── main_window.py      # PyQt6 交互逻辑
│   │── log_viewer.py       # 📖 日志查看窗口
│   └── log_statistics_window.py  # 📊 日志趋势分析窗口（新增）
│
├── managers/
│   ├── sound_manager.py          # 所有声音控制逻辑
│   ├── alert_manager.py          # 所有弹窗/报警控制
│   ├── log_manager.py            # 日志记录统一管理
│   ├── settings_manager.py       # 统一存取配置项
│
├── detection/              # 🔍 目标检测（YOLOv8 + 预处理）
│   ├── detector.py         # 行人检测模型封装（调用 YOLOv8）
│   ├── preprocess.py       # 数据预处理（亮度增强、畸变矫正）
│   ├── tracker.py          # 目标跟踪（后续优化） 
│   └── collision_checker.py  # ✅ 🚦碰撞检测模块（新增）     
│
├── utils/                  # ⚙️ 工具模块
│   ├── config.py           # 配置文件（模型参数、路径等）
│   ├── logger.py           # 日志管理
│
├── models/                 # 🧠 预训练模型
│   ├── yolo_weights/       # YOLOv8 预训练权重
│
├── data/                   # 📂 测试数据
│   ├── test_images/        # 测试图片
│   ├── test_videos/        # 测试视频
│   └── sounds/             # 所有声音资源放这里
│       └── alert.wav           
│
├── docs/                   # 📖 文档管理
│   ├── README.md           # 详细文档
│   ├── architecture.md     # 系统架构设计
│   ├── database.md         # 数据存储方案
│   ├── yolo_optimization.md # YOLOv8 调优记录
│   └── 更新日志.md          # 更新日志于3.29日添加
│
├── requirements.txt        # 🔗 依赖库
└── README.md               # 📌 项目说明文档

```

---

## **📌 功能说明**

### ✅ 行人检测  
- 使用 **YOLOv8** 实现行人和车辆目标检测  
- 支持 **实时视频流输入** 与 **本地视频分析**

### ✅ 多尺度检测  
- 原生支持多尺度特征提取  
- 提升远距离小目标的检测能力

### ✅ 姿态不变性  
- 鲁棒适应行人 **行走、奔跑、侧身、倒地** 等多种姿态

### ✅ 复杂背景适应  
- 适用于 **街道、树木、人群、建筑** 等复杂背景场景

### ✅ 用户界面  
- 采用 **PyQt6** 开发 GUI  
- 支持 **视频显示、滑块调参、日志查看**

### ✅ 数据管理  
- 检测结果自动写入日志  
- 支持 **时间追踪、类别记录、行为统计**

### ✅ 碰撞预警模块（🚦已集成）  
- 📦 模块文件：`detection/collision_checker.py`  
- 🎯 功能：实时计算**行人与车辆**之间的中心点距离  
- 📏 **阈值可调**：通过 GUI 滑块调整距离阈值  
- ⚠️ **触发逻辑**：一旦距离小于阈值，立即 **触发声音报警 + 日志记录**
- 
### 📊 报警趋势统计（更新）

- 📦 模块文件：`ui/log_statistics_window.py`
- 📈 折线图展示 **每分钟报警次数**
- 🔄 自动读取 `logs/` 目录下最新的日志文件，进行分钟级聚合分析
- ✅ 图表支持中文字体，防止乱码问题（如“报警次数”、“时间”等）
- 🖼️ 实现基于 `matplotlib` + `PyQt6` 的嵌入式图形展示


### ✅ 日志记录功能  
- 每帧检测信息与每次预警事件都会自动保存  
- 日志文件位于 `logs/` 目录中，格式为 `.csv`，支持后续分析与报告生成
---

## **📌 依赖安装**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

---

## **📌 运行方式**
```bash
# 运行 PyQt6 界面
python main.py
```

---

## **📌 主要技术**
| **类别** | **使用技术** |
|------|------|
| **前端** | PyQt6 |
| **目标检测** | YOLOv8 |
| **深度学习框架** | PyTorch |
| **图像处理** | OpenCV |
| **数据管理** | SQLite / JSON |
| **日志管理** | Python logging |

---

## **📌 论文优化点**
本系统后续将优化 **10 篇论文中的核心技术**，包括：
1. **YOLOv8-Large 优化**（提高检测精度）
2. **DCGAN 数据增强**（提高远距离行人检测能力）
3. **多网络融合**（提升复杂场景适应能力）
4. **深度强化学习（DRL）**（实现动态调整检测策略）
5. **亮度感知机制**（解决日夜检测问题）
6. **碰撞预警优化**（提高智能交通安全性）
7. **多尺度特征提取**（提升小目标检测能力）
8. **目标跟踪优化**（提升跟踪稳定性）
9. **边缘计算部署**（优化低功耗设备上的运行）
10. **全景检测**（适应鱼眼摄像头等特殊场景）

---

## **📌 未来优化方向**
1. **优化检测速度**：加入 **TensorRT** 或 **ONNX 加速推理**。
2. **支持行人 Re-ID**：识别 **同一行人** 在不同摄像头下的匹配情况。
3. **交通灯检测 & 行人行为分析**：适用于智能交通系统。
4. **云端 & 边缘计算协同**：支持 **Jetson Nano / Raspberry Pi** 部署。
5. **与自动驾驶系统集成**：增强车辆行人检测能力。

---

## **📌 贡献者**
- **开发 & 架构设计**：唐英昊
- **文档优化 & 论文集成**：唐英昊
- **算法优化 & 深度学习**：唐英昊
- **前端 UI & 用户体验**：唐英昊

---
