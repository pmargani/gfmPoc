"main entry point for the GFM application"

import sys

from PySide6.QtWidgets import QApplication

from GfmWindow import GfmWindow

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    else:
        project_name = "GFM"
    window = GfmWindow(project_name, app)
    window.show()
    sys.exit(app.exec())
