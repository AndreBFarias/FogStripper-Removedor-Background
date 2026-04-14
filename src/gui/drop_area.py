import os
from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.gui.constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS


class DropArea(QFrame):
    def __init__(
        self,
        on_files_added: Callable[[list[str]], None],
        on_process_requested: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_files_added = on_files_added
        self._on_process_requested = on_process_requested
        self._current_files: list[str] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("DropArea")
        self.setFixedHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            #DropArea {
                border: 2px dashed #6272a4;
                border-radius: 10px;
                background: #2a2a2a;
            }
            #DropArea:hover {
                border-color: #bd93f9;
                background: #333;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Área de seleção e preview — expande para preencher o espaço disponível
        left_widget = QWidget()
        left_widget.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.placeholder_label = QLabel("Selecione ou arraste suas imagens aqui!")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("border: none; color: #aaa; font-size: 14px;")
        left_layout.addWidget(self.placeholder_label)

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
        left_layout.addWidget(self.scroll_area)

        main_layout.addWidget(left_widget, 1)

        # Coluna de botões — largura natural, alinhada à direita
        self._buttons_widget = QWidget()
        self._buttons_widget.setStyleSheet("background: transparent;")
        buttons_layout = QVBoxLayout(self._buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_layout.setSpacing(10)

        self.btn_processar = QPushButton("Processar")
        self.btn_processar.setEnabled(False)
        self.btn_processar.setFixedSize(90, 28)
        self.btn_processar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_processar.setStyleSheet("""
            QPushButton {
                background: #50fa7b;
                color: #282a36;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 8px;
            }
            QPushButton:hover { background: #5af78e; }
            QPushButton:disabled { background: #44475a; color: #6272a4; }
        """)
        self.btn_processar.clicked.connect(self._on_processar_clicked)
        buttons_layout.addWidget(self.btn_processar)

        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.setEnabled(False)
        self.btn_limpar.setFixedSize(90, 28)
        self.btn_limpar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpar.setStyleSheet("""
            QPushButton {
                background: #ff5555;
                color: #f8f8f2;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 8px;
            }
            QPushButton:hover { background: #ff6e6e; }
            QPushButton:disabled { background: #44475a; color: #6272a4; }
        """)
        self.btn_limpar.clicked.connect(self.clear)
        buttons_layout.addWidget(self.btn_limpar)

        main_layout.addWidget(self._buttons_widget)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._buttons_widget.geometry().contains(event.pos()):
                self._open_file_dialog()

    def _open_file_dialog(self) -> None:
        video_exts = " ".join([f"*{ext}" for ext in VIDEO_EXTENSIONS])
        image_exts = " ".join([f"*{ext}" for ext in IMAGE_EXTENSIONS])
        filter_str = f"Imagens e Vídeos ({image_exts} {video_exts})"
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecione as Imagens", "", filter_str)
        if paths:
            self._register_files(paths)

    def _register_files(self, paths: list[str]) -> None:
        self._current_files = list(paths)
        self.update_preview(paths)
        self._on_files_added(paths)
        self.btn_processar.setEnabled(True)
        self.btn_limpar.setEnabled(True)

    def add_files(self, paths: list[str]) -> None:
        """Registra arquivos externamente (drag-and-drop na janela principal)."""
        if paths:
            self._register_files(paths)

    def _on_processar_clicked(self) -> None:
        if self._current_files:
            self._on_process_requested()

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
        self._current_files.clear()
        self.btn_processar.setEnabled(False)
        self.btn_limpar.setEnabled(False)
        self.update_preview([])
