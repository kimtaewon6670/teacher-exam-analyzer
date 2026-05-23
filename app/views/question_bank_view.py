from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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

        self.set_questions_data(
            [
                {
                    "content": "빈칸에 들어갈 알맞은 단어를 고르시오.",
                    "type": "어휘",
                    "sub_category": "동의어",
                    "difficulty": "쉬움",
                    "answer": "important",
                    "tags": "vocabulary, basic",
                    "status": "활성",
                },
                {
                    "content": "다음 문장에서 어법상 틀린 부분을 고르시오.",
                    "type": "문법",
                    "sub_category": "시제",
                    "difficulty": "보통",
                    "answer": "has went",
                    "tags": "grammar, tense",
                    "status": "활성",
                },
                {
                    "content": "글의 주제로 가장 적절한 것을 고르시오.",
                    "type": "독해",
                    "sub_category": "주제 찾기",
                    "difficulty": "보통",
                    "answer": "environmental protection",
                    "tags": "reading, topic",
                    "status": "활성",
                },
                {
                    "content": "밑줄 친 표현의 의미로 가장 적절한 것을 고르시오.",
                    "type": "어휘",
                    "sub_category": "문맥 의미",
                    "difficulty": "어려움",
                    "answer": "give up",
                    "tags": "idiom, context",
                    "status": "비활성",
                },
            ]
        )

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
        self.questions_table.setRowCount(len(questions))

        for row_index, question in enumerate(questions):
            values = [
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
                alignment = Qt.AlignLeft | Qt.AlignVCenter if column_index == 0 else Qt.AlignCenter
                item.setTextAlignment(alignment)
                self.questions_table.setItem(row_index, column_index, item)

            self.questions_table.setCellWidget(row_index, 7, self._make_table_button_cell("수정", "editButton"))
            self.questions_table.setCellWidget(row_index, 8, self._make_table_button_cell("비활성화", "disableButton"))
            self.questions_table.setRowHeight(row_index, 40)

    def get_question_form_data(self) -> dict[str, str]:
        return {
            "content": self.content_input.toPlainText().strip(),
            "type": self.type_combo.currentText(),
            "sub_category": self.sub_category_input.text().strip(),
            "difficulty": self.difficulty_combo.currentText(),
            "answer": self.answer_input.text().strip(),
            "allowed_answers": self.allowed_answers_input.text().strip(),
            "explanation": self.explanation_input.toPlainText().strip(),
            "tags": self.tags_input.text().strip(),
        }

    def get_filter_data(self) -> dict[str, str]:
        return {
            "keyword": self.keyword_input.text().strip(),
            "type": self.type_filter.currentText(),
            "sub_category": self.sub_category_filter.text().strip(),
            "difficulty": self.difficulty_filter.currentText(),
            "tag": self.tag_filter.text().strip(),
        }

    def _on_register_clicked(self) -> None:
        pass

    def _on_search_clicked(self) -> None:
        pass

    def _on_reset_filter_clicked(self) -> None:
        self.keyword_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.sub_category_filter.clear()
        self.difficulty_filter.setCurrentIndex(0)
        self.tag_filter.clear()

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

        form.addWidget(self._make_labeled_widget("문제 내용", self.content_input), 0, 0, 2, 2)
        form.addWidget(self._make_labeled_widget("문제 유형", self.type_combo), 0, 2)
        form.addWidget(self._make_labeled_widget("세부 분류", self.sub_category_input), 0, 3)
        form.addWidget(self._make_labeled_widget("난이도", self.difficulty_combo), 1, 2)
        form.addWidget(self._make_labeled_widget("기준 정답", self.answer_input), 1, 3)
        form.addWidget(self._make_labeled_widget("허용 답안", self.allowed_answers_input), 2, 0)
        form.addWidget(self._make_labeled_widget("해설", self.explanation_input), 2, 1, 1, 2)
        form.addWidget(self._make_labeled_widget("태그", self.tags_input), 2, 3)
        layout.addLayout(form)

        button_row = QHBoxLayout()
        button_row.addStretch()
        register_button = QPushButton("문제 등록")
        register_button.setObjectName("primaryButton")
        register_button.setFixedWidth(130)
        register_button.clicked.connect(self._on_register_clicked)
        button_row.addWidget(register_button)
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
        self.type_filter = QComboBox()
        self.type_filter.addItems(["전체 유형", "어휘", "문법", "독해"])
        self.sub_category_filter = QLineEdit()
        self.sub_category_filter.setPlaceholderText("세부 분류")
        self.difficulty_filter = QComboBox()
        self.difficulty_filter.addItems(["전체 난이도", "쉬움", "보통", "어려움"])
        self.tag_filter = QLineEdit()
        self.tag_filter.setPlaceholderText("태그")

        search_button = QPushButton("검색")
        search_button.setObjectName("primaryButton")
        search_button.clicked.connect(self._on_search_clicked)
        reset_button = QPushButton("필터 초기화")
        reset_button.clicked.connect(self._on_reset_filter_clicked)

        filters.addWidget(self.keyword_input, 2)
        filters.addWidget(self.type_filter, 1)
        filters.addWidget(self.sub_category_filter, 1)
        filters.addWidget(self.difficulty_filter, 1)
        filters.addWidget(self.tag_filter, 1)
        filters.addWidget(search_button)
        filters.addWidget(reset_button)
        layout.addLayout(filters)

        return card

    def _build_table_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        title = QLabel("문제 목록")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        self.questions_table = QTableWidget(0, 9)
        self.questions_table.setHorizontalHeaderLabels(
            ["문제 내용", "유형", "세부 분류", "난이도", "기준 정답", "태그", "상태", "수정", "비활성화"]
        )
        self.questions_table.verticalHeader().setVisible(False)
        self.questions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.questions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.questions_table.setColumnWidth(0, 330)
        self.questions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.questions_table.setSelectionMode(QTableWidget.NoSelection)
        self.questions_table.setAlternatingRowColors(False)
        layout.addWidget(self.questions_table, 1)

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

    def _make_table_button_cell(self, text: str, object_name: str) -> QWidget:
        cell = QWidget()
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(self._make_table_button(text, object_name))
        layout.addStretch()
        return cell

    def _make_table_button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setFixedSize(78, 26)
        return button
