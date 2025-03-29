import os
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import QUrl, QObject, pyqtSlot  # ✅ 加入 QObject, pyqtSlot

class SoundManager(QObject):  # ✅ 继承 QObject
    def __init__(self, sound_file="data/sounds/alert.wav", volume=0.9):

        super().__init__()  # ✅ 初始化 QObject 父类

        # 获取当前文件所在目录的“上两级路径”作为项目根路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_path = os.path.join(base_dir, sound_file)

        print(f"[SoundManager] 绝对路径确认: {abs_path}")
        print(f"[SoundManager] 文件存在性: {os.path.exists(abs_path)}")

        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(abs_path))
        self.sound.setLoopCount(1)
        self.sound.setVolume(volume)

        # 标志位：防止重复播放
        self.is_playing = False

        # 信号绑定：播放完成时重置标志位
        self.sound.statusChanged.connect(self.on_status_changed)

    def play_alert(self):
        if not self.is_playing:
            self.is_playing = True
            self.sound.play()
            print("🔊 播放警报声音")

    @pyqtSlot()
    def on_status_changed(self):
        """
        播放完成后，重置播放标志
        注意：QSoundEffect 没有 finished() 信号，只能通过 status 变化 + isPlaying 检查
        """
        if self.sound.status() == QSoundEffect.Status.Ready and not self.sound.isPlaying():
            self.is_playing = False
            print("✅ 播放完成，恢复播放权限")
