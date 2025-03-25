import os
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl


class SoundManager:
    def __init__(self, sound_file="data/sounds/alert.wav", volume=0.9):
        # 获取当前文件所在目录的“上两级路径”作为项目根路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_path = os.path.join(base_dir, sound_file)

        print(f"[SoundManager] 绝对路径确认: {abs_path}")
        print(f"[SoundManager] 文件存在性: {os.path.exists(abs_path)}")

        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(abs_path))
        self.sound.setLoopCount(1)
        self.sound.setVolume(volume)

    def play_alert(self):
        if self.sound.isLoaded():
            self.sound.play()
