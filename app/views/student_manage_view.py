from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class StudentManageView(QWidget):
    def __init__(self, student_controller: Any) -> None:
        super().__init__()
        self.student_controller = student_controller
        self.setObjectName("studentManageView")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root_layout.addWidget(scroll)

        content = QWidget()
        content.setMinimumWidth(920)
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(16)

        title = QLabel("학생 관리")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        layout.addWidget(self._build_register_card())
        layout.addWidget(self._build_search_card())
        layout.addWidget(self._build_table_card(), 1)
        layout.addStretch()

        self._refresh_students()

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
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.students_table.setItem(row_index, column_index, item)

            student_db_id = student.get("id")
            is_active = student.get("status") == "활성"
            self.students_table.setCellWidget(
                row_index,
                4,
                self._make_table_button_cell(
                    "수정",
                    "editButton",
                    lambda checked=False, student=student: self._on_edit_clicked(student),
                ),
            )
            self.students_table.setCellWidget(
                row_index,
                5,
                self._make_table_button_cell(
                    "비활성화" if is_active else "활성화",
                    "disableButton",
                    lambda checked=False, student_id=student_db_id, is_active=is_active: self._on_status_change_clicked(
                        student_id,
                        is_active,
                    ),
                ),
            )
            self.students_table.setRowHeight(row_index, 38)

    def _refresh_students(self) -> None:
        keyword = self.search_input.text().strip()
        class_name = self.class_filter.currentText()
        if class_name == "전체 반":
            class_name = ""

        self.set_students_data(self.student_controller.search_students(keyword, class_name))

    def _on_register_clicked(self) -> None:
        name = self.name_input.text().strip()
        student_number = self.student_id_input.text().strip()
        class_name = self.class_input.text().strip()

        if not name or not student_number or not class_name:
            QMessageBox.warning(self, "입력 확인", "이름, 학번, 반 정보를 모두 입력해주세요.")
            return

        try:
            self.student_controller.create_student(name, student_number, class_name)
        except Exception as exc:
            QMessageBox.warning(self, "등록 실패", f"학생 등록 중 오류가 발생했습니다.\n{exc}")
            return

        self.name_input.clear()
        self.student_id_input.clear()
        self.class_input.clear()
        self._refresh_students()

    def _on_edit_clicked(self, student: dict[str, str]) -> None:
        edited_student = self._show_edit_dialog(student)
        if edited_student is None:
            return

        try:
            updated = self.student_controller.update_student(
                int(student["id"]),
                edited_student["name"],
                edited_student["student_id"],
                edited_student["class_name"],
            )
        except Exception as exc:
            QMessageBox.warning(self, "수정 실패", f"학생 정보 수정 중 오류가 발생했습니다.\n{exc}")
            return

        if not updated:
            QMessageBox.warning(self, "수정 실패", "수정할 학생을 찾을 수 없습니다.")
            return

        self._refresh_students()

    def _on_status_change_clicked(self, student_id: int | None, is_active: bool) -> None:
        if student_id is None:
            QMessageBox.warning(self, "상태 변경 실패", "상태를 변경할 학생을 찾을 수 없습니다.")
            return

        action_text = "비활성화" if is_active else "활성화"
        answer = QMessageBox.question(
            self,
            f"{action_text} 확인",
            f"선택한 학생을 {action_text}하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        try:
            changed = (
                self.student_controller.deactivate_student(int(student_id))
                if is_active
                else self.student_controller.activate_student(int(student_id))
            )
        except Exception as exc:
            QMessageBox.warning(self, f"{action_text} 실패", f"학생 {action_text} 중 오류가 발생했습니다.\n{exc}")
            return

        if not changed:
            QMessageBox.warning(self, f"{action_text} 실패", f"{action_text}할 학생을 찾을 수 없습니다.")
            return

        self._refresh_students()

    def _show_edit_dialog(self, student: dict[str, str]) -> dict[str, str] | None:
        dialog = QDialog(self)
        dialog.setWindowTitle("학생 정보 수정")

        layout = QFormLayout(dialog)
        name_input = QLineEdit(student.get("name", ""))
        student_number_input = QLineEdit(student.get("student_id", ""))
        class_name_input = QLineEdit(student.get("class_name", ""))

        layout.addRow("학생 이름", name_input)
        layout.addRow("학번", student_number_input)
        layout.addRow("반 정보", class_name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return None

        edited_student = {
            "name": name_input.text().strip(),
            "student_id": student_number_input.text().strip(),
            "class_name": class_name_input.text().strip(),
        }
        if not edited_student["name"] or not edited_student["student_id"] or not edited_student["class_name"]:
            QMessageBox.warning(self, "입력 확인", "이름, 학번, 반 정보를 모두 입력해주세요.")
            return None

        return edited_student

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
        register_button.clicked.connect(self._on_register_clicked)
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
        self.search_input.textChanged.connect(self._refresh_students)
        layout.addWidget(self.search_input, 1)

        self.class_filter = QComboBox()
        self.class_filter.addItems(["전체 반", "1학년 1반", "1학년 2반", "1학년 3반"])
        self.class_filter.currentTextChanged.connect(self._refresh_students)
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
        self.students_table.setHorizontalHeaderLabels(["이름", "학번", "반", "상태", "수정", "상태 변경"])
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
