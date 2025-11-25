import os
import logging
import shutil
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, 
                             QMessageBox, QProgressBar, QSlider, QFrame, 
                             QGridLayout, QComboBox, QCheckBox, QTabWidget,
                             QRadioButton, QHBoxLayout, QGroupBox, QDialog, QButtonGroup)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QColor
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QColorDialog
from processor import ProcessThread
from logger_config import get_log_path

logger = logging.getLogger(__name__)

MODEL_DESCRIPTIONS = {
    "u2netp": "Versão 'light' do u2net. Mais rápido, menos detalhe.",
    "u2net": "Modelo de uso geral, bom equilíbrio entre velocidade e precisão.",    
    "u2net_human_seg": "Alta precisão, especializado para recortar pessoas.",
    "isnet-general-use": "Moderno e porém pesado, mas com a melhor precisão para objetos."
}

def create_styled_message_box(parent, title, text, icon=QMessageBox.Icon.NoIcon, informative_text=""):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    if informative_text:
        msg_box.setInformativeText(informative_text)
    msg_box.setIcon(icon)
    msg_box.setStyleSheet("QLabel{ min-width: 600px; font-size: 13pt; } QPushButton{ font-size: 13pt; padding: 5px; }")
    return msg_box

class ProcessingOptionsDialog(QDialog):
    def __init__(self, parent=None, num_files=1):
        super().__init__(parent)
        self.setWindowTitle("Opções de Processamento")
        self.setFixedSize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"Deseja processar {num_files} imagem(ns)?")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Options Group
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
        
        # Fill Holes Option
        self.cb_fill_holes = QCheckBox("Agir sobre objetos internos?")
        self.cb_fill_holes.setToolTip("Marcado: Preenche buracos internos.\nDesmarcado: Remove ruídos externos (mantém apenas o maior objeto).")
        layout.addWidget(self.cb_fill_holes)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_process = QPushButton("Processar")
        self.btn_process.clicked.connect(self.accept)
        self.btn_process.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_process)
        layout.addLayout(btn_layout)
        
    def get_crop_option(self):
        return 'trim' if self.rb_trim.isChecked() else 'original'
        
    def get_fill_holes_option(self):
        return self.cb_fill_holes.isChecked()

class DesnudadorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("FogStripper")
        self.setWindowTitle("FogStripper")
        self.setAcceptDrops(True)
        self.setFixedSize(800, 850)
        
        # --- Estados da Janela ---
        self.upscale_factor = 4
        self.post_processing_enabled = False
        self.background_type = 'color'
        self.background_data = '#000000'
        self.background_resize_mode = 'fit-bg-to-fg'
        self.shadow_enabled = False
        self.shadow_blur = 15
        self.shadow_opacity = 70
        self.crop_option = 'original'

        self.files_to_process = []
        self.current_index = 0
        self.total_files = 0
        self.output_directory = ""
        self.thread = None

        # --- Construção da UI ---
        main_layout = QVBoxLayout(self)
        
        self.icon_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')
        pixmap = QPixmap(logo_path)
        self.icon_label.setPixmap(pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.icon_label)
        
        self.label = QLabel("Arraste e solte as imagens aqui")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label)
        
        self.setup_main_settings(main_layout)
        self.setup_post_processing_ui(main_layout)

        main_layout.addStretch()
        
        self.button = QPushButton("Selecione as Imagens")
        self.button.clicked.connect(self.open_files)
        main_layout.addWidget(self.button)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.update_model_description(0)

    def setup_main_settings(self, main_layout):
        settings_frame = QFrame()
        main_layout.addWidget(settings_frame)
        settings_layout = QGridLayout(settings_frame)
        settings_layout.setContentsMargins(50, 5, 50, 5)

        settings_layout.addWidget(QLabel("Arsenal Neural:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(MODEL_DESCRIPTIONS.keys())
        self.model_combo.currentIndexChanged.connect(self.update_model_description)
        settings_layout.addWidget(self.model_combo, 0, 1)

        self.model_desc_label = QLabel()
        self.model_desc_label.setWordWrap(True)
        self.model_desc_label.setStyleSheet("font-size: 10pt; color: #aaa;")
        settings_layout.addWidget(self.model_desc_label, 1, 0, 1, 2)

        settings_layout.addWidget(QLabel("Formato de Saída:"), 2, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "WEBP", "SVG", "GIF"])
        settings_layout.addWidget(self.format_combo, 2, 1)

        settings_layout.addWidget(QLabel("Potência (Borda):"), 3, 0)
        self.slider = QSlider(Qt.Orientation.Horizontal); self.slider.setRange(0, 100); self.slider.setValue(75)
        settings_layout.addWidget(self.slider, 3, 1)

        settings_layout.addWidget(QLabel("Bloco (VRAM):"), 4, 0)
        self.tile_slider = QSlider(Qt.Orientation.Horizontal); self.tile_slider.setRange(256, 1024); self.tile_slider.setValue(512); self.tile_slider.setSingleStep(64)
        self.tile_slider.setToolTip("Blocos menores usam menos VRAM.")
        settings_layout.addWidget(self.tile_slider, 4, 1)

        self.setup_upscale_options(settings_layout)

    def setup_upscale_options(self, layout):
        self.upscale_group = QGroupBox("Upscale (Melhora na Resolução)")
        upscale_layout = QHBoxLayout(); self.upscale_group.setLayout(upscale_layout)
        
        self.rb_upscale_off = QRadioButton("Off"); self.rb_upscale_off.toggled.connect(lambda: self.on_upscale_change(0))
        self.rb_upscale_2x = QRadioButton("2x"); self.rb_upscale_2x.toggled.connect(lambda: self.on_upscale_change(2))
        self.rb_upscale_3x = QRadioButton("3x"); self.rb_upscale_3x.toggled.connect(lambda: self.on_upscale_change(3))
        self.rb_upscale_4x = QRadioButton("4x"); self.rb_upscale_4x.setChecked(True); self.rb_upscale_4x.toggled.connect(lambda: self.on_upscale_change(4))
        
        upscale_layout.addWidget(self.rb_upscale_off); upscale_layout.addWidget(self.rb_upscale_2x)
        upscale_layout.addWidget(self.rb_upscale_3x); upscale_layout.addWidget(self.rb_upscale_4x)
        layout.addWidget(self.upscale_group, 5, 0, 1, 2)

    def setup_post_processing_ui(self, main_layout):
        self.post_processing_frame = QFrame(); self.post_processing_frame.setObjectName("PostProcessingFrame")
        self.post_processing_frame.setStyleSheet("#PostProcessingFrame { border: 1px solid #555; border-radius: 5px; margin-top: 5px; }")
        altar_layout = QVBoxLayout(self.post_processing_frame)
        
        self.post_process_checkbox = QCheckBox("Habilitar Pós-Processamento")
        self.post_process_checkbox.toggled.connect(self.toggle_post_processing)
        altar_layout.addWidget(self.post_process_checkbox)
        
        self.tabs = QTabWidget(); self.tabs.setEnabled(False)
        altar_layout.addWidget(self.tabs)
        self.setup_background_tab(); self.setup_effects_tab()
        main_layout.addWidget(self.post_processing_frame)

    def setup_background_tab(self):
        tab = QWidget(); layout = QGridLayout(tab)
        self.rb_solid_color = QRadioButton("Cor Sólida"); self.rb_solid_color.setChecked(True); self.rb_solid_color.toggled.connect(self.on_background_type_changed)
        layout.addWidget(self.rb_solid_color, 0, 0)
        color_layout = QHBoxLayout(); self.btn_choose_color = QPushButton("Escolher Cor"); self.btn_choose_color.clicked.connect(self.choose_color)
        self.color_display = QLabel(); self.color_display.setFixedSize(24, 24); self.update_color_display(QColor(self.background_data))
        color_layout.addWidget(self.btn_choose_color); color_layout.addWidget(self.color_display); color_layout.addStretch()
        layout.addLayout(color_layout, 0, 1)
        self.rb_image_bg = QRadioButton("Imagem"); self.rb_image_bg.toggled.connect(self.on_background_type_changed)
        layout.addWidget(self.rb_image_bg, 1, 0)
        self.btn_choose_image = QPushButton("Selecionar Imagem..."); self.btn_choose_image.setEnabled(False); self.btn_choose_image.clicked.connect(self.choose_background_image)
        layout.addWidget(self.btn_choose_image, 1, 1)
        self.bg_resize_group = QGroupBox("Modo de Redimensionamento"); self.bg_resize_group.setEnabled(False); bg_resize_layout = QVBoxLayout(); self.bg_resize_group.setLayout(bg_resize_layout)
        self.rb_fit_bg = QRadioButton("Ajustar fundo à imagem (Padrão)"); self.rb_fit_bg.setChecked(True); self.rb_fit_bg.toggled.connect(lambda: self.on_resize_mode_change('fit-bg-to-fg'))
        self.rb_fit_fg = QRadioButton("Manter fundo original (Centralizar imagem)"); self.rb_fit_fg.toggled.connect(lambda: self.on_resize_mode_change('fit-fg-to-bg'))
        bg_resize_layout.addWidget(self.rb_fit_bg); bg_resize_layout.addWidget(self.rb_fit_fg)
        layout.addWidget(self.bg_resize_group, 2, 0, 1, 2)
        self.tabs.addTab(tab, "Fundo")

    def setup_effects_tab(self):
        tab = QWidget(); layout = QGridLayout(tab)
        self.shadow_checkbox = QCheckBox("Projetar Sombra Sutil"); self.shadow_checkbox.toggled.connect(self.toggle_shadow)
        layout.addWidget(self.shadow_checkbox, 0, 0, 1, 2)
        layout.addWidget(QLabel("Desfoque:"), 1, 0)
        self.blur_slider = QSlider(Qt.Orientation.Horizontal); self.blur_slider.setRange(0, 50); self.blur_slider.setValue(self.shadow_blur); self.blur_slider.valueChanged.connect(lambda v: setattr(self, 'shadow_blur', v)); self.blur_slider.setEnabled(False)
        layout.addWidget(self.blur_slider, 1, 1)
        layout.addWidget(QLabel("Opacidade:"), 2, 0)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal); self.opacity_slider.setRange(0, 100); self.opacity_slider.setValue(self.shadow_opacity); self.opacity_slider.valueChanged.connect(lambda v: setattr(self, 'shadow_opacity', v)); self.opacity_slider.setEnabled(False)
        layout.addWidget(self.opacity_slider, 2, 1)
        self.tabs.addTab(tab, "Efeitos")

    def on_upscale_change(self, value):
        if self.sender().isChecked(): self.upscale_factor = value
    def on_resize_mode_change(self, mode):
        if self.sender().isChecked(): self.background_resize_mode = mode
    def toggle_post_processing(self, checked):
        self.post_processing_enabled = checked; self.tabs.setEnabled(checked)
    def on_background_type_changed(self):
        is_image = self.rb_image_bg.isChecked()
        self.background_type = 'image' if is_image else 'color'
        self.btn_choose_color.setEnabled(not is_image); self.btn_choose_image.setEnabled(is_image); self.bg_resize_group.setEnabled(is_image)
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.background_data)); 
        if color.isValid(): self.background_data = color.name(); self.update_color_display(color)
    def update_color_display(self, color):
        pixmap = QPixmap(24, 24); pixmap.fill(color); self.color_display.setPixmap(pixmap)
        self.color_display.setStyleSheet(f"border: 1px solid #888; border-radius: 4px;")
    def choose_background_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem de Fundo", "", "Imagens (*.png *.jpg *.jpeg *.webp)")
        if path: self.background_data = path; self.btn_choose_image.setText(os.path.basename(path))
    def toggle_shadow(self, checked):
        self.shadow_enabled = checked; self.blur_slider.setEnabled(checked); self.opacity_slider.setEnabled(checked)

    def handle_processing_error(self, error_message):
        self.label.setText("Ocorreu um erro!"); self.progress_bar.setVisible(False)
        self.set_controls_enabled(True); self.files_to_process.clear()
        error_dialog = create_styled_message_box(self, "Erro no Processamento", "Ocorreu um erro.", QMessageBox.Icon.Critical, f"Detalhes: {error_message}")
        save_button = error_dialog.addButton("Salvar Relatório", QMessageBox.ButtonRole.ActionRole)
        error_dialog.addButton("OK", QMessageBox.ButtonRole.AcceptRole); error_dialog.exec()
        if error_dialog.clickedButton() == save_button: self.save_log_file()
    
    def save_log_file(self):
        log_path = get_log_path()
        if not os.path.exists(log_path): return
        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório", os.path.expanduser("~/fogstripper_error_report.log"), "Log Files (*.log)")
        if save_path:
            try: shutil.copy(log_path, save_path)
            except Exception as e: logger.error(f"Falha ao salvar o relatório: {e}")

    def set_controls_enabled(self, enabled):
        for w in [self.button, self.model_combo, self.format_combo, self.slider, self.tile_slider, self.upscale_group, self.post_processing_frame]: w.setEnabled(enabled)
        self.setAcceptDrops(enabled)
        is_animated = any(p.lower().endswith(('.gif', '.webm')) for p in self.files_to_process)
        if is_animated and enabled: self.upscale_group.setEnabled(False); self.post_processing_frame.setEnabled(False)

    def update_model_description(self, index): self.model_desc_label.setText(MODEL_DESCRIPTIONS.get(self.model_combo.currentText(), ""))
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
    def dropEvent(self, event: QDropEvent):
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.webm'))]
        if paths: self.start_file_processing(paths)
    def open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecione as Imagens", "", "Imagens (*.png *.jpg *.jpeg *.webp *.gif *.webm)")
        if paths: self.start_file_processing(paths)

    def start_file_processing(self, paths):
        if not paths: return
        self.files_to_process = paths
        is_animated = any(p.lower().endswith(('.gif', '.webm')) for p in paths)
        if is_animated: self.upscale_group.setEnabled(False); self.post_processing_frame.setEnabled(False)
        else: self.upscale_group.setEnabled(True); self.post_processing_frame.setEnabled(True)
        
        if is_animated:
            # Para animações, usa o diálogo simples padrão
            msg_box = create_styled_message_box(self, 'Confirmar Processamento', f"Processar {len(paths)} imagem(ns)?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No); msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            if msg_box.exec() == QMessageBox.StandardButton.No: self.files_to_process.clear(); return
            self.crop_option = 'original' # Animações não suportam crop por enquanto
            self.fill_holes_option = False
        else:
            # Para imagens estáticas, usa o novo diálogo com opções
            dialog = ProcessingOptionsDialog(self, len(paths))
            if dialog.exec() == QDialog.DialogCode.Rejected:
                self.files_to_process.clear()
                return
            self.crop_option = dialog.get_crop_option()
            self.fill_holes_option = dialog.get_fill_holes_option()

        self.output_directory = os.path.dirname(paths[0]); self.total_files = len(paths); self.current_index = 0
        self.progress_bar.setValue(0); self.progress_bar.setVisible(True)
        self.set_controls_enabled(False); self.process_next_image()

    def process_next_image(self):
        if self.current_index < self.total_files:
            path = self.files_to_process[self.current_index]
            self.label.setText(f"Processando: {os.path.basename(path)} ({self.current_index + 1}/{self.total_files})")
            
            post_opts = {"enabled": self.post_processing_enabled, "upscale_factor": self.upscale_factor, "shadow_enabled": self.shadow_enabled,
                         "background_type": self.background_type, "background_data": self.background_data, "background_resize_mode": self.background_resize_mode,
                         "crop_option": self.crop_option, "fill_holes": self.fill_holes_option}

            self.thread = ProcessThread(input_path=path, model_name=self.model_combo.currentText(), output_format=self.format_combo.currentText().lower(),
                                        potencia=self.slider.value(), tile_size=self.tile_slider.value(), post_processing_opts=post_opts)
            self.thread.progress.connect(self.progress_bar.setValue)
            self.thread.finished.connect(self.finish_image)
            self.thread.error.connect(self.handle_processing_error)
            self.thread.start()
        else:
            self.on_all_files_processed()
    
    def finish_image(self, output_path):
        self.last_output_path = output_path # Store for "Open Image" / "Copy Image"
        self.current_index += 1
        self.process_next_image()

    def on_all_files_processed(self):
        self.label.setText("Arraste e solte as imagens aqui"); self.progress_bar.setVisible(False)
        self.set_controls_enabled(True); self.files_to_process.clear()
        
        msg_box = create_styled_message_box(self, "Processo Concluído", "Todas as imagens foram processadas.")
        
        # Add buttons based on context
        open_folder_button = msg_box.addButton("Abrir Pasta", QMessageBox.ButtonRole.ActionRole)
        
        open_image_button = None
        copy_image_button = None
        
        # If only one file was processed, show "Open Image" and "Copy Image"
        if self.total_files == 1 and hasattr(self, 'last_output_path') and os.path.exists(self.last_output_path):
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

    def copy_image_to_clipboard(self, path):
        try:
            image = QImage(path)
            if not image.isNull():
                QApplication.clipboard().setImage(image)
                # Optional: Show a small tooltip or status?
                # For now, just rely on user checking clipboard.
            else:
                QMessageBox.warning(self, "Erro", "Falha ao carregar imagem para cópia.")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao copiar imagem: {e}")


