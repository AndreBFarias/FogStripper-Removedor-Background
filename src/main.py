import sys
import logging
import traceback
import shutil
import os
from src.core.logger_config import setup_logging, get_log_path

setup_logging()

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog

    QApplication.setApplicationName("FogStripper")
    from src.gui.main_window import FogStripperWindow
    import qdarkstyle
except ImportError as e:
    logging.critical(f"Falha ao importar dependências críticas da GUI: {e}")

    print("\n--> ERRO: Dependências da interface não encontradas.")
    print("--> Se este for o primeiro uso do dev_run.py, isso é esperado.")
    print("--> O script tentará instalá-las agora. Por favor, aguarde.")
    sys.exit(1)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Captura exceções não tratadas para evitar que a aplicação feche silenciosamente."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Erro não capturado!", exc_info=(exc_type, exc_value, exc_traceback))

    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setText("Ocorreu um erro fatal e inesperado.\nA aplicação precisa ser fechada.")
    msg_box.setInformativeText("Você pode salvar um relatório do erro para análise.")
    msg_box.setWindowTitle("Erro Crítico")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Close)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Close)

    if msg_box.exec() == QMessageBox.StandardButton.Save:
        log_path = get_log_path()
        if os.path.exists(log_path):
            save_path, _ = QFileDialog.getSaveFileName(None, "Salvar Relatório de Erro", os.path.expanduser("~/fogstripper_crash_report.log"), "Log Files (*.log)")
            if save_path:
                try:
                    shutil.copy(log_path, save_path)
                except Exception as e:
                    logging.error(f"Não foi possível salvar o log: {e}")

    QApplication.instance().quit()

sys.excepthook = handle_exception

if __name__ == "__main__":
    app = QApplication(sys.argv)
    base_style = qdarkstyle.load_stylesheet()
    combo_fix = """
        QComboBox QAbstractItemView::item {
            padding-left: 0px;
        }
        QComboBox QAbstractItemView::indicator {
            width: 0px;
            height: 0px;
            margin: 0px;
            padding: 0px;
            border: none;
            background: transparent;
        }
        QComboBox QAbstractItemView::indicator:checked,
        QComboBox QAbstractItemView::indicator:unchecked {
            width: 0px;
            height: 0px;
            image: none;
            border: none;
            background: transparent;
        }
    """
    app.setStyleSheet(base_style + combo_fix)
    window = FogStripperWindow()
    window.show()
    logging.info("Aplicação iniciada com sucesso.")
    sys.exit(app.exec())
