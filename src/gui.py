import os
import logging
import shutil
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, 
                             QMessageBox, QProgressBar, QSlider, QFrame, 
                             QGridLayout, QComboBox, QCheckBox)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from processor import ProcessThread
from logger_config import get_log_path

logger = logging.getLogger(__name__)

MODEL_DESCRIPTIONS = {
    "u2net": "Modelo de uso geral, bom equilíbrio entre velocidade e precisão.",
    "u2netp": "Versão 'light' do u2net. Mais rápido, menos detalhe.",
    "u2net_human_seg": "Alta precisão, especializado para recortar pessoas.",
    "isnet-general-use": "Moderno e pesado. Lento, mas com a melhor precisão."
}

#2
def create_styled_message_box(parent, title, text, icon=QMessageBox.Icon.NoIcon, informative_text=""):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    if informative_text:
        msg_box.setInformativeText(informative_text)
    msg_box.setIcon(icon)
    msg_box.setStyleSheet("QLabel{ min-width: 450px; font-size: 13pt; } QPushButton{ font-size: 13pt; padding: 5px; }")
    # Devolve a instância para que botões possam ser adicionados externamente
    return msg_box

class DesnudadorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("FogStripper")
        self.setWindowTitle("FogStripper")
        # ... (O resto do seu __init__ permanece o mesmo)
        self.setAcceptDrops(True)
        self.setFixedSize(800, 800)
        
        main_layout = QVBoxLayout(self)
        
        self.icon_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')
        pixmap = QPixmap(logo_path)
        self.icon_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.icon_label)
        
        self.label = QLabel("Arraste e solte as imagens aqui")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label)
        
        settings_frame = QFrame()
        main_layout.addWidget(settings_frame)
        
        settings_layout = QGridLayout(settings_frame)
        settings_layout.setContentsMargins(50, 10, 50, 10)

        self.model_label = QLabel("Arsenal Neural:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(MODEL_DESCRIPTIONS.keys())
        self.model_combo.currentIndexChanged.connect(self.update_model_description)
        settings_layout.addWidget(self.model_label, 0, 0)
        settings_layout.addWidget(self.model_combo, 0, 1)

        self.model_desc_label = QLabel()
        self.model_desc_label.setWordWrap(True)
        self.model_desc_label.setStyleSheet("font-size: 10pt; color: #aaa;")
        settings_layout.addWidget(self.model_desc_label, 1, 0, 1, 2)

        self.format_label = QLabel("Formato de Saída:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "SVG", "GIF", "WEBM"])
        settings_layout.addWidget(self.format_label, 2, 0)
        settings_layout.addWidget(self.format_combo, 2, 1)

        self.slider_label = QLabel("Potência (Borda):")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(75)
        settings_layout.addWidget(self.slider_label, 3, 0)
        settings_layout.addWidget(self.slider, 3, 1)

        self.tile_label = QLabel("Bloco (VRAM):")
        self.tile_slider = QSlider(Qt.Orientation.Horizontal)
        self.tile_slider.setMinimum(256)
        self.tile_slider.setMaximum(1024)
        self.tile_slider.setValue(512)
        self.tile_slider.setSingleStep(64)
        self.tile_slider.setToolTip("Blocos menores usam menos VRAM, evitando erros em imagens grandes.")
        settings_layout.addWidget(self.tile_label, 4, 0)
        settings_layout.addWidget(self.tile_slider, 4, 1)
        
        self.upscale_checkbox = QCheckBox("Aplicar Upscale 4x (Melhora a qualidade)")
        self.upscale_checkbox.setChecked(True)
        settings_layout.addWidget(self.upscale_checkbox, 5, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch()
        
        self.button = QPushButton("Selecione as Imagens")
        self.button.clicked.connect(self.open_files)
        main_layout.addWidget(self.button)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.files_to_process = []
        self.current_index = 0
        self.total_files = 0
        self.output_directory = ""
        self.thread = None
        self.update_model_description(0)

    # ... (O resto dos seus métodos permanece o mesmo até o handle_processing_error)

    def handle_processing_error(self, error_message):
        """ Conjura uma janela de diálogo para revelar a alma do erro, com a opção de salvar o relatório. """
        logger.error(f"Um erro foi capturado pela GUI: {error_message}")
        self.label.setText("Ocorreu um erro!")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.set_controls_enabled(True)
        self.files_to_process.clear()

        log_path = get_log_path()
        error_dialog = create_styled_message_box(
            self,
            "Erro no Processamento",
            "Ocorreu um erro durante a purificação do espírito.",
            QMessageBox.Icon.Critical,
            f"Detalhes: {error_message}\n\nUm registro completo da provação foi salvo em:\n{log_path}"
        )
        #3
        # Conjura os botões personalizados
        save_button = error_dialog.addButton("Salvar Relatório", QMessageBox.ButtonRole.ActionRole)
        error_dialog.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        
        error_dialog.exec()

        if error_dialog.clickedButton() == save_button:
            self.save_log_file()

    def save_log_file(self):
        log_path = get_log_path()
        if not os.path.exists(log_path):
            logger.error("Arquivo de log não encontrado para salvamento.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório de Erro", os.path.expanduser("~/fogstripper_error_report.log"), "Log Files (*.log)")
        if save_path:
            try:
                shutil.copy(log_path, save_path)
                logger.info(f"Relatório de erro salvo em: {save_path}")
            except Exception as e:
                logger.error(f"Falha ao salvar o relatório de erro: {e}")
    
    # Adicionando os outros métodos para completude, sem alterações
    def set_controls_enabled(self, enabled):
        self.button.setEnabled(enabled)
        self.model_combo.setEnabled(enabled)
        self.format_combo.setEnabled(enabled)
        self.slider.setEnabled(enabled)
        self.tile_slider.setEnabled(enabled)
        self.setAcceptDrops(enabled)
        is_animated = any(p.lower().endswith(('.gif', '.webm')) for p in self.files_to_process)
        if not is_animated:
            self.upscale_checkbox.setEnabled(enabled)

    def update_model_description(self, index):
        model_name = self.model_combo.currentText()
        self.model_desc_label.setText(MODEL_DESCRIPTIONS.get(model_name, ""))

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
        
        is_animated = any(p.lower().endswith(('.gif', '.webm')) for p in paths)
        if is_animated:
            self.upscale_checkbox.setChecked(False)
            self.upscale_checkbox.setEnabled(False)
            self.upscale_checkbox.setToolTip("Upscale não está disponível para GIFs/WEBMs.")
        else:
            self.upscale_checkbox.setEnabled(True)
            self.upscale_checkbox.setToolTip("")
        
        msg_box = create_styled_message_box(self, 'Confirmar Processamento', f"Você está prestes a processar {len(paths)} imagem(ns).\n\nDeseja continuar?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec() == QMessageBox.StandardButton.No: return

        self.files_to_process = paths
        self.output_directory = os.path.dirname(paths[0])
        self.total_files = len(paths)
        self.current_index = 0
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.set_controls_enabled(False)
        logger.info(f"Iniciando processamento de {self.total_files} arquivos.")
        self.process_next_image()

    def process_next_image(self):
        if self.current_index < self.total_files:
            path = self.files_to_process[self.current_index]
            logger.info(f"Processando arquivo: {path}")
            self.label.setText(f"Processando: {os.path.basename(path)} ({self.current_index + 1}/{self.total_files})")
            
            self.thread = ProcessThread(
                input_path=path,
                apply_upscale=self.upscale_checkbox.isChecked(),
                model_name=self.model_combo.currentText(),
                output_format=self.format_combo.currentText().lower(),
                potencia=self.slider.value(),
                tile_size=self.tile_slider.value()
            )
            self.thread.progress.connect(self.progress_bar.setValue)
            self.thread.finished.connect(self.finish_image)
            self.thread.error.connect(self.handle_processing_error)
            self.thread.start()
        else:
            logger.info("Processamento em lote concluído.")
            self.label.setText("Arraste e solte as imagens aqui")
            self.progress_bar.setVisible(False)
            self.set_controls_enabled(True)

            msg_box = create_styled_message_box(self, "Processo Concluído", "Todas as imagens foram processadas com sucesso!")
            open_folder_button = msg_box.addButton("Abrir Pasta", QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
            
            msg_box.exec()

            if msg_box.clickedButton() == open_folder_button:
                QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_directory))

    def finish_image(self, output_path):
        self.current_index += 1
        self.process_next_image()
