#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication
from gui import DesnudadorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DesnudadorWindow()
    window.show()
    sys.exit(app.exec())
