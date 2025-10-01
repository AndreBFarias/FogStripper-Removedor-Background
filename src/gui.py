import os
import logging
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, 
                             QMessageBox, QProgressBar, QSlider, QFrame, QHBoxLayout, 
                             QCheckBox, QComboBox, QGridLayout)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from processor import ProcessThread

logger = logging.getLogger(__name__)

MODEL_DESCRIPTIONS = {
    "u2net": "Modelo de uso geral, bom equilíbrio entre velocidade e precisão para objetos.",
    "u2netp": "Versão 'light' do u2net. Mais rápido, mas com um pouco menos de detalhe.",
    "u2net_human_seg": "Modelo de alta precisão, especializado e otimizado para recortar pessoas.",
    "isnet-general-use": "Modelo moderno e pesado. Lento, mas com a melhor precisão para assuntos complexos."
}

def create_styled_message_box(parent, title, text, icon=QMessageBox.Icon.NoIcon):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setIcon(icon)
    msg_box.setStyleSheet("QLabel{ min-width: 450px; font-size: 13pt; } QPushButton{ font-size: 13pt; padding: 5px; }")
    return msg_box

class DesnudadorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("FogStripper")
        self.setWindowTitle("FogStripper")
        self.setAcceptDrops(True)
        self.setFixedSize(800, 800)
        
        main_layout = QVBoxLayout(self)
        
        self.icon_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'desnudador.png')
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
        self.format_combo.addItems(["PNG", "WEBP"])
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
        
        self.current_index = 0
        self.total_files = 0
        self.output_directory = ""
        self.update_model_description(0)

    def update_model_description(self, index):
        model_name = self.model_combo.currentText()
        self.model_desc_label.setText(MODEL_DESCRIPTIONS.get(model_name, ""))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))]
        if paths: self.process_images(paths)

    def open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecione as Imagens", "", "Imagens (*.png *.jpg *.jpeg *.webp *.gif)")
        if paths: self.process_images(paths)

    def process_images(self, paths):
        if not paths: return
        
        msg_box = create_styled_message_box(self, 'Confirmar Processamento', 
                                            f"Você está prestes a processar {len(paths)} imagem(ns).\n\nDeseja continuar?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec() == QMessageBox.StandardButton.No:
            return

        self.output_directory = os.path.dirname(paths[0])
        self.total_files = len(paths)
        self.current_index = 0
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        logger.info(f"Iniciando processamento de {self.total_files} arquivos.")
        self.process_next_image(paths)

    def process_next_image(self, paths):
        if self.current_index < self.total_files:
            path = paths[self.current_index]
            logger.info(f"Processando arquivo: {path}")
            self.label.setText(f"Processando: {os.path.basename(path)} ({self.current_index + 1}/{self.total_files})")
            
            self.thread = ProcessThread(
                input_path=path,
                apply_upscale=self.upscale_checkbox.isChecked(),
                model_name=self.model_combo.currentText(),
                output_format=self.format_combo.currentText(),
                potencia=self.slider.value(),
                tile_size=self.tile_slider.value()
            )
            self.thread.progress.connect(self.update_progress)
            self.thread.finished.connect(lambda p: self.finish_image(p, paths))
            self.thread.start()
        else:
            logger.info("Processamento em lote concluído.")
            self.label.setText("Arraste e solte as imagens aqui")
            self.progress_bar.setVisible(False)

            msg_box = create_styled_message_box(self, "Processo Concluído", 
                                                "Todas as imagens foram processadas com sucesso!")
            open_folder_button = msg_box.addButton("Abrir Pasta", QMessageBox.ButtonRole.ActionRole)
            process_more_button = msg_box.addButton("Processar Mais", QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
            
            msg_box.exec()

            if msg_box.clickedButton() == open_folder_button:
                QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_directory))
            elif msg_box.clickedButton() == process_more_button:
                self.open_files()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def finish_image(self, output_path, paths):
        if not output_path:
            logger.error("Ocorreu um erro e o caminho de saída não foi gerado.")
            error_box = create_styled_message_box(self, "Erro", 
                                                  "Ocorreu um erro durante o processamento.\nVerifique o arquivo de log para detalhes.",
                                                  icon=QMessageBox.Icon.Critical)
            error_box.exec()
        
        self.current_index += 1
        self.process_next_image(paths)
