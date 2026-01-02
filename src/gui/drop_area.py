import os
from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.gui.constants import ALL_EXTENSIONS, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS


class DropArea(QFrame):
    def __init__(self, on_files_selected: Callable[[list[str]], None]) -> None:
        super().__init__()
        self._on_files_selected = on_files_selected
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("DropArea")
        self.setFixedHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            #DropArea {
                border: 2px dashed #555;
                border-radius: 10px;
                background: #2a2a2a;
            }
            #DropArea:hover {
                border-color: #777;
                background: #333;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.placeholder_label = QLabel("Selecione ou arraste suas imagens aqui!")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("border: none; color: #aaa; font-size: 14px;")
        layout.addWidget(self.placeholder_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")
        self.scroll_area.setVisible(False)

        self.preview_container = QWidget()
        self.preview_container.setStyleSheet("background: transparent;")
        self.preview_layout = QHBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(8)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.scroll_area.setWidget(self.preview_container)
        layout.addWidget(self.scroll_area)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._open_file_dialog()

    def _open_file_dialog(self) -> None:
        video_exts = " ".join([f"*{ext}" for ext in VIDEO_EXTENSIONS])
        image_exts = " ".join([f"*{ext}" for ext in IMAGE_EXTENSIONS])
        filter_str = f"Imagens e Videos ({image_exts} {video_exts})"
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecione as Imagens", "", filter_str)
        if paths:
            self._on_files_selected(paths)

    def update_preview(self, paths: list[str]) -> None:
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not paths:
            self.placeholder_label.setVisible(True)
            self.scroll_area.setVisible(False)
            return

        self.placeholder_label.setVisible(False)
        self.scroll_area.setVisible(True)

        for path in paths[:15]:
            thumb = QLabel()
            thumb.setFixedSize(70, 70)
            thumb.setStyleSheet("border: 1px solid #555; border-radius: 5px; background: #222;")
            thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            thumb.setToolTip(os.path.basename(path))

            if path.lower().endswith(IMAGE_EXTENSIONS):
                pix = QPixmap(path)
                if not pix.isNull():
                    thumb.setPixmap(
                        pix.scaled(
                            68,
                            68,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                else:
                    thumb.setText("IMG")
            else:
                thumb.setText("VID")

            self.preview_layout.addWidget(thumb)

        if len(paths) > 15:
            more = QLabel(f"+{len(paths) - 15}")
            more.setFixedSize(70, 70)
            more.setAlignment(Qt.AlignmentFlag.AlignCenter)
            more.setStyleSheet("color: #888; border: none;")
            self.preview_layout.addWidget(more)

    def clear(self) -> None:
        self.update_preview([])
