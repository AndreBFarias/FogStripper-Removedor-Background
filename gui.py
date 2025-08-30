#1
import os
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox, QProgressBar, QSlider, QFrame, QHBoxLayout
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from processor import ProcessThread

#2
class DesnudadorWindow(QWidget):
    def __init__(self):
        super().__init__()
#3
        self.setWindowTitle("FogStripper")
        self.showMaximized()
        self.setAcceptDrops(True)
        
        # Central frame for the GUI elements
        self.central_frame = QFrame(self)
        self.central_frame.setFixedSize(800, 600)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addStretch()
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch()
        horizontal_layout.addWidget(self.central_frame)
        horizontal_layout.addStretch()
        self.main_layout.addLayout(horizontal_layout)
        self.main_layout.addStretch()
        
        # Layout for the central frame
        self.layout = QVBoxLayout(self.central_frame)
        
        # Icon label with relative path
        self.icon_label = QLabel()
#4
        logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'desnudador.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
        else:
            pixmap = QPixmap()  # Fallback to empty image
        self.icon_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.icon_label)
        
        # Instruction label
        self.label = QLabel("Arraste e solte as imagens aqui")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
        
        # GPU power label
        self.slider_label = QLabel("Potência da GPU")
        self.slider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.slider_label)
        
        # Slider for GPU power
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(75)
        self.layout.addWidget(self.slider)
        
        # Scale label
        self.scale_label = QLabel("Escala: 4x (Potência: 75%)")
        self.scale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.scale_label)
        self.slider.valueChanged.connect(self.update_scale)
        
        # Button to select images
        self.button = QPushButton("Selecione Imagens")
        self.button.clicked.connect(self.open_files)
        self.layout.addWidget(self.button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)
        
        self.current_index = 0
        self.total_files = 0

    def update_scale(self, value):
        scale = 1 + int((value / 100) * 4)
        self.scale_label.setText(f"Escala: {scale}x (Potência: {value}%)")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        input_paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg', '.ico', '.bmp', '.tiff', '.gif'))]
        if input_paths:
            self.process_images(input_paths)

    def open_files(self):
        input_paths, _ = QFileDialog.getOpenFileNames(self, "Selecione Imagens para Despir", "", "Images (*.png *.jpg *.jpeg *.webp *.svg *.ico *.bmp *.tiff *.gif)")
        if input_paths:
            self.process_images(input_paths)

    def process_images(self, input_paths):
        self.total_files = len(input_paths)
        self.current_index = 0
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_next_image(input_paths)

    def process_next_image(self, input_paths):
        if self.current_index < self.total_files:
            input_path = input_paths[self.current_index]
            self.label.setText(f"Processando imagem {self.current_index + 1} de {self.total_files} - 0% concluído")
            self.thread = ProcessThread(input_path, self.slider.value())
            self.thread.progress.connect(self.update_progress)
            self.thread.finished.connect(lambda output_path: self.finish_image(output_path, input_paths))
            self.thread.start()
        else:
            self.label.setText("Arraste e solte as imagens aqui")
            self.progress_bar.setVisible(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.label.setText(f"Processando imagem {self.current_index + 1} de {self.total_files} - {value}% concluído")

    def finish_image(self, output_path, input_paths):
        if output_path:
            msg = QMessageBox(self)
#5
            msg.setWindowTitle("Processo Concluído")
            msg.setText(f"Imagem processada salva em: {output_path}")
            view_button = QPushButton("Abrir Pasta")
            view_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(output_path))))
            msg.addButton(view_button, QMessageBox.ButtonRole.ActionRole)
            msg.exec()
        self.current_index += 1
        self.process_next_image(input_paths)
