import sys

from PySide6.QtWidgets import QApplication

from app.repositories.db import init_database
from app.views.main_window import MainWindow


def main() -> int:
    init_database()

    app = QApplication(sys.argv)
    app.setApplicationName("Teacher exam analyzer")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
