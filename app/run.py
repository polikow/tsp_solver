import sys

from PyQt5.QtWidgets import QApplication, QStyleFactory

from app.main_window import App


def run():
    app = QApplication([])
    application = App()
    app.setStyle(QStyleFactory.create('Fusion'))
    application.show()

    sys.exit(app.exec())
