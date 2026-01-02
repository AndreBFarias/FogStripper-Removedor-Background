import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.gui.constants import MODEL_DESCRIPTIONS

logger = logging.getLogger(__name__)


class SettingsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)

        arsenal_label = QLabel("Modelo de Processamento:")
        arsenal_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(arsenal_label)

        self.model_desc_label = QLabel()
        self.model_desc_label.setWordWrap(True)
        self.model_desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.model_desc_label.setStyleSheet("font-size: 10pt; color: #aaa; margin-left: 60px;")
        header_layout.addWidget(self.model_desc_label, 1)
        layout.addLayout(header_layout)

        settings_frame = QFrame()
        settings_frame.setObjectName("SettingsFrame")
        settings_frame.setStyleSheet("#SettingsFrame { border: 1px solid #555; border-radius: 5px; padding: 10px; }")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(15, 15, 15, 15)
        settings_layout.setSpacing(10)
        layout.addWidget(settings_frame)

        ROW_HEIGHT = 30

        engine_label = QLabel("Selecione o Motor Grafico:")
        settings_layout.addWidget(engine_label)

        self.model_combo = QComboBox()
        self.model_combo.setFixedHeight(ROW_HEIGHT)
        self.model_combo.addItems(MODEL_DESCRIPTIONS.keys())
        settings_layout.addWidget(self.model_combo)

        format_label = QLabel("Formato de Saida:")
        settings_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.setFixedHeight(ROW_HEIGHT)
        self.format_combo.addItems(["PNG", "WEBP", "SVG", "GIF"])
        settings_layout.addWidget(self.format_combo)

        power_label = QLabel("Potencia (Borda):")
        settings_layout.addWidget(power_label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setFixedHeight(ROW_HEIGHT)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        settings_layout.addWidget(self.slider)

        vram_label = QLabel("Bloco (VRAM):")
        settings_layout.addWidget(vram_label)

        self.tile_slider = QSlider(Qt.Orientation.Horizontal)
        self.tile_slider.setFixedHeight(ROW_HEIGHT)
        self.tile_slider.setRange(256, 1024)
        self.tile_slider.setValue(640)
        self.tile_slider.setSingleStep(64)
        self.tile_slider.setToolTip("Blocos menores usam menos VRAM.")
        settings_layout.addWidget(self.tile_slider)

        self._setup_upscale_options(settings_layout)

    def _setup_upscale_options(self, layout: QVBoxLayout) -> None:
        self.upscale_group = QGroupBox("Upscale (Melhora na Resolucao)")
        self.upscale_group.setFixedHeight(70)
        upscale_layout = QHBoxLayout()
        upscale_layout.setContentsMargins(20, 10, 20, 10)
        upscale_layout.setSpacing(40)
        self.upscale_group.setLayout(upscale_layout)

        self.rb_upscale_off = QRadioButton("Off")
        self.rb_upscale_off.setChecked(True)
        upscale_layout.addWidget(self.rb_upscale_off)

        self.rb_upscale_2x = QRadioButton("2x")
        upscale_layout.addWidget(self.rb_upscale_2x)

        self.rb_upscale_3x = QRadioButton("3x")
        upscale_layout.addWidget(self.rb_upscale_3x)

        self.rb_upscale_4x = QRadioButton("4x")
        upscale_layout.addWidget(self.rb_upscale_4x)

        upscale_layout.addStretch()

        layout.addWidget(self.upscale_group)

    def update_model_description(self, model_name: str) -> None:
        self.model_desc_label.setText(MODEL_DESCRIPTIONS.get(model_name, ""))
