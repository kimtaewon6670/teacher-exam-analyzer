from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class QuestionBankView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.on_edit_question = None
        self.on_status_change_question = None
        self.setObjectName("questionBankView")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(16)

        title = QLabel("문제은행 관리")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        layout.addWidget(self._build_register_card())
        layout.addWidget(self._build_filter_card())
        layout.addWidget(self._build_table_card(), 1)
        self.questions_data: list[dict[str, str]] = []
        self.question_list_window: QuestionListDialog | None = None

        self.setStyleSheet(
            """
            #questionBankView {
                background: #f4f7fb;
                color: #172033;
                font-family: "Malgun Gothic", "Segoe UI", Arial;
            }
            #pageTitle {
                color: #18263a;
                font-size: 26px;
                font-weight: 800;
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
            QLineEdit, QComboBox, QTextEdit {
                background: white;
                border: 1px solid #d8e0ea;
                border-radius: 6px;
                color: #28384c;
                padding: 8px 10px;
            }
            QLineEdit, QComboBox {
                min-height: 30px;
            }
            QTextEdit {
                min-height: 58px;
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
            QPushButton#editButton {
                color: #1f6fc2;
                max-height: 24px;
                min-height: 24px;
                padding: 0;
            }
            QPushButton#disableButton {
                color: #b54708;
                max-height: 24px;
                min-height: 24px;
                padding: 0;
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

    def set_questions_data(self, questions: list[dict[str, str]]) -> None:
        self.questions_data = questions
        if self.question_list_window is not None and self.question_list_window.isVisible():
            self.question_list_window.set_questions_data(questions)

    def _fill_questions_table(self, table: QTableWidget, questions: list[dict[str, str]]) -> None:
        table.setRowCount(len(questions))
        for row_index, question in enumerate(questions):
            values = [
                question.get("exam", ""),
                question.get("class_name", ""),
                question.get("content", ""),
                question.get("type", ""),
                question.get("sub_category", ""),
                question.get("difficulty", ""),
                question.get("answer", ""),
                question.get("tags", ""),
                question.get("status", ""),
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                alignment = Qt.AlignLeft | Qt.AlignVCenter if column_index == 2 else Qt.AlignCenter
                item.setTextAlignment(alignment)
                table.setItem(row_index, column_index, item)

            question_id = question.get("id")
            is_active = question.get("status") == "활성"
            table.setCellWidget(
                row_index,
                9,
                self._make_table_button_cell(
                    "수정",
                    "editButton",
                    lambda checked=False, question_id=question_id: self._handle_edit_clicked(question_id),
                ),
            )
            table.setCellWidget(
                row_index,
                10,
                self._make_table_button_cell(
                    "비활성화" if is_active else "활성화",
                    "disableButton",
                    lambda checked=False, question_id=question_id, is_active=is_active: self._handle_status_change_clicked(
                        question_id,
                        is_active,
                    ),
                ),
            )
            table.setRowHeight(row_index, 40)

    def _handle_edit_clicked(self, question_id: int | None) -> None:
        if question_id is not None and self.on_edit_question is not None:
            self.on_edit_question(int(question_id))

    def _handle_status_change_clicked(self, question_id: int | None, is_active: bool) -> None:
        if question_id is not None and self.on_status_change_question is not None:
            self.on_status_change_question(int(question_id), is_active)

    def get_question_form_data(self) -> dict[str, str]:
        return {
            "exam_year": self.exam_year_input.text().strip(),
            "semester": self.semester_combo.currentText(),
            "exam_type": self.exam_type_combo.currentText(),
            "exam_name": self._get_selected_exam_name(),
            "class_name": self.class_combo.currentText(),
            "content": self.content_input.toPlainText().strip(),
            "type": self.type_combo.currentText(),
            "sub_category": self.sub_category_input.text().strip(),
            "difficulty": self.difficulty_combo.currentText(),
            "answer": self.answer_input.text().strip(),
            "allowed_answers": self.allowed_answers_input.text().strip(),
            "explanation": self.explanation_input.toPlainText().strip(),
            "tags": self.tags_input.text().strip(),
        }

    def set_question_form_data(self, question: dict[str, str]) -> None:
        exam_name = question.get("exam", "")
        exam_parts = exam_name.split()
        if len(exam_parts) >= 3:
            self.exam_year_input.setText(exam_parts[0].replace("년", ""))
            self._set_combo_value(self.semester_combo, exam_parts[1])
            self._set_combo_value(self.exam_type_combo, exam_parts[2])

        self._set_combo_value(self.class_combo, question.get("class_name", ""))
        self.content_input.setPlainText(question.get("content", ""))
        self._set_combo_value(self.type_combo, question.get("type", ""))
        self.sub_category_input.setText(question.get("sub_category", ""))
        self._set_combo_value(self.difficulty_combo, question.get("difficulty", ""))
        self.answer_input.setText(question.get("answer", ""))
        self.allowed_answers_input.setText(question.get("allowed_answers", ""))
        self.explanation_input.setPlainText(question.get("explanation", ""))
        self.tags_input.setText(question.get("tags", ""))

    def clear_form(self) -> None:
        self.content_input.clear()
        self.sub_category_input.clear()
        self.answer_input.clear()
        self.allowed_answers_input.clear()
        self.explanation_input.clear()
        self.tags_input.clear()

    def set_submit_button_text(self, text: str) -> None:
        self.register_button.setText(text)

    def close_question_list_window(self) -> None:
        if self.question_list_window is not None:
            self.question_list_window.close()
            self.question_list_window = None

    def get_search_keyword(self) -> str:
        return self.keyword_input.text().strip()

    def get_selected_filters(self) -> dict[str, str]:
        filters = {
            "keyword": self.get_search_keyword(),
            "exam": self.exam_filter.currentText(),
            "class_name": self.class_filter.currentText(),
            "type": self.type_filter.currentText(),
            "sub_category": self.sub_category_filter.text().strip(),
            "difficulty": self.difficulty_filter.currentText(),
            "tag": self.tag_filter.text().strip(),
        }

        if filters["exam"] == "전체 시험":
            filters["exam"] = ""
        if filters["class_name"] == "전체 반":
            filters["class_name"] = ""
        if filters["type"] == "전체 유형":
            filters["type"] = ""
        if filters["difficulty"] == "전체 난이도":
            filters["difficulty"] = ""

        return filters

    def get_filter_data(self) -> dict[str, str]:
        return {
            "keyword": self.keyword_input.text().strip(),
            "exam": self.exam_filter.currentText(),
            "class_name": self.class_filter.currentText(),
            "type": self.type_filter.currentText(),
            "sub_category": self.sub_category_filter.text().strip(),
            "difficulty": self.difficulty_filter.currentText(),
            "tag": self.tag_filter.text().strip(),
        }

    def _get_selected_exam_name(self) -> str:
        year = self.exam_year_input.text().strip()
        year_label = year if year.endswith("년") else f"{year}년"
        return f"{year_label} {self.semester_combo.currentText()} {self.exam_type_combo.currentText()}"

    def _set_combo_value(self, combo: QComboBox, value: str) -> None:
        if not value:
            return
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _on_reset_filter_clicked(self) -> None:
        self.clear_filters()

    def clear_filters(self) -> None:
        self.keyword_input.clear()
        self.exam_filter.setCurrentIndex(0)
        self.class_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.sub_category_filter.clear()
        self.difficulty_filter.setCurrentIndex(0)
        self.tag_filter.clear()

    def _on_open_question_list_clicked(self) -> None:
        self.question_list_window = QuestionListDialog(self.questions_data, self)
        self.question_list_window.showMaximized()

    def _build_register_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        title = QLabel("문제 등록")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.exam_year_input = QLineEdit()
        self.exam_year_input.setValidator(QIntValidator(2000, 2099, self))
        self.exam_year_input.setPlaceholderText("예: 2024")
        self.exam_year_input.setText("2024")
        self.semester_combo = QComboBox()
        self.semester_combo.addItems(["1학기", "2학기"])
        self.exam_type_combo = QComboBox()
        self.exam_type_combo.addItems(["중간고사", "기말고사"])
        self.class_combo = QComboBox()
        self.class_combo.addItems(["1학년 1반", "1학년 2반", "1학년 3반"])
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("문제 내용 입력")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["어휘", "문법", "독해"])
        self.sub_category_input = QLineEdit()
        self.sub_category_input.setPlaceholderText("세부 분류 입력")
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["쉬움", "보통", "어려움"])
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("기준 정답 입력")
        self.allowed_answers_input = QLineEdit()
        self.allowed_answers_input.setPlaceholderText("허용 답안 입력")
        self.explanation_input = QTextEdit()
        self.explanation_input.setPlaceholderText("해설 입력")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("태그 입력")

        form.addWidget(self._make_labeled_widget("연도", self.exam_year_input), 0, 0)
        form.addWidget(self._make_labeled_widget("학기", self.semester_combo), 0, 1)
        form.addWidget(self._make_labeled_widget("시험 구분", self.exam_type_combo), 0, 2)
        form.addWidget(self._make_labeled_widget("반", self.class_combo), 0, 3)
        form.addWidget(self._make_labeled_widget("문제 내용", self.content_input), 1, 0, 2, 2)
        form.addWidget(self._make_labeled_widget("문제 유형", self.type_combo), 1, 2)
        form.addWidget(self._make_labeled_widget("세부 분류", self.sub_category_input), 1, 3)
        form.addWidget(self._make_labeled_widget("난이도", self.difficulty_combo), 2, 2)
        form.addWidget(self._make_labeled_widget("기준 정답", self.answer_input), 2, 3)
        form.addWidget(self._make_labeled_widget("허용 답안", self.allowed_answers_input), 3, 0)
        form.addWidget(self._make_labeled_widget("해설", self.explanation_input), 3, 1, 1, 2)
        form.addWidget(self._make_labeled_widget("태그", self.tags_input), 3, 3)
        layout.addLayout(form)

        button_row = QHBoxLayout()
        button_row.addStretch()
        self.register_button = QPushButton("문제 등록")
        self.register_button.setObjectName("primaryButton")
        self.register_button.setFixedWidth(130)
        button_row.addWidget(self.register_button)
        layout.addLayout(button_row)

        return card

    def _build_filter_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title = QLabel("문제 검색 / 필터")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        filters = QHBoxLayout()
        filters.setSpacing(10)

        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("검색어 입력")
        self.exam_filter = QComboBox()
        self.exam_filter.addItems(["전체 시험", "2024년 1학기 중간고사", "2024년 1학기 기말고사", "2024년 2학기 중간고사"])
        self.class_filter = QComboBox()
        self.class_filter.addItems(["전체 반", "1학년 1반", "1학년 2반", "1학년 3반"])
        self.type_filter = QComboBox()
        self.type_filter.addItems(["전체 유형", "어휘", "문법", "독해"])
        self.sub_category_filter = QLineEdit()
        self.sub_category_filter.setPlaceholderText("세부 분류")
        self.difficulty_filter = QComboBox()
        self.difficulty_filter.addItems(["전체 난이도", "쉬움", "보통", "어려움"])
        self.tag_filter = QLineEdit()
        self.tag_filter.setPlaceholderText("태그")

        self.search_button = QPushButton("검색")
        self.search_button.setObjectName("primaryButton")
        self.reset_filter_button = QPushButton("초기화")

        filters.addWidget(self.keyword_input, 2)
        filters.addWidget(self.exam_filter, 2)
        filters.addWidget(self.class_filter, 1)
        filters.addWidget(self.type_filter, 1)
        filters.addWidget(self.sub_category_filter, 1)
        filters.addWidget(self.difficulty_filter, 1)
        filters.addWidget(self.tag_filter, 1)
        filters.addWidget(self.search_button)
        filters.addWidget(self.reset_filter_button)
        layout.addLayout(filters)

        return card

    def _build_table_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("문제 목록")
        title.setObjectName("cardTitle")
        list_button = QPushButton("전체 보기")
        list_button.setFixedWidth(100)
        list_button.clicked.connect(self._on_open_question_list_clicked)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(list_button)
        layout.addLayout(header)

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

    def _make_table_button_cell(self, text: str, object_name: str, on_clicked=None, enabled: bool = True) -> QWidget:
        cell = QWidget()
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(self._make_table_button(text, object_name, on_clicked, enabled))
        layout.addStretch()
        return cell

    def _make_table_button(self, text: str, object_name: str, on_clicked=None, enabled: bool = True) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setFixedSize(78, 26)
        button.setEnabled(enabled)
        if on_clicked is not None:
            button.clicked.connect(on_clicked)
        return button


class QuestionListDialog(QDialog):
    def __init__(self, questions: list[dict[str, str]], parent: QuestionBankView | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("문제 목록")
        self.resize(1400, 820)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 24)
        layout.setSpacing(14)

        title = QLabel("문제 목록")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels(
            ["시험", "반", "문제 내용", "유형", "세부 분류", "난이도", "기준 정답", "태그", "상태", "수정", "상태 변경"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.setColumnWidth(2, 520)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.table, 1)

        if parent is not None:
            parent._fill_questions_table(self.table, questions)

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
            QPushButton {
                background: white;
                border: 1px solid #d8e0ea;
                border-radius: 6px;
                color: #27384c;
                font-weight: 700;
                min-height: 24px;
                padding: 0;
            }
            QPushButton#editButton {
                color: #1f6fc2;
            }
            QPushButton#disableButton {
                color: #b54708;
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

    def set_questions_data(self, questions: list[dict[str, str]]) -> None:
        parent = self.parent()
        if isinstance(parent, QuestionBankView):
            parent._fill_questions_table(self.table, questions)
