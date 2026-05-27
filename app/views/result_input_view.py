from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ResultInputView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("resultInputView")
        self._manual_answers: dict[int, str] = {}
        self.answer_input_window: AnswerInputDialog | None = None
        self._exam_ids: list[object] = []
        self._class_ids: list[object] = []
        self._student_ids: list[object] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(16)

        title = QLabel("시험 결과 입력")
        title.setObjectName("pageTitle")
        description = QLabel("시험을 선택한 뒤 학생별 답안을 입력하거나 CSV 파일을 불러와 자동 채점을 실행할 수 있습니다.")
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self._build_exam_select_card())
        layout.addWidget(self._build_answer_input_card(), 1)
        layout.addWidget(self._build_csv_card(), 1)
        layout.addWidget(self._build_validation_card())
        layout.addWidget(self._build_action_bar())

        self.setStyleSheet(
            """
            #resultInputView {
                background: #f4f7fb;
                color: #172033;
                font-family: "Malgun Gothic", "Segoe UI", Arial;
            }
            #pageTitle {
                color: #18263a;
                font-size: 26px;
                font-weight: 800;
            }
            #pageDescription {
                color: #53657a;
                font-size: 13px;
            }
            #card {
                background: white;
                border: 1px solid #dfe6ef;
                border-radius: 8px;
            }
            #cardTitle {
                color: #172033;
                font-size: 16px;
                font-weight: 800;
            }
            #fieldLabel {
                color: #53657a;
                font-size: 12px;
                font-weight: 700;
            }
            #examSummary, #csvGuide, #validationMessage {
                color: #40536b;
                font-size: 13px;
            }
            QComboBox {
                background: white;
                border: 1px solid #d8e0ea;
                border-radius: 6px;
                color: #28384c;
                min-height: 30px;
                padding: 8px 10px;
            }
            QPushButton {
                background: white;
                border: 1px solid #d8e0ea;
                border-radius: 6px;
                color: #27384c;
                font-weight: 700;
                min-height: 30px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: #eef5ff;
            }
            QPushButton#primaryButton {
                background: #2f85dc;
                border-color: #2f85dc;
                color: white;
            }
            QPushButton#primaryButton:hover {
                background: #2475c6;
            }
            QTableWidget {
                background: white;
                border: 1px solid #dfe6ef;
                border-radius: 6px;
                color: #233348;
                gridline-color: #e6ecf3;
                selection-background-color: #e8f2ff;
            }
            QHeaderView::section {
                background: #f7f9fc;
                border: 0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
                color: #2a3a50;
                font-weight: 800;
                padding: 9px;
            }
            """
        )

    def set_exam_options(self, exams: list[dict[str, object]]) -> None:
        self._exam_ids = []
        self.exam_combo.clear()
        for exam in exams:
            self._exam_ids.append(exam.get("id"))
            self.exam_combo.addItem(str(exam.get("name", "")))

    def set_class_options(self, classes: list[dict[str, object]]) -> None:
        self._class_ids = []
        self.class_combo.clear()
        for class_item in classes:
            self._class_ids.append(class_item.get("id"))
            self.class_combo.addItem(str(class_item.get("name", "")))

    def set_student_options(self, students: list[dict[str, object]]) -> None:
        self._student_ids = []
        self.student_combo.clear()
        for student in students:
            self._student_ids.append(student.get("id"))
            self.student_combo.addItem(f"{student.get('name', '')} / {student.get('student_id', '')}")

    def set_exam_summary(self, summary: dict[str, object]) -> None:
        self.exam_summary_label.setText(
            f"문항 수: {summary.get('question_count', '-')}    "
            f"과목/영역: {summary.get('subject', '-')}    "
            f"시험일: {summary.get('exam_date', '-')}"
        )

    def set_answer_items(self, question_count: int) -> None:
        self._manual_answers = {question_number: "" for question_number in range(1, question_count + 1)}
        if self.answer_input_window is not None:
            self.answer_input_window.set_answers(self.get_manual_answers())

    def get_selected_exam_id(self) -> object | None:
        return self._get_selected_id(self._exam_ids, self.exam_combo.currentIndex())

    def get_selected_class_id(self) -> object | None:
        return self._get_selected_id(self._class_ids, self.class_combo.currentIndex())

    def get_selected_student_id(self) -> object | None:
        return self._get_selected_id(self._student_ids, self.student_combo.currentIndex())

    def get_manual_answers(self) -> dict[int, str]:
        return dict(self._manual_answers)

    def set_manual_answers(self, answers: dict[int, str]) -> None:
        for question_number, answer in answers.items():
            if question_number in self._manual_answers:
                self._manual_answers[question_number] = str(answer).strip()

    def set_csv_file_name(self, file_name: str) -> None:
        self.csv_file_name_label.setText(file_name or "선택된 CSV 파일이 없습니다.")

    def get_csv_file_path(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "CSV 파일 선택",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )
        return file_path

    def set_csv_preview_data(self, rows: list[dict[str, object]]) -> None:
        if not rows:
            self.csv_preview_table.setRowCount(0)
            self.csv_preview_table.setColumnCount(0)
            return

        headers = list(rows[0].keys())
        self.csv_preview_table.setColumnCount(len(headers))
        self.csv_preview_table.setHorizontalHeaderLabels(headers)
        self.csv_preview_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, header in enumerate(headers):
                item = QTableWidgetItem(str(row.get(header, "")))
                item.setTextAlignment(Qt.AlignCenter)
                self.csv_preview_table.setItem(row_index, column_index, item)
            self.csv_preview_table.setRowHeight(row_index, 34)

    def show_validation_message(self, message: str, is_success: bool = False) -> None:
        self.validation_message_label.setText(message)
        color = "#16803c" if is_success else "#b54708"
        self.validation_message_label.setStyleSheet(f"color: {color}; font-weight: 700;")

    def clear_form(self) -> None:
        self.exam_combo.setCurrentIndex(0 if self.exam_combo.count() else -1)
        self.class_combo.setCurrentIndex(0 if self.class_combo.count() else -1)
        self.student_combo.setCurrentIndex(0 if self.student_combo.count() else -1)
        for question_number in self._manual_answers:
            self._manual_answers[question_number] = ""
        self.set_csv_file_name("")
        self.set_csv_preview_data([])
        self.show_validation_message("입력값 검증 결과가 여기에 표시됩니다.")

    def _build_exam_select_card(self) -> QFrame:
        card = self._make_card("시험 선택")
        layout = card.layout()
        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.exam_combo = QComboBox()
        self.class_combo = QComboBox()
        self.student_combo = QComboBox()
        self.exam_summary_label = QLabel("문항 수: -    과목/영역: -    시험일: -")
        self.exam_summary_label.setObjectName("examSummary")

        form.addWidget(self._make_labeled_widget("시험 선택", self.exam_combo), 0, 0)
        form.addWidget(self._make_labeled_widget("반 선택", self.class_combo), 0, 1)
        form.addWidget(self._make_labeled_widget("학생 선택", self.student_combo), 0, 2)
        form.addWidget(self._make_labeled_widget("선택한 시험 정보", self.exam_summary_label), 1, 0, 1, 3)
        layout.addLayout(form)
        return card

    def _build_answer_input_card(self) -> QFrame:
        card = self._make_card("답안 입력")
        layout = card.layout()

        header = QHBoxLayout()
        description = QLabel("학생의 단답형 답안은 큰 입력 창에서 한 번에 입력합니다.")
        description.setObjectName("csvGuide")
        header.addWidget(description)
        header.addStretch()
        open_answer_button = QPushButton("답안 입력")
        open_answer_button.setObjectName("primaryButton")
        open_answer_button.setFixedWidth(120)
        open_answer_button.clicked.connect(self._open_answer_input_window)
        header.addWidget(open_answer_button)
        layout.addLayout(header)
        return card

    def _build_csv_card(self) -> QFrame:
        card = self._make_card("CSV 파일 불러오기")
        layout = card.layout()

        top_row = QHBoxLayout()
        self.load_csv_button = QPushButton("CSV 파일 불러오기")
        self.load_csv_button.setObjectName("primaryButton")
        self.csv_file_name_label = QLabel("선택된 CSV 파일이 없습니다.")
        self.csv_file_name_label.setObjectName("csvGuide")
        top_row.addWidget(self.load_csv_button)
        top_row.addWidget(self.csv_file_name_label, 1)
        layout.addLayout(top_row)

        guide = QLabel("첫 번째 열에는 학번을 넣고, 그 다음 열부터 1번 문항 답안, 2번 문항 답안 순서로 작성해 주세요.")
        guide.setObjectName("csvGuide")
        layout.addWidget(guide)

        self.csv_preview_table = QTableWidget(0, 0)
        self.csv_preview_table.verticalHeader().setVisible(False)
        self.csv_preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.csv_preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.csv_preview_table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.csv_preview_table)
        return card

    def _build_validation_card(self) -> QFrame:
        card = self._make_card("입력값 검증")
        layout = card.layout()
        self.validation_message_label = QLabel("입력값 검증 결과가 여기에 표시됩니다.")
        self.validation_message_label.setObjectName("validationMessage")
        layout.addWidget(self.validation_message_label)
        return card

    def _build_action_bar(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        self.validate_button = QPushButton("입력값 검증")
        self.save_button = QPushButton("답안 저장")
        self.grade_button = QPushButton("자동 채점 실행")
        self.reset_button = QPushButton("초기화")
        self.grade_button.setObjectName("primaryButton")

        layout.addStretch()
        layout.addWidget(self.validate_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.grade_button)
        layout.addWidget(self.reset_button)
        return card

    def _make_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)
        label = QLabel(title)
        label.setObjectName("cardTitle")
        layout.addWidget(label)
        return card

    def _make_labeled_widget(self, label_text: str, field: QWidget) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addWidget(field)
        return wrapper

    def _open_answer_input_window(self) -> None:
        self.answer_input_window = AnswerInputDialog(self.get_manual_answers(), self)
        if self.answer_input_window.exec() == QDialog.Accepted:
            self.set_manual_answers(self.answer_input_window.get_answers())

    def _get_selected_id(self, ids: list[object], index: int) -> object | None:
        if 0 <= index < len(ids):
            return ids[index]
        return None


