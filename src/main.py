#!/usr/bin/env python3
import sys
import logging
import traceback
import shutil
import os
from logger_config import setup_logging, get_log_path

setup_logging()

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog
    #1
    # Feitiço de Identidade: Batiza a aplicação com seu nome verdadeiro.
    QApplication.setApplicationName("FogStripper")
    from gui import DesnudadorWindow
    import qdarkstyle
except ImportError as e:
    logging.critical(f"Falha ao importar dependências críticas da GUI: {e}")
    # Adiciona uma mensagem mais clara para o usuário
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
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = DesnudadorWindow()
    window.show()
    logging.info("Aplicação iniciada com sucesso.")
    sys.exit(app.exec())
