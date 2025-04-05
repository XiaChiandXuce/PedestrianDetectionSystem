import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import PedestrianDetectionUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PedestrianDetectionUI()
    win.show()
    sys.exit(app.exec())
