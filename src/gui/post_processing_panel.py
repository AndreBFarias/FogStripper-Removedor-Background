import logging
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.gui.constants import PRESET_COLORS

logger = logging.getLogger(__name__)


class PostProcessingPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.background_type: str = "color"
        self.background_data: str = "#000000"
        self.background_resize_mode: str = "fit-bg-to-fg"
        self.shadow_enabled: bool = False
        self.shadow_blur: int = 15
        self.shadow_opacity: int = 70
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 0, 30, 0)

        self.frame = QFrame()
        self.frame.setObjectName("PostProcessingFrame")
        self.frame.setStyleSheet(
            "#PostProcessingFrame { border: 1px solid #555; border-radius: 5px; margin-top: 5px; }"
        )
        altar_layout = QVBoxLayout(self.frame)

        vertical_wrapper = QWidget()
        vertical_layout = QVBoxLayout(vertical_wrapper)
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_layout.setSpacing(2)

        self.checkbox = QCheckBox("Habilitar Pos-Processamento")
        vertical_layout.addWidget(self.checkbox)
        vertical_layout.addWidget(self.frame)

        layout.addWidget(vertical_wrapper)

        self.tabs = QTabWidget()
        self.tabs.setEnabled(False)
        altar_layout.addWidget(self.tabs)

        self._setup_background_tab()
        self._setup_effects_tab()

        self.checkbox.toggled.connect(self._on_toggle)

    def _on_toggle(self, checked: bool) -> None:
        self.tabs.setEnabled(checked)

    def _setup_background_tab(self) -> None:
        tab = QWidget()
        layout = QGridLayout(tab)

        self.rb_solid_color = QRadioButton("Cor Solida:")
        self.rb_solid_color.setChecked(True)
        self.rb_solid_color.toggled.connect(self._on_background_type_changed)
        self.rb_solid_color.setStyleSheet("margin-left: 20px;")
        layout.addWidget(self.rb_solid_color, 0, 0)

        color_layout = QHBoxLayout()
        color_layout.setSpacing(4)
        color_layout.addStretch()

        self.btn_choose_color = QPushButton("Personalizar")
        self.btn_choose_color.setFixedSize(150, 28)
        self.btn_choose_color.clicked.connect(self._choose_color)

        self.color_display = QLabel()
        self.color_display.setFixedSize(26, 26)
        self._update_color_display(QColor(self.background_data))

        color_layout.addWidget(self.btn_choose_color)
        color_layout.addWidget(self.color_display)

        self.color_presets: list[QLabel] = []
        for hex_color in PRESET_COLORS:
            preset = QLabel()
            preset.setFixedSize(26, 26)
            preset.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #888; border-radius: 3px;")
            preset.setCursor(Qt.CursorShape.PointingHandCursor)
            preset.setToolTip(hex_color)
            preset.mousePressEvent = lambda e, c=hex_color: self._select_preset_color(c)
            color_layout.addWidget(preset)
            self.color_presets.append(preset)

        layout.addLayout(color_layout, 0, 1)

        self.rb_image_bg = QRadioButton("Imagem de Fundo:")
        self.rb_image_bg.toggled.connect(self._on_background_type_changed)
        self.rb_image_bg.setStyleSheet("margin-left: 20px;")
        layout.addWidget(self.rb_image_bg, 1, 0)

        self.btn_choose_image = QPushButton("Selecionar...")
        self.btn_choose_image.setFixedSize(510, 28)
        self.btn_choose_image.setEnabled(False)
        self.btn_choose_image.clicked.connect(self._choose_background_image)
        layout.addWidget(self.btn_choose_image, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.bg_resize_group = QGroupBox("Modo de Redimensionamento")
        self.bg_resize_group.setEnabled(False)
        self.bg_resize_group.setMinimumHeight(90)
        bg_resize_layout = QHBoxLayout()
        bg_resize_layout.setContentsMargins(10, 15, 10, 15)
        self.bg_resize_group.setLayout(bg_resize_layout)

        bg_resize_layout.addStretch(1)
        self.rb_fit_bg = QRadioButton("Ajustar fundo a imagem (Padrao)")
        self.rb_fit_bg.setChecked(True)
        self.rb_fit_bg.toggled.connect(lambda: self._on_resize_mode_change("fit-bg-to-fg"))
        bg_resize_layout.addWidget(self.rb_fit_bg)

        bg_resize_layout.addStretch(1)

        self.rb_fit_fg = QRadioButton("Manter fundo original (Centralizar imagem)")
        self.rb_fit_fg.toggled.connect(lambda: self._on_resize_mode_change("fit-fg-to-bg"))
        bg_resize_layout.addWidget(self.rb_fit_fg)
        bg_resize_layout.addStretch(1)

        layout.addWidget(self.bg_resize_group, 2, 0, 1, 2)
        self.tabs.addTab(tab, "Fundo")

    def _setup_effects_tab(self) -> None:
        tab = QWidget()
        layout = QGridLayout(tab)

        self.shadow_checkbox = QCheckBox("Projetar Sombra Sutil:")
        self.shadow_checkbox.toggled.connect(self._toggle_shadow)
        layout.addWidget(self.shadow_checkbox, 0, 0, 1, 2)

        layout.addWidget(QLabel("Desfoque:"), 1, 0)
        self.blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_slider.setRange(0, 50)
        self.blur_slider.setValue(self.shadow_blur)
        self.blur_slider.valueChanged.connect(lambda v: setattr(self, "shadow_blur", v))
        self.blur_slider.setEnabled(False)
        layout.addWidget(self.blur_slider, 1, 1)

        layout.addWidget(QLabel("Opacidade:"), 2, 0)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.shadow_opacity)
        self.opacity_slider.valueChanged.connect(lambda v: setattr(self, "shadow_opacity", v))
        self.opacity_slider.setEnabled(False)
        layout.addWidget(self.opacity_slider, 2, 1)

        self.tabs.addTab(tab, "Efeitos")

    def _select_preset_color(self, hex_color: str) -> None:
        self.background_data = hex_color
        self._update_color_display(QColor(hex_color))

    def _on_resize_mode_change(self, mode: str) -> None:
        if self.sender().isChecked():
            self.background_resize_mode = mode

    def _on_background_type_changed(self) -> None:
        is_image: bool = self.rb_image_bg.isChecked()
        self.background_type = "image" if is_image else "color"
        self.btn_choose_color.setEnabled(not is_image)
        self.btn_choose_image.setEnabled(is_image)
        self.bg_resize_group.setEnabled(is_image)

    def _choose_color(self) -> None:
        color = QColorDialog.getColor(QColor(self.background_data))
        if color.isValid():
            self.background_data = color.name()
            self._update_color_display(color)

    def _update_color_display(self, color: QColor) -> None:
        pixmap = QPixmap(24, 24)
        pixmap.fill(color)
        self.color_display.setPixmap(pixmap)
        self.color_display.setStyleSheet("border: 1px solid #666; border-radius: 2px;")

    def _choose_background_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Imagem de Fundo", "", "Imagens (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self.background_data = path
            self.btn_choose_image.setText(os.path.basename(path))

    def _toggle_shadow(self, checked: bool) -> None:
        self.shadow_enabled = checked
        self.blur_slider.setEnabled(checked)
        self.opacity_slider.setEnabled(checked)

    def is_enabled(self) -> bool:
        return self.checkbox.isChecked()

    def get_options(self) -> dict:
        return {
            "background_type": self.background_type,
            "background_data": self.background_data,
            "background_resize_mode": self.background_resize_mode,
            "shadow_enabled": self.shadow_enabled,
        }
