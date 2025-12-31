import logging
import os
import shutil
from typing import Any

from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QDesktopServices, QDragEnterEvent, QDropEvent, QIcon, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.worker_background import BackgroundWorker
from src.worker_rembg import RembgWorker

# Configuração de Log
logger = logging.getLogger("FogStripper.MainWindow")

class ProcessThread(QThread):
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    
    # ... (Keep ProcessThread content as is, I am only targeting imports and __init__)
    # Wait, replace_file_content needs contiguous block. 
    # I'll just target the header and __init__ parts separately if needed, 
    # or just the __init__ part for resizing and header for imports.
    # Actually, simplest is to just fix the resize first.
    
# Let's just fix the resize first to be safe.

MODEL_DESCRIPTIONS: dict[str, str] = {
    "u2netp": "Versão 'light' do u2net. Mais rápido, menos detalhe.",
    "u2net": "Modelo de uso geral, bom equilíbrio entre velocidade e precisão.",
    "u2net_human_seg": "Alta precisão, especializado para recortar pessoas.",
    "isnet-general-use": "Moderno e porém pesado, mas com a melhor precisão para objetos.",
}


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
    msg_box.setStyleSheet(
        "QLabel{ min-width: 600px; font-size: 13pt; } QPushButton{ font-size: 13pt; padding: 5px; }"
    )
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
        self.rb_original.setToolTip(
            "Mantém o tamanho original da imagem (ex: 1920x1080), apenas removendo o fundo."
        )

        self.rb_trim = QRadioButton("Ajustar e recortar (Trim)")
        self.rb_trim.setToolTip(
            "Recorta a imagem para conter apenas o objeto, removendo o espaço vazio transparente."
        )

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
        self.btn_process.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold;"
        )

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_process)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def get_crop_option(self) -> str:
        return "trim" if self.rb_trim.isChecked() else "original"

    def get_fill_holes_option(self) -> bool:
        return self.cb_fill_holes.isChecked()


class FogStripperWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("FogStripper")
        self.setWindowTitle("Removedor de Background")
        self.setAcceptDrops(True)
        self.setFixedSize(950, 880)

        self.upscale_factor: int = 0
        self.post_processing_enabled: bool = False
        self.background_type: str = "color"
        self.background_data: str = "#000000"
        self.background_resize_mode: str = "fit-bg-to-fg"
        self.shadow_enabled: bool = False
        self.shadow_blur: int = 15
        self.shadow_opacity: int = 70
        self.crop_option: str = "original"
        self.fill_holes_option: bool = False

        self.video_extensions: tuple[str, ...] = (
            ".mp4", ".mov", ".avi", ".wmv", ".mkv", ".avchd", ".flv", ".webm", ".m4v", ".divx", ".gif"
        )
        self.image_extensions: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".webp")
        self.all_extensions: tuple[str, ...] = self.image_extensions + self.video_extensions

        self.files_to_process: list[str] = []
        self.current_index: int = 0
        self.total_files: int = 0
        self.output_directory: str = ""
        self.thread: ProcessThread | None = None
        self.last_output_path: str = ""

        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.setContentsMargins(20, 10, 20, 10)

        self.icon_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            image = scaled_pixmap.toImage()
            mirrored_image = image.mirrored(True, False)
            self.icon_label.setPixmap(QPixmap.fromImage(mirrored_image))
        header_layout.addWidget(self.icon_label)

        self.title_label = QLabel("FogStripper")
        self.title_label.setStyleSheet("font-size: 22pt; font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()



        main_layout.addLayout(header_layout)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setVisible(False)
        main_layout.addWidget(self.label)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.preview_scroll.setFixedHeight(90)
        self.preview_scroll.setVisible(False)

        self.preview_container = QWidget()
        self.preview_layout = QHBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(5, 5, 5, 5)
        self.preview_layout.setSpacing(10)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.preview_scroll.setWidget(self.preview_container)
        main_layout.addWidget(self.preview_scroll)

        self.setup_main_settings(main_layout)
        self.setup_post_processing_ui(main_layout)

        btn_container = QWidget()
        btn_container_layout = QHBoxLayout(btn_container)
        btn_container_layout.setContentsMargins(30, 0, 30, 0)

        self.button = QPushButton("Selecione ou arraste suas imagens aqui!")
        self.button.setFixedHeight(45)
        self.button.clicked.connect(self.open_files)
        btn_container_layout.addWidget(self.button)
        main_layout.addWidget(btn_container)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.update_model_description(0)

    def setup_main_settings(self, main_layout: QVBoxLayout) -> None:
        # Add spacing below banner/header
        main_layout.addSpacing(20)

        # Container for Arsenal Header + Settings Box
        settings_container = QWidget()
        settings_container_layout = QVBoxLayout(settings_container) 
        settings_container_layout.setContentsMargins(30, 0, 30, 0)
        settings_container_layout.setSpacing(10) # Standardized spacing

        # "Arsenal Neural" Header Layout (Label + Description)
        arsenal_header_layout = QHBoxLayout()
        arsenal_header_layout.setContentsMargins(0, 0, 0, 0)
        arsenal_header_layout.setSpacing(15) # Add spacing between title and desc
        
        arsenal_label = QLabel("Arsenal Neural:")
        arsenal_label.setStyleSheet("font-weight: bold;")
        arsenal_header_layout.addWidget(arsenal_label)
        
        self.model_desc_label = QLabel()
        self.model_desc_label.setWordWrap(True)
        self.model_desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.model_desc_label.setStyleSheet("font-size: 10pt; color: #aaa; margin-left: 60px;") # Increased indent to 60px
        # Add widget with stretch=1 to ensure it takes available space
        arsenal_header_layout.addWidget(self.model_desc_label, 1) 
        
        settings_container_layout.addLayout(arsenal_header_layout)

        # Settings Frame
        settings_frame = QFrame()
        settings_frame.setObjectName("SettingsFrame")
        settings_frame.setStyleSheet(
            "#SettingsFrame { border: 1px solid #555; border-radius: 5px; padding: 10px; }"
        )
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(15, 15, 15, 15)
        settings_layout.setSpacing(10) # Standardized spacing
        
        settings_container_layout.addWidget(settings_frame)
        main_layout.addWidget(settings_container)

        ROW_HEIGHT = 30
        
        # 1. Select Engine Label
        engine_label = QLabel("Selecione o Motor Gráfico:")
        settings_layout.addWidget(engine_label)
        
        # 2. Model Combo
        self.model_combo = QComboBox()
        self.model_combo.setFixedHeight(ROW_HEIGHT)
        self.model_combo.addItems(MODEL_DESCRIPTIONS.keys())
        self.model_combo.currentIndexChanged.connect(self.update_model_description)
        settings_layout.addWidget(self.model_combo)

        # 3. Formato de Saida
        format_label = QLabel("Formato de Saida:")
        settings_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.setFixedHeight(ROW_HEIGHT)
        self.format_combo.addItems(["PNG", "WEBP", "SVG", "GIF"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        settings_layout.addWidget(self.format_combo)

        # 4. Potência (Borda)
        power_label = QLabel("Potência (Borda):")
        settings_layout.addWidget(power_label)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setFixedHeight(ROW_HEIGHT)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        settings_layout.addWidget(self.slider)

        # 5. Bloco (VRAM)
        vram_label = QLabel("Bloco (VRAM):")
        settings_layout.addWidget(vram_label)
        
        self.tile_slider = QSlider(Qt.Orientation.Horizontal)
        self.tile_slider.setFixedHeight(ROW_HEIGHT)
        self.tile_slider.setRange(256, 1024)
        self.tile_slider.setValue(640)
        self.tile_slider.setSingleStep(64)
        self.tile_slider.setToolTip("Blocos menores usam menos VRAM.")
        settings_layout.addWidget(self.tile_slider)

        self.setup_upscale_options(settings_layout)

    def setup_upscale_options(self, layout: QVBoxLayout) -> None:
        self.upscale_group = QGroupBox("Upscale (Melhora na Resolução)")
        self.upscale_group.setMinimumHeight(90) # Increased height to GUARANTEE border visibility
        upscale_layout = QHBoxLayout()
        upscale_layout.setContentsMargins(10, 15, 10, 15)
        self.upscale_group.setLayout(upscale_layout)

        upscale_layout.addStretch(1)

        self.rb_upscale_off = QRadioButton("Off")
        self.rb_upscale_off.setChecked(True)
        self.rb_upscale_off.toggled.connect(lambda: self.on_upscale_change(0))
        upscale_layout.addWidget(self.rb_upscale_off)
        
        upscale_layout.addStretch(1)
        
        self.rb_upscale_2x = QRadioButton("2x")
        self.rb_upscale_2x.toggled.connect(lambda: self.on_upscale_change(2))
        upscale_layout.addWidget(self.rb_upscale_2x)
        
        upscale_layout.addStretch(1)
        
        self.rb_upscale_3x = QRadioButton("3x")
        self.rb_upscale_3x.toggled.connect(lambda: self.on_upscale_change(3))
        upscale_layout.addWidget(self.rb_upscale_3x)
        
        upscale_layout.addStretch(1)
        
        self.rb_upscale_4x = QRadioButton("4x")
        self.rb_upscale_4x.toggled.connect(lambda: self.on_upscale_change(4))
        upscale_layout.addWidget(self.rb_upscale_4x)
        
        upscale_layout.addStretch(1)
        
        layout.addWidget(self.upscale_group)

    def setup_post_processing_ui(self, main_layout: QVBoxLayout) -> None:
        post_container = QWidget()
        post_container_layout = QHBoxLayout(post_container)
        post_container_layout.setContentsMargins(30, 0, 30, 0)

        # Frame for Post Processing Content
        self.post_processing_frame = QFrame()
        self.post_processing_frame.setObjectName("PostProcessingFrame")
        self.post_processing_frame.setStyleSheet(
            "#PostProcessingFrame { border: 1px solid #555; border-radius: 5px; margin-top: 5px; }"
        )
        altar_layout = QVBoxLayout(self.post_processing_frame)

        # Container for Checkbox + Frame
        vertical_wrapper = QWidget()
        vertical_layout = QVBoxLayout(vertical_wrapper)
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_layout.setSpacing(2) # Reduced spacing as requested
        
        self.post_process_checkbox = QCheckBox("Habilitar Pós-Processamento")
        self.post_process_checkbox.toggled.connect(self.toggle_post_processing)
        vertical_layout.addWidget(self.post_process_checkbox)
        vertical_layout.addWidget(self.post_processing_frame)
        
        post_container_layout.addWidget(vertical_wrapper)

        self.tabs = QTabWidget()
        self.tabs.setEnabled(False)
        altar_layout.addWidget(self.tabs)
        self.setup_background_tab()
        self.setup_effects_tab()
        main_layout.addWidget(post_container)

    def setup_background_tab(self) -> None:
        tab = QWidget()
        layout = QGridLayout(tab)

        self.rb_solid_color = QRadioButton("Cor Solida:")
        self.rb_solid_color.setChecked(True)
        self.rb_solid_color.toggled.connect(self.on_background_type_changed)
        self.rb_solid_color.setStyleSheet("margin-left: 20px;")
        layout.addWidget(self.rb_solid_color, 0, 0)

        color_layout = QHBoxLayout()
        color_layout.setSpacing(4)
        color_layout.addStretch() # Push controls to the right
        
        self.btn_choose_color = QPushButton("Personalizar")
        self.btn_choose_color.setFixedSize(150, 28)
        self.btn_choose_color.clicked.connect(self.choose_color)
        self.color_display = QLabel()
        self.color_display.setFixedSize(26, 26)
        self.update_color_display(QColor(self.background_data))
        color_layout.addWidget(self.btn_choose_color)
        color_layout.addWidget(self.color_display)

        self.preset_colors: list[str] = [
            "#282a36", "#44475a", "#f8f8f2", "#6272a4",
            "#8be9fd", "#50fa7b", "#ffb86c", "#ff79c6",
            "#bd93f9", "#ff5555", "#f1fa8c", # Removed last color #21222c to fit width
        ]
        self.color_presets: list[QLabel] = []
        for hex_color in self.preset_colors:
            preset = QLabel()
            preset.setFixedSize(26, 26)
            preset.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #888; border-radius: 3px;")
            preset.setCursor(Qt.CursorShape.PointingHandCursor)
            preset.setToolTip(hex_color)
            preset.mousePressEvent = lambda e, c=hex_color: self.select_preset_color(c)
            color_layout.addWidget(preset)
            self.color_presets.append(preset)
        
        layout.addLayout(color_layout, 0, 1)

        self.rb_image_bg = QRadioButton("Imagem de Fundo:")
        self.rb_image_bg.toggled.connect(self.on_background_type_changed)
        self.rb_image_bg.setStyleSheet("margin-left: 20px;")
        layout.addWidget(self.rb_image_bg, 1, 0)
        
        self.btn_choose_image = QPushButton("Selecionar...")
        self.btn_choose_image.setFixedSize(510, 28) # Exact calculated width (150+26+11*26+12*4 = 510)
        self.btn_choose_image.setEnabled(False)
        self.btn_choose_image.clicked.connect(self.choose_background_image)
        layout.addWidget(self.btn_choose_image, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.bg_resize_group = QGroupBox("Modo de Redimensionamento")
        self.bg_resize_group.setEnabled(False)
        self.bg_resize_group.setMinimumHeight(90) # Match Upscale height
        bg_resize_layout = QHBoxLayout() # Horizontal layout to match Upscale
        bg_resize_layout.setContentsMargins(10, 15, 10, 15) # Match Upscale margins
        self.bg_resize_group.setLayout(bg_resize_layout)

        bg_resize_layout.addStretch(1)
        self.rb_fit_bg = QRadioButton("Ajustar fundo à imagem (Padrão)")
        self.rb_fit_bg.setChecked(True)
        self.rb_fit_bg.toggled.connect(lambda: self.on_resize_mode_change("fit-bg-to-fg"))
        bg_resize_layout.addWidget(self.rb_fit_bg)
        
        bg_resize_layout.addStretch(1)
        
        self.rb_fit_fg = QRadioButton("Manter fundo original (Centralizar imagem)")
        self.rb_fit_fg.toggled.connect(lambda: self.on_resize_mode_change("fit-fg-to-bg"))
        bg_resize_layout.addWidget(self.rb_fit_fg)
        bg_resize_layout.addStretch(1)

        layout.addWidget(self.bg_resize_group, 2, 0, 1, 2)
        self.tabs.addTab(tab, "Fundo")

    def setup_effects_tab(self) -> None:
        tab = QWidget()
        layout = QGridLayout(tab)

        self.shadow_checkbox = QCheckBox("Projetar Sombra Sutil:")
        self.shadow_checkbox.toggled.connect(self.toggle_shadow)
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

    def select_preset_color(self, hex_color: str) -> None:
        self.background_data = hex_color
        self.update_color_display(QColor(hex_color))

    def on_upscale_change(self, value: int) -> None:
        if self.sender().isChecked():
            self.upscale_factor = value

    def on_resize_mode_change(self, mode: str) -> None:
        if self.sender().isChecked():
            self.background_resize_mode = mode

    def toggle_post_processing(self, checked: bool) -> None:
        self.post_processing_enabled = checked
        self.tabs.setEnabled(checked)

    def on_background_type_changed(self) -> None:
        is_image: bool = self.rb_image_bg.isChecked()
        self.background_type = "image" if is_image else "color"
        self.btn_choose_color.setEnabled(not is_image)
        self.btn_choose_image.setEnabled(is_image)
        self.bg_resize_group.setEnabled(is_image)

    def choose_color(self) -> None:
        color = QColorDialog.getColor(QColor(self.background_data))
        if color.isValid():
            self.background_data = color.name()
            self.update_color_display(color)

    def update_color_display(self, color: QColor) -> None:
        pixmap = QPixmap(24, 24)
        pixmap.fill(color)
        self.color_display.setPixmap(pixmap)
        self.color_display.setStyleSheet("border: 1px solid #666; border-radius: 2px;")

    def choose_background_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Imagem de Fundo", "", "Imagens (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self.background_data = path
            self.btn_choose_image.setText(os.path.basename(path))

    def toggle_shadow(self, checked: bool) -> None:
        self.shadow_enabled = checked
        self.blur_slider.setEnabled(checked)
        self.opacity_slider.setEnabled(checked)

    def handle_processing_error(self, error_message: str) -> None:
        self.label.setText("Ocorreu um erro!")
        self.label.setVisible(True)
        self.progress_bar.setVisible(False)
        self.set_controls_enabled(True)
        self.files_to_process.clear()

        error_dialog = create_styled_message_box(
            self, "Erro no Processamento", "Ocorreu um erro.", QMessageBox.Icon.Critical, f"Detalhes: {error_message}"
        )
        save_button = error_dialog.addButton("Salvar Relatório", QMessageBox.ButtonRole.ActionRole)
        error_dialog.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        error_dialog.exec()

        if error_dialog.clickedButton() == save_button:
            self.save_log_file()

    def save_log_file(self) -> None:
        log_path: str = get_log_path()
        if not os.path.exists(log_path):
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Relatório", os.path.expanduser("~/fogstripper_error_report.log"), "Log Files (*.log)"
        )
        if save_path:
            try:
                shutil.copy(log_path, save_path)
            except Exception as e:
                logger.error(f"Falha ao salvar o relatório: {e}")

    def set_controls_enabled(self, enabled: bool) -> None:
        for w in [
            self.button,
            self.model_combo,
            self.format_combo,
            self.slider,
            self.tile_slider,
            self.upscale_group,
            self.post_processing_frame,
        ]:
            w.setEnabled(enabled)
        self.setAcceptDrops(enabled)
        is_animated: bool = any(p.lower().endswith(self.video_extensions) for p in self.files_to_process)
        if is_animated and enabled:
            self.upscale_group.setEnabled(False)
            self.post_processing_frame.setEnabled(False)

    def update_model_description(self, index: int) -> None:
        model_name = self.model_combo.currentText()
        self.model_desc_label.setText(MODEL_DESCRIPTIONS.get(model_name, ""))
        if model_name == "isnet-general-use" and self.format_combo.currentText() != "SVG":
            self.format_combo.blockSignals(True)
            self.format_combo.setCurrentText("SVG")
            self.format_combo.blockSignals(False)

    def on_format_changed(self, format_text: str) -> None:
        if format_text.upper() == "SVG" and self.model_combo.currentText() != "isnet-general-use":
            self.model_combo.blockSignals(True)
            self.model_combo.setCurrentText("isnet-general-use")
            self.model_combo.blockSignals(False)
            self.model_desc_label.setText(MODEL_DESCRIPTIONS.get("isnet-general-use", ""))

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        paths: list[str] = [
            u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile().lower().endswith(self.all_extensions)
        ]
        if paths:
            self.start_file_processing(paths)

    def open_files(self) -> None:
        video_exts: str = " ".join([f"*{ext}" for ext in self.video_extensions])
        image_exts: str = " ".join([f"*{ext}" for ext in self.image_extensions])
        filter_str: str = f"Imagens e Vídeos ({image_exts} {video_exts})"
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecione as Imagens", "", filter_str)
        if paths:
            self.start_file_processing(paths)

    def update_preview(self, paths: list[str]) -> None:
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not paths:
            self.preview_scroll.setVisible(False)
            self.label.setVisible(False)
            return

        self.label.setText(f"{len(paths)} imagem(ns) selecionada(s)")
        self.label.setVisible(True)
        self.preview_scroll.setVisible(True)

        for path in paths[:20]:
            thumb_label = QLabel()
            thumb_label.setFixedSize(70, 70)
            thumb_label.setStyleSheet("border: 1px solid #555; border-radius: 5px;")
            thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            thumb_label.setToolTip(os.path.basename(path))

            if path.lower().endswith(self.image_extensions):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    thumb_label.setPixmap(pixmap.scaled(68, 68, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    thumb_label.setText("IMG")
            else:
                thumb_label.setText("VID")
                thumb_label.setStyleSheet("border: 1px solid #555; border-radius: 5px; background: #333;")

            self.preview_layout.addWidget(thumb_label)

        if len(paths) > 20:
            more_label = QLabel(f"+{len(paths) - 20}")
            more_label.setFixedSize(70, 70)
            more_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            more_label.setStyleSheet("color: #888;")
            self.preview_layout.addWidget(more_label)

    def start_file_processing(self, paths: list[str]) -> None:
        if not paths:
            return
        self.files_to_process = paths
        self.update_preview(paths)
        is_animated: bool = any(p.lower().endswith(self.video_extensions) for p in paths)
        if is_animated:
            self.upscale_group.setEnabled(False)
            self.post_processing_frame.setEnabled(False)
        else:
            self.upscale_group.setEnabled(True)
            self.post_processing_frame.setEnabled(True)

        if is_animated:
            msg_box = create_styled_message_box(self, "Confirmar Processamento", f"Processar {len(paths)} imagem(ns)?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            if msg_box.exec() == QMessageBox.StandardButton.No:
                self.files_to_process.clear()
                return
            self.crop_option = "original"
            self.fill_holes_option = False
        else:
            dialog = ProcessingOptionsDialog(self, len(paths))
            if dialog.exec() == QDialog.DialogCode.Rejected:
                self.files_to_process.clear()
                return
            self.crop_option = dialog.get_crop_option()
            self.fill_holes_option = dialog.get_fill_holes_option()

        self.output_directory = os.path.dirname(paths[0])
        self.total_files = len(paths)
        self.current_index = 0
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.set_controls_enabled(False)
        self.process_next_image()

    def process_next_image(self) -> None:
        if self.current_index < self.total_files:
            path: str = self.files_to_process[self.current_index]
            self.label.setText(f"Processando: {os.path.basename(path)} ({self.current_index + 1}/{self.total_files})")
            self.label.setVisible(True)

            post_opts: dict[str, Any] = {
                "enabled": self.post_processing_enabled,
                "upscale_factor": self.upscale_factor,
                "shadow_enabled": self.shadow_enabled,
                "background_type": self.background_type,
                "background_data": self.background_data,
                "background_resize_mode": self.background_resize_mode,
                "crop_option": self.crop_option,
                "fill_holes": self.fill_holes_option,
            }

            self.thread = ProcessThread(
                input_path=path,
                model_name=self.model_combo.currentText(),
                output_format=self.format_combo.currentText().lower(),
                potencia=self.slider.value(),
                tile_size=self.tile_slider.value(),
                post_processing_opts=post_opts,
            )
            self.thread.progress.connect(self.progress_bar.setValue)
            self.thread.finished.connect(self.finish_image)
            self.thread.error.connect(self.handle_processing_error)
            self.thread.start()
        else:
            self.on_all_files_processed()

    def finish_image(self, output_path: str) -> None:
        self.last_output_path = output_path
        self.current_index += 1
        self.process_next_image()

    def on_all_files_processed(self) -> None:
        self.label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.set_controls_enabled(True)
        self.files_to_process.clear()
        self.update_preview([])

        msg_box = create_styled_message_box(self, "Processo Concluído", "Todas as imagens foram processadas.")

        open_folder_button = msg_box.addButton("Abrir Pasta", QMessageBox.ButtonRole.ActionRole)

        open_image_button = None
        copy_image_button = None

        if self.total_files == 1 and self.last_output_path and os.path.exists(self.last_output_path):
            open_image_button = msg_box.addButton("Abrir Imagem", QMessageBox.ButtonRole.ActionRole)
            copy_image_button = msg_box.addButton("Copiar Imagem", QMessageBox.ButtonRole.ActionRole)

        msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()

        clicked = msg_box.clickedButton()
        if clicked == open_folder_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_directory))
        elif open_image_button and clicked == open_image_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_output_path))
        elif copy_image_button and clicked == copy_image_button:
            self.copy_image_to_clipboard(self.last_output_path)

    def copy_image_to_clipboard(self, path: str) -> None:
        try:
            image = QImage(path)
            if not image.isNull():
                QApplication.clipboard().setImage(image)
            else:
                QMessageBox.warning(self, "Erro", "Falha ao carregar imagem para cópia.")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao copiar imagem: {e}")
