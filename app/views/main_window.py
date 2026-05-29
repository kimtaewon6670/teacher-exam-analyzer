from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.controllers.exam_controller import ExamController
from app.controllers.analysis_controller import AnalysisController
from app.controllers.question_controller import QuestionController
from app.controllers.result_controller import ResultController
from app.controllers.student_controller import StudentController
from app.repositories.question_repository import QuestionRepository
from app.services.exam_builder_service import ExamBuilderService
from app.services.pdf_export_service import PdfExportService
from app.views.dashboard_view import DashboardView
from app.views.analysis_view import AnalysisView
from app.views.exam_builder_view import ExamBuilderView
from app.views.question_bank_view import QuestionBankView
from app.views.result_input_view import ResultInputView
from app.views.student_manage_view import StudentManageView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Teacher exam analyzer")
        self.resize(1440, 900)
        self.setMinimumSize(1180, 760)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.pages = QStackedWidget()

        self.student_controller = StudentController()
        self.question_controller = None
        self.exam_controller = None
        self.result_controller = None
        self.analysis_controller = None

        self.pages.addWidget(DashboardView())

        for name in [
            "학생 관리",
            "문제은행 관리",
            "시험지 생성",
            "결과 입력",
            "결과 분석",
        ]:
            self.pages.addWidget(PlaceholderPage(name))

        student_placeholder = self.pages.widget(1)
        self.pages.removeWidget(student_placeholder)
        student_placeholder.deleteLater()
        self.pages.insertWidget(1, StudentManageView(self.student_controller))

        question_placeholder = self.pages.widget(2)
        self.pages.removeWidget(question_placeholder)
        question_placeholder.deleteLater()
        question_view = QuestionBankView()
        self.question_controller = QuestionController(question_view)
        self.pages.insertWidget(2, question_view)

        exam_placeholder = self.pages.widget(3)
        self.pages.removeWidget(exam_placeholder)
        exam_placeholder.deleteLater()
        exam_view = ExamBuilderView()
        self.exam_controller = ExamController(
            exam_view,
            ExamBuilderService(QuestionRepository),
            PdfExportService(),
        )
        self.pages.insertWidget(3, exam_view)

        result_input_placeholder = self.pages.widget(4)
        self.pages.removeWidget(result_input_placeholder)
        result_input_placeholder.deleteLater()
        result_input_view = ResultInputView()
        self.result_controller = ResultController(result_input_view)
        self.pages.insertWidget(4, result_input_view)

        analysis_placeholder = self.pages.widget(5)
        self.pages.removeWidget(analysis_placeholder)
        analysis_placeholder.deleteLater()
        analysis_view = AnalysisView()
        self.analysis_controller = AnalysisController(analysis_view)
        self.pages.insertWidget(5, analysis_view)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages, 1)

        self.sidebar.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.pages.currentChanged.connect(self._on_page_changed)
        self.sidebar.navigation.setCurrentRow(0)

        self.setStyleSheet(
            """
            #root {
                background: #f4f7fb;
                color: #172033;
                font-family: "Malgun Gothic", "Segoe UI", Arial;
            }
            QListWidget {
                border: 0;
                outline: 0;
                background: transparent;
                color: #d9e7f8;
            }
            QListWidget::item {
                min-height: 44px;
                padding: 0 14px;
                margin: 4px 10px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background: #2f85dc;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background: rgba(255, 255, 255, 0.08);
            }
            """
        )

    def _on_page_changed(self, index: int) -> None:
        if index == 4 and self.result_controller is not None:
            self.result_controller.refresh_options()
        if index == 5 and self.analysis_controller is not None:
            self.analysis_controller.refresh_options()


class Sidebar(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self.setStyleSheet(
            """
            #sidebar {
                background: #13263d;
                border: 0;
            }
            #brand {
                color: white;
                font-size: 16px;
                font-weight: 700;
            }
            #brandIcon {
                color: #4aa3ff;
                font-size: 20px;
                font-weight: 700;
            }
            #utility {
                color: #c9d7e8;
                font-size: 13px;
            }
            #divider {
                background: rgba(255, 255, 255, 0.08);
                min-height: 1px;
                max-height: 1px;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 18, 12, 18)
        layout.setSpacing(12)

        brand = QWidget()
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(8)

        icon = QLabel("◆")
        icon.setObjectName("brandIcon")
        title = QLabel("Teacher exam analyzer")
        title.setObjectName("brand")
        title.setWordWrap(True)

        brand_layout.addWidget(icon)
        brand_layout.addWidget(title, 1)
        layout.addWidget(brand)

        self.navigation = QListWidget()
        self.navigation.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        for label in [
            "⌂  대시보드",
            "♙  학생 관리",
            "▤  문제은행 관리",
            "▣  시험지 생성",
            "✎  결과 입력",
            "▥  결과 분석",
        ]:
            self.navigation.addItem(QListWidgetItem(label))

        layout.addWidget(self.navigation, 1)


class PlaceholderPage(QWidget):
    def __init__(self, title: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        label = QLabel(title)
        label.setStyleSheet("font-size: 24px; font-weight: 700; color: #172033;")
        layout.addWidget(label)
        layout.addStretch()
