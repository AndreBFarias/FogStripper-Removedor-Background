import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


def create_styled_message_box(
    parent: QWidget | None,
    title: str,
    text: str,
    icon: QMessageBox.Icon = QMessageBox.Icon.NoIcon,
    informative_text: str = "",
) -> QMessageBox:
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    if informative_text:
        msg_box.setInformativeText(informative_text)
    msg_box.setIcon(icon)
    msg_box.setStyleSheet("QLabel{ min-width: 600px; font-size: 13pt; } QPushButton{ font-size: 13pt; padding: 5px; }")
    return msg_box


class ProcessingOptionsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, num_files: int = 1) -> None:
        super().__init__(parent)
        self.setWindowTitle("Opções de Processamento")
        self.setFixedSize(500, 300)

        layout = QVBoxLayout(self)

        title = QLabel(f"Deseja processar {num_files} imagem(ns)?")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        group = QGroupBox("Modo de Recorte")
        group_layout = QVBoxLayout(group)

        self.rb_original = QRadioButton("Manter dimensões originais")
        self.rb_original.setChecked(True)
        self.rb_original.setToolTip("Mantém o tamanho original da imagem (ex: 1920x1080), apenas removendo o fundo.")

        self.rb_trim = QRadioButton("Ajustar e recortar (Trim)")
        self.rb_trim.setToolTip("Recorta a imagem para conter apenas o objeto, removendo o espaço vazio transparente.")

        group_layout.addWidget(self.rb_original)
        group_layout.addWidget(self.rb_trim)
        layout.addWidget(group)

        self.cb_fill_holes = QCheckBox("Agir sobre objetos internos?")
        self.cb_fill_holes.setToolTip(
            "Marcado: Preenche buracos internos.\nDesmarcado: Remove ruídos externos (mantém apenas o maior objeto)."
        )
        layout.addWidget(self.cb_fill_holes)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        BTN_WIDTH = 150
        BTN_HEIGHT = 36

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_process = QPushButton("Processar")
        self.btn_process.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        self.btn_process.clicked.connect(self.accept)
        self.btn_process.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_process)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def get_crop_option(self) -> str:
        return "trim" if self.rb_trim.isChecked() else "original"

    def get_fill_holes_option(self) -> bool:
        return self.cb_fill_holes.isChecked()
