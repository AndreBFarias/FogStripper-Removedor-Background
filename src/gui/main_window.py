import logging
import os
import shutil
from typing import Any

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QDragEnterEvent, QDropEvent, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from src.core.logger_config import get_log_path
from src.core.processor import ProcessThread
from src.gui.constants import ALL_EXTENSIONS, VIDEO_EXTENSIONS
from src.gui.dialogs import ProcessingOptionsDialog, create_styled_message_box
from src.gui.drop_area import DropArea
from src.gui.widgets import PostProcessingPanel, SettingsPanel

logger = logging.getLogger(__name__)


class FogStripperWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._init_state()
        self._setup_ui()
        self._connect_signals()

    def _init_state(self) -> None:
        self.setObjectName("FogStripper")
        self.setWindowTitle("Removedor de Background")
        self.setAcceptDrops(True)
        self.setFixedSize(950, 880)

        self.upscale_factor: int = 0
        self.crop_option: str = "original"
        self.fill_holes_option: bool = False
        self.files_to_process: list[str] = []
        self.current_index: int = 0
        self.total_files: int = 0
        self.output_directory: str = ""
        self.thread: ProcessThread | None = None
        self.last_output_path: str = ""

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        self._setup_header(main_layout)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)

        self.settings_panel = SettingsPanel()
        main_layout.addWidget(self.settings_panel)

        self.post_panel = PostProcessingPanel()
        main_layout.addWidget(self.post_panel)

        self._setup_drop_area(main_layout)
        self._setup_progress_bar(main_layout)

        self.settings_panel.update_model_description(self.settings_panel.model_combo.currentText())

    def _setup_header(self, layout: QVBoxLayout) -> None:
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.setContentsMargins(20, 10, 20, 10)

        self.icon_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                96,
                96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            mirrored = scaled.toImage().mirrored(True, False)
            self.icon_label.setPixmap(QPixmap.fromImage(mirrored))
        header_layout.addWidget(self.icon_label)

        title = QLabel("FogStripper")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

    def _setup_drop_area(self, layout: QVBoxLayout) -> None:
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(30, 0, 30, 0)

        self.drop_area = DropArea(self.start_file_processing)
        container_layout.addWidget(self.drop_area)
        layout.addWidget(container)

    def _setup_progress_bar(self, layout: QVBoxLayout) -> None:
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

    def _connect_signals(self) -> None:
        self.settings_panel.model_combo.currentIndexChanged.connect(self._on_model_changed)
        self.settings_panel.format_combo.currentTextChanged.connect(self._on_format_changed)
        self.settings_panel.rb_upscale_off.toggled.connect(lambda: self._on_upscale_change(0))
        self.settings_panel.rb_upscale_2x.toggled.connect(lambda: self._on_upscale_change(2))
        self.settings_panel.rb_upscale_3x.toggled.connect(lambda: self._on_upscale_change(3))
        self.settings_panel.rb_upscale_4x.toggled.connect(lambda: self._on_upscale_change(4))

    def _on_model_changed(self, index: int) -> None:
        model_name = self.settings_panel.model_combo.currentText()
        self.settings_panel.update_model_description(model_name)
        if model_name == "isnet-general-use" and self.settings_panel.format_combo.currentText() != "SVG":
            self.settings_panel.format_combo.blockSignals(True)
            self.settings_panel.format_combo.setCurrentText("SVG")
            self.settings_panel.format_combo.blockSignals(False)

    def _on_format_changed(self, format_text: str) -> None:
        if format_text.upper() == "SVG" and self.settings_panel.model_combo.currentText() != "isnet-general-use":
            self.settings_panel.model_combo.blockSignals(True)
            self.settings_panel.model_combo.setCurrentText("isnet-general-use")
            self.settings_panel.model_combo.blockSignals(False)
            self.settings_panel.update_model_description("isnet-general-use")

    def _on_upscale_change(self, value: int) -> None:
        if self.sender().isChecked():
            self.upscale_factor = value

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile().lower().endswith(ALL_EXTENSIONS)]
        if paths:
            self.start_file_processing(paths)

    def start_file_processing(self, paths: list[str]) -> None:
        if not paths:
            return

        self.files_to_process = paths
        self.drop_area.update_preview(paths)

        is_animated = any(p.lower().endswith(VIDEO_EXTENSIONS) for p in paths)
        self.settings_panel.upscale_group.setEnabled(not is_animated)
        self.post_panel.frame.setEnabled(not is_animated)

        if is_animated:
            msg = create_styled_message_box(self, "Confirmar Processamento", f"Processar {len(paths)} imagem(ns)?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if msg.exec() == QMessageBox.StandardButton.No:
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
        self._set_controls_enabled(False)
        self._process_next()

    def _process_next(self) -> None:
        if self.current_index >= self.total_files:
            self._on_all_processed()
            return

        path = self.files_to_process[self.current_index]
        self.status_label.setText(
            f"Processando: {os.path.basename(path)} ({self.current_index + 1}/{self.total_files})"
        )
        self.status_label.setVisible(True)

        post_opts: dict[str, Any] = {
            "enabled": self.post_panel.is_enabled(),
            "upscale_factor": self.upscale_factor,
            "crop_option": self.crop_option,
            "fill_holes": self.fill_holes_option,
            **self.post_panel.get_options(),
        }

        self.thread = ProcessThread(
            input_path=path,
            model_name=self.settings_panel.model_combo.currentText(),
            output_format=self.settings_panel.format_combo.currentText().lower(),
            potencia=self.settings_panel.slider.value(),
            tile_size=self.settings_panel.tile_slider.value(),
            post_processing_opts=post_opts,
        )
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self._on_image_finished)
        self.thread.error.connect(self._on_error)
        self.thread.start()

    def _on_image_finished(self, output_path: str) -> None:
        self.last_output_path = output_path
        self.current_index += 1
        self._process_next()

    def _on_all_processed(self) -> None:
        self.status_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self._set_controls_enabled(True)
        self.files_to_process.clear()
        self.drop_area.clear()

        msg = create_styled_message_box(self, "Processo Concluído", "Todas as imagens foram processadas.")
        open_folder = msg.addButton("Abrir Pasta", QMessageBox.ButtonRole.ActionRole)

        open_image = None
        copy_image = None
        if self.total_files == 1 and self.last_output_path and os.path.exists(self.last_output_path):
            open_image = msg.addButton("Abrir Imagem", QMessageBox.ButtonRole.ActionRole)
            copy_image = msg.addButton("Copiar Imagem", QMessageBox.ButtonRole.ActionRole)

        msg.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == open_folder:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_directory))
        elif open_image and clicked == open_image:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_output_path))
        elif copy_image and clicked == copy_image:
            self._copy_to_clipboard(self.last_output_path)

    def _on_error(self, error_message: str) -> None:
        self.status_label.setText("Ocorreu um erro!")
        self.status_label.setVisible(True)
        self.progress_bar.setVisible(False)
        self._set_controls_enabled(True)
        self.files_to_process.clear()
        self.drop_area.clear()

        dialog = create_styled_message_box(
            self,
            "Erro no Processamento",
            "Ocorreu um erro.",
            QMessageBox.Icon.Critical,
            f"Detalhes: {error_message}",
        )
        save_btn = dialog.addButton("Salvar Relatório", QMessageBox.ButtonRole.ActionRole)
        dialog.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        dialog.exec()

        if dialog.clickedButton() == save_btn:
            self._save_log()

    def _save_log(self) -> None:
        log_path = get_log_path()
        if not os.path.exists(log_path):
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            os.path.expanduser("~/fogstripper_error_report.log"),
            "Log Files (*.log)",
        )
        if save_path:
            try:
                shutil.copy(log_path, save_path)
            except Exception as e:
                logger.error(f"Falha ao salvar o relatório: {e}")

    def _set_controls_enabled(self, enabled: bool) -> None:
        self.drop_area.setEnabled(enabled)
        self.settings_panel.setEnabled(enabled)
        self.post_panel.setEnabled(enabled)
        self.setAcceptDrops(enabled)

        is_animated = any(p.lower().endswith(VIDEO_EXTENSIONS) for p in self.files_to_process)
        if is_animated and enabled:
            self.settings_panel.upscale_group.setEnabled(False)
            self.post_panel.frame.setEnabled(False)

    def _copy_to_clipboard(self, path: str) -> None:
        try:
            image = QImage(path)
            if not image.isNull():
                QApplication.clipboard().setImage(image)
            else:
                QMessageBox.warning(self, "Erro", "Falha ao carregar imagem para cópia.")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao copiar imagem: {e}")
