from __future__ import annotations

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ExamBuilderView(QWidget):
    auto_extract_requested = Signal()
    manual_select_requested = Signal()
    selection_clear_requested = Signal()
    preview_requested = Signal()
    pdf_export_requested = Signal()
    save_exam_requested = Signal()
    question_exclude_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("examBuilderView")
        self.selected_questions: list[dict[str, object]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(16)

        title = QLabel("시험지 생성")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)
        top_row.addWidget(self._build_exam_info_card(), 1)
        top_row.addWidget(self._build_condition_card(), 1)
        layout.addLayout(top_row)

        layout.addWidget(self._build_selection_action_card())
        layout.addWidget(self._build_selected_questions_card(), 1)
        layout.addWidget(self._build_output_action_card())

        self._connect_total_count_updates()
        self.set_filter_options(
            {
                "question_types": ["어휘", "문법", "독해"],
                "sub_categories": ["시제", "수동태", "관계대명사", "주제 찾기"],
                "tags": ["중간고사", "기말고사", "문법", "독해", "빈출"],
                "classes": ["1학년 1반", "1학년 2반", "1학년 3반"],
            }
        )
        self.set_selected_questions(
            [
                {
                    "question_id": 101,
                    "content": "빈칸에 들어갈 알맞은 단어를 고르시오.",
                    "type": "어휘",
                    "sub_category": "동의어",
                    "difficulty": "쉬움",
                    "answer": "important",
                    "tags": "vocabulary, basic",
                },
                {
                    "question_id": 102,
                    "content": "다음 문장에서 어법상 틀린 부분을 고르시오.",
                    "type": "문법",
                    "sub_category": "시제",
                    "difficulty": "보통",
                    "answer": "has gone",
                    "tags": "grammar, tense",
                },
                {
                    "question_id": 103,
                    "content": "글의 주제로 가장 적절한 것을 고르시오.",
                    "type": "독해",
                    "sub_category": "주제 찾기",
                    "difficulty": "어려움",
                    "answer": "environmental protection",
                    "tags": "reading, topic",
                },
            ]
        )

        self.setStyleSheet(
            """
            #examBuilderView {
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
            #totalCountLabel {
                color: #172033;
                font-size: 20px;
                font-weight: 800;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {
                background: white;
                border: 1px solid #d8e0ea;
                border-radius: 6px;
                color: #28384c;
                padding: 8px 10px;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
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
            QPushButton#dangerButton {
                color: #b54708;
            }
            QPushButton#tableButton {
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

    def get_exam_form_data(self) -> dict[str, str]:
        return {
            "exam_name": self.exam_name_input.text().strip(),
            "description": self.exam_description_input.toPlainText().strip(),
            "year": self.year_input.text().strip(),
            "semester": self.semester_combo.currentText(),
            "exam_type": self.exam_type_combo.currentText(),
            "class_name": self.class_combo.currentText().strip(),
            "exam_date": self.exam_date_edit.date().toString("yyyy-MM-dd"),
        }

    def get_exam_condition_data(self) -> dict[str, object]:
        return {
            "type_counts": {
                "vocabulary": self.vocabulary_count_input.value(),
                "grammar": self.grammar_count_input.value(),
                "reading": self.reading_count_input.value(),
            },
            "difficulty_counts": {
                "easy": self.easy_count_input.value(),
                "normal": self.normal_count_input.value(),
                "hard": self.hard_count_input.value(),
            },
            "sub_category": self.sub_category_combo.currentText().strip(),
            "tag": self.tag_combo.currentText().strip(),
            "total_count": self._calculate_total_count(),
        }

    def set_selected_questions(self, questions: list[dict[str, object]]) -> None:
        self.selected_questions = questions
        self.selected_questions_table.setRowCount(len(questions))

        for row_index, question in enumerate(questions):
            values = [
                str(row_index + 1),
                str(question.get("content", "")),
                str(question.get("type", "")),
                str(question.get("sub_category", "")),
                str(question.get("difficulty", "")),
                str(question.get("answer", "")),
                str(question.get("tags", "")),
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                alignment = Qt.AlignLeft | Qt.AlignVCenter if column_index == 1 else Qt.AlignCenter
                item.setTextAlignment(alignment)
                self.selected_questions_table.setItem(row_index, column_index, item)

            question_id = question.get("question_id")
            self.selected_questions_table.setCellWidget(
                row_index,
                7,
                self._make_table_button_cell("제외", lambda checked=False, qid=question_id: self._exclude_question(qid)),
            )
            self.selected_questions_table.setRowHeight(row_index, 40)

    def get_selected_question_ids(self) -> list[object]:
        return [question.get("question_id") for question in self.selected_questions if question.get("question_id") is not None]

    def clear_form(self) -> None:
        self.exam_name_input.clear()
        self.exam_description_input.clear()
        self.year_input.setText(str(QDate.currentDate().year()))
        self.semester_combo.setCurrentIndex(0)
        self.exam_type_combo.setCurrentIndex(0)
        self.class_combo.setCurrentIndex(0)
        self.exam_date_edit.setDate(QDate.currentDate())
        self.vocabulary_count_input.setValue(0)
        self.grammar_count_input.setValue(0)
        self.reading_count_input.setValue(0)
        self.easy_count_input.setValue(0)
        self.normal_count_input.setValue(0)
        self.hard_count_input.setValue(0)
        self.sub_category_combo.setCurrentIndex(0)
        self.tag_combo.setCurrentIndex(0)
        self.set_selected_questions([])
        self._update_total_count()

    def show_message(self, message: str) -> None:
        QMessageBox.information(self, "안내", message)

    def set_filter_options(self, options: dict[str, list[str]]) -> None:
        self._set_combo_options(self.sub_category_combo, ["전체 분류"] + options.get("sub_categories", []))
        self._set_combo_options(self.tag_combo, ["전체 태그"] + options.get("tags", []))
        self._set_combo_options(self.class_combo, options.get("classes", ["1학년 1반"]))

    def _build_exam_info_card(self) -> QFrame:
        card = self._make_card("시험 기본 정보")
        layout = card.layout()

        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.exam_name_input = QLineEdit()
        self.exam_name_input.setPlaceholderText("시험명 입력")
        self.exam_description_input = QTextEdit()
        self.exam_description_input.setPlaceholderText("시험 설명 입력")
        self.year_input = QLineEdit(str(QDate.currentDate().year()))
        self.year_input.setValidator(QIntValidator(2000, 2099, self))
        self.year_input.setPlaceholderText("예: 2026")
        self.semester_combo = QComboBox()
        self.semester_combo.addItems(["1학기", "2학기"])
        self.exam_type_combo = QComboBox()
        self.exam_type_combo.addItems(["중간고사", "기말고사", "수행평가", "기타"])
        self.class_combo = QComboBox()
        self.class_combo.setEditable(True)
        self.exam_date_edit = QDateEdit(QDate.currentDate())
        self.exam_date_edit.setCalendarPopup(True)
        self.exam_date_edit.setDisplayFormat("yyyy-MM-dd")

        form.addWidget(self._make_labeled_widget("시험명", self.exam_name_input), 0, 0, 1, 2)
        form.addWidget(self._make_labeled_widget("연도", self.year_input), 0, 2)
        form.addWidget(self._make_labeled_widget("학기", self.semester_combo), 0, 3)
        form.addWidget(self._make_labeled_widget("시험 설명", self.exam_description_input), 1, 0, 2, 2)
        form.addWidget(self._make_labeled_widget("시험 구분", self.exam_type_combo), 1, 2)
        form.addWidget(self._make_labeled_widget("대상 반", self.class_combo), 1, 3)
        form.addWidget(self._make_labeled_widget("시험 일자", self.exam_date_edit), 2, 2, 1, 2)
        layout.addLayout(form)
        return card

    def _build_condition_card(self) -> QFrame:
        card = self._make_card("문제 추출 조건")
        layout = card.layout()

        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.vocabulary_count_input = self._make_spin_box()
        self.grammar_count_input = self._make_spin_box()
        self.reading_count_input = self._make_spin_box()
        self.easy_count_input = self._make_spin_box()
        self.normal_count_input = self._make_spin_box()
        self.hard_count_input = self._make_spin_box()
        self.sub_category_combo = QComboBox()
        self.sub_category_combo.setEditable(True)
        self.tag_combo = QComboBox()
        self.tag_combo.setEditable(True)
        self.total_count_label = QLabel("0문항")
        self.total_count_label.setObjectName("totalCountLabel")
        self.total_count_label.setAlignment(Qt.AlignCenter)

        form.addWidget(self._make_labeled_widget("어휘 문항 수", self.vocabulary_count_input), 0, 0)
        form.addWidget(self._make_labeled_widget("문법 문항 수", self.grammar_count_input), 0, 1)
        form.addWidget(self._make_labeled_widget("독해 문항 수", self.reading_count_input), 0, 2)
        form.addWidget(self._make_labeled_widget("총 문항 수", self.total_count_label), 0, 3)
        form.addWidget(self._make_labeled_widget("쉬움", self.easy_count_input), 1, 0)
        form.addWidget(self._make_labeled_widget("보통", self.normal_count_input), 1, 1)
        form.addWidget(self._make_labeled_widget("어려움", self.hard_count_input), 1, 2)
        form.addWidget(self._make_labeled_widget("세부 분류 필터", self.sub_category_combo), 2, 0, 1, 2)
        form.addWidget(self._make_labeled_widget("태그 필터", self.tag_combo), 2, 2, 1, 2)
        layout.addLayout(form)
        return card

    def _build_selection_action_card(self) -> QFrame:
        card = self._make_card("문제 선택 방식")
        layout = card.layout()

        row = QHBoxLayout()
        row.setSpacing(10)
        auto_button = QPushButton("자동 추출")
        auto_button.setObjectName("primaryButton")
        manual_button = QPushButton("직접 선택")
        clear_button = QPushButton("선택 초기화")
        clear_button.setObjectName("dangerButton")

        auto_button.clicked.connect(self.auto_extract_requested.emit)
        manual_button.clicked.connect(self.manual_select_requested.emit)
        clear_button.clicked.connect(self.selection_clear_requested.emit)
        clear_button.clicked.connect(lambda: self.set_selected_questions([]))

        row.addWidget(auto_button)
        row.addWidget(manual_button)
        row.addWidget(clear_button)
        row.addStretch()
        layout.addLayout(row)
        return card

    def _build_selected_questions_card(self) -> QFrame:
        card = self._make_card("선택된 문제 목록")
        layout = card.layout()

        self.selected_questions_table = QTableWidget(0, 8)
        self.selected_questions_table.setHorizontalHeaderLabels(
            ["순번", "문제 내용", "유형", "세부 분류", "난이도", "기준 정답", "태그", "제외"]
        )
        self.selected_questions_table.verticalHeader().setVisible(False)
        self.selected_questions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.selected_questions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.selected_questions_table.setColumnWidth(1, 420)
        self.selected_questions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.selected_questions_table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.selected_questions_table, 1)
        return card

    def _build_output_action_card(self) -> QFrame:
        card = self._make_card("시험지 미리보기 / 저장")
        layout = card.layout()

        row = QHBoxLayout()
        row.setSpacing(10)
        preview_button = QPushButton("시험지 미리보기")
        pdf_button = QPushButton("PDF 출력")
        save_button = QPushButton("시험지 저장")
        save_button.setObjectName("primaryButton")

        preview_button.clicked.connect(self.preview_requested.emit)
        pdf_button.clicked.connect(self.pdf_export_requested.emit)
        save_button.clicked.connect(self.save_exam_requested.emit)

        row.addStretch()
        row.addWidget(preview_button)
        row.addWidget(pdf_button)
        row.addWidget(save_button)
        layout.addLayout(row)
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

    def _make_spin_box(self) -> QSpinBox:
        spin_box = QSpinBox()
        spin_box.setRange(0, 200)
        return spin_box

    def _make_table_button_cell(self, text: str, on_clicked) -> QWidget:
        cell = QWidget()
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        button = QPushButton(text)
        button.setObjectName("tableButton")
        button.setFixedSize(64, 26)
        button.clicked.connect(on_clicked)
        layout.addWidget(button)
        layout.addStretch()
        return cell

    def _connect_total_count_updates(self) -> None:
        for spin_box in [
            self.vocabulary_count_input,
            self.grammar_count_input,
            self.reading_count_input,
            self.easy_count_input,
            self.normal_count_input,
            self.hard_count_input,
        ]:
            spin_box.valueChanged.connect(self._update_total_count)

    def _calculate_total_count(self) -> int:
        return self.vocabulary_count_input.value() + self.grammar_count_input.value() + self.reading_count_input.value()

    def _update_total_count(self) -> None:
        self.total_count_label.setText(f"{self._calculate_total_count()}문항")

    def _exclude_question(self, question_id: object) -> None:
        self.question_exclude_requested.emit(question_id)
        self.set_selected_questions(
            [question for question in self.selected_questions if question.get("question_id") != question_id]
        )

    def _set_combo_options(self, combo: QComboBox, values: list[str]) -> None:
        current = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(values)
        if current:
            index = combo.findText(current)
            if index >= 0:
                combo.setCurrentIndex(index)
        combo.blockSignals(False)
