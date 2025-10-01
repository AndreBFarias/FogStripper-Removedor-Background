#!/usr/bin/env python3
import sys
import logging
from logger_config import setup_logging

setup_logging()

try:
    from PyQt6.QtWidgets import QApplication
    from gui import DesnudadorWindow
    import qdarkstyle
except ImportError as e:
    logging.critical(f"Falha ao importar dependências críticas da GUI: {e}")
    sys.exit(1)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        # Aplica um estilo global com a fonte de 13pt
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6') + "QWidget { font-size: 13pt; }")
        window = DesnudadorWindow()
        window.show()
        logging.info("Aplicação iniciada com sucesso.")
        sys.exit(app.exec())
    except Exception as e:
        logging.critical(f"Erro fatal na execução da aplicação: {e}", exc_info=True)
        sys.exit(1)