class AnswerInputDialog(QDialog):
    def __init__(self, answers: dict[int, str], parent: ResultInputView | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("답안 입력")
        self.resize(900, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 24)
        layout.setSpacing(14)

        title = QLabel("답안 입력")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        self.answer_widgets: dict[int, QLineEdit] = {}
        self.answer_table = QTableWidget(0, 3)
        self.answer_table.setHorizontalHeaderLabels(["문항 번호", "입력 답안", "입력 상태"])
        self.answer_table.verticalHeader().setVisible(False)
        self.answer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.answer_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.answer_table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.answer_table, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("적용")
        buttons.button(QDialogButtonBox.Cancel).setText("취소")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.set_answers(answers)
        self.setStyleSheet(
            """
            QDialog {
                background: #f4f7fb;
                color: #172033;
                font-family: "Malgun Gothic", "Segoe UI", Arial;
            }
            #dialogTitle {
                color: #18263a;
                font-size: 24px;
                font-weight: 800;
            }
            QLineEdit {
                background: white;
                border: 1px solid #d8e0ea;
                border-radius: 6px;
                color: #28384c;
                min-height: 30px;
                padding: 8px 10px;
            }
            QTableWidget {
                background: white;
                border: 1px solid #dfe6ef;
                border-radius: 6px;
                color: #233348;
                gridline-color: #e6ecf3;
            }
            QHeaderView::section {
                background: #f7f9fc;
                border: 0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
                color: #2a3a50;
                font-weight: 800;
                padding: 9px;
            }
            """
        )

    def set_answers(self, answers: dict[int, str]) -> None:
        self.answer_widgets = {}
        question_numbers = sorted(answers.keys())
        self.answer_table.setRowCount(len(question_numbers))
        for row_index, question_number in enumerate(question_numbers):
            answer_input = QLineEdit()
            answer_input.setPlaceholderText("단답형 답안 입력")
            answer_input.setText(str(answers.get(question_number, "")))
            answer_input.textChanged.connect(
                lambda text, row=row_index: self._update_answer_status(row, text)
            )

            number_item = QTableWidgetItem(str(question_number))
            number_item.setTextAlignment(Qt.AlignCenter)
            status_item = QTableWidgetItem("입력 완료" if answer_input.text().strip() else "미입력")
            status_item.setTextAlignment(Qt.AlignCenter)

            self.answer_widgets[question_number] = answer_input
            self.answer_table.setItem(row_index, 0, number_item)
            self.answer_table.setCellWidget(row_index, 1, answer_input)
            self.answer_table.setItem(row_index, 2, status_item)
            self.answer_table.setRowHeight(row_index, 40)

    def get_answers(self) -> dict[int, str]:
        return {
            question_number: answer_widget.text().strip()
            for question_number, answer_widget in self.answer_widgets.items()
        }

    def _update_answer_status(self, row: int, answer: str) -> None:
        item = self.answer_table.item(row, 2)
        if item is not None:
            item.setText("입력 완료" if answer else "미입력")
