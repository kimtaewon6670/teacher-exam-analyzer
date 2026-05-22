from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
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


class StudentManageView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("studentManageView")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(16)

        title = QLabel("학생 관리")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        layout.addWidget(self._build_register_card())
        layout.addWidget(self._build_search_card())
        layout.addWidget(self._build_table_card(), 1)

        self.set_students_data(
            [
                {"name": "김민수", "student_id": "2024001", "class_name": "1학년 1반", "status": "활성"},
                {"name": "이서연", "student_id": "2024002", "class_name": "1학년 1반", "status": "활성"},
                {"name": "박지훈", "student_id": "2024003", "class_name": "1학년 2반", "status": "활성"},
                {"name": "최유진", "student_id": "2024004", "class_name": "1학년 2반", "status": "비활성"},
                {"name": "정하랑", "student_id": "2024005", "class_name": "1학년 3반", "status": "활성"},
            ]
        )

        self.setStyleSheet(
            """
            #studentManageView {
                background: #f4f7fb;
                color: #172033;
                font-family: "Malgun Gothic", "Segoe UI", Arial;
            }
            #pageTitle {
                font-size: 26px;
                font-weight: 800;
                color: #18263a;
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
            QLineEdit, QComboBox {
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
            QPushButton#editButton {
                color: #1f6fc2;
                min-height: 24px;
                max-height: 24px;
                padding: 0;
            }
            QPushButton#disableButton {
                color: #b54708;
                min-height: 24px;
                max-height: 24px;
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

    def set_students_data(self, students: list[dict[str, str]]) -> None:
        self.students_table.setRowCount(len(students))

        for row_index, student in enumerate(students):
            values = [
                student.get("name", ""),
                student.get("student_id", ""),
                student.get("class_name", ""),
                student.get("status", ""),
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.students_table.setItem(row_index, column_index, item)

            self.students_table.setCellWidget(row_index, 4, self._make_table_button_cell("수정", "editButton"))
            self.students_table.setCellWidget(row_index, 5, self._make_table_button_cell("비활성화", "disableButton"))
            self.students_table.setRowHeight(row_index, 38)

    def _build_register_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        title = QLabel("학생 등록")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        fields = QHBoxLayout()
        fields.setSpacing(12)

        self.name_input = self._make_labeled_input(fields, "학생 이름", "이름 입력")
        self.student_id_input = self._make_labeled_input(fields, "학번", "학번 입력")
        self.class_input = self._make_labeled_input(fields, "반 정보", "예: 1학년 1반")

        register_button = QPushButton("학생 등록")
        register_button.setObjectName("primaryButton")
        register_button.setFixedWidth(130)
        fields.addWidget(register_button, 0, Qt.AlignBottom)

        layout.addLayout(fields)
        return card

    def _build_search_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title = QLabel("학생 검색")
        title.setObjectName("cardTitle")
        title.setFixedWidth(90)
        layout.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("이름 또는 학번 검색")
        layout.addWidget(self.search_input, 1)

        self.class_filter = QComboBox()
        self.class_filter.addItems(["전체 반", "1학년 1반", "1학년 2반", "1학년 3반"])
        self.class_filter.setFixedWidth(160)
        layout.addWidget(self.class_filter)

        return card

    def _build_table_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        title = QLabel("학생 목록")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        self.students_table = QTableWidget(0, 6)
        self.students_table.setHorizontalHeaderLabels(["이름", "학번", "반", "상태", "수정", "비활성화"])
        self.students_table.verticalHeader().setVisible(False)
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.students_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.students_table.setSelectionMode(QTableWidget.NoSelection)
        self.students_table.setAlternatingRowColors(False)
        layout.addWidget(self.students_table, 1)

        return card

    def _make_labeled_input(self, parent_layout: QHBoxLayout, label_text: str, placeholder: str) -> QLineEdit:
        field = QWidget()
        layout = QVBoxLayout(field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel(label_text)
        label.setObjectName("fieldLabel")

        input_box = QLineEdit()
        input_box.setPlaceholderText(placeholder)

        layout.addWidget(label)
        layout.addWidget(input_box)
        parent_layout.addWidget(field, 1)

        return input_box

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
