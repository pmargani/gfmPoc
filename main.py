"main entry point for the GFM application"

import sys
import logging
import argparse

from PySide6.QtWidgets import QApplication

from GfmWindow import GfmWindow
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GFM Application")
    parser.add_argument("project", help="Name of the project")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = GfmWindow(args.project, app)
    window.show()
    sys.exit(app.exec())
