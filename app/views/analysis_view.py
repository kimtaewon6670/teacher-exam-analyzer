from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class AnalysisView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("analysisView")
        self._exam_ids: list[object] = []
        self._class_ids: list[object] = []
        self._summary_value_labels: dict[str, QLabel] = {}

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root_layout.addWidget(scroll)

        content = QWidget()
        content.setMinimumWidth(1080)
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(16)

        title = QLabel("결과 분석")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        layout.addWidget(self._build_filter_card())
        layout.addLayout(self._build_summary_cards())
        layout.addWidget(self._build_question_analysis_card())

        middle_row = QHBoxLayout()
        middle_row.setSpacing(16)
        middle_row.addWidget(self._build_type_analysis_card(), 1)
        middle_row.addWidget(self._build_difficulty_analysis_card(), 1)
        layout.addLayout(middle_row)

        layout.addWidget(self._build_sub_category_analysis_card())
        layout.addStretch()

        self.setStyleSheet(
            """
            #analysisView {
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
            #metricLabel {
                color: #75849a;
                font-size: 12px;
                font-weight: 700;
            }
            #metricValue {
                color: #172033;
                font-size: 24px;
                font-weight: 800;
            }
            #fieldLabel, #graphPlaceholder, #interpretationLabel, #weaknessLabel {
                color: #53657a;
                font-size: 13px;
            }
            #graphPlaceholder {
                background: #f7f9fc;
                border: 1px dashed #cbd6e2;
                border-radius: 8px;
                padding: 18px;
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

    def get_analysis_filter_data(self) -> dict[str, object]:
        return {
            "exam_id": self._get_selected_id(self._exam_ids, self.exam_combo.currentIndex()),
            "class_id": self._get_selected_id(self._class_ids, self.class_combo.currentIndex()),
            "basis": self.basis_combo.currentText(),
        }

    def set_summary_data(self, summary: dict[str, object]) -> None:
        label_map = {
            "student_count": "응시 학생 수",
            "average_score": "반 전체 평균 점수",
            "correct_rate": "전체 정답률",
            "wrong_rate": "전체 오답률",
            "weak_type": "가장 취약한 문제 유형",
        }
        for key, title in label_map.items():
            value_label = self._summary_value_labels.get(title)
            if value_label is not None:
                value_label.setText(str(summary.get(key, "-")))

    def set_question_analysis_data(self, rows: list[dict[str, object]]) -> None:
        self._fill_table(
            self.question_table,
            rows,
            ["question_number", "content", "type", "sub_category", "difficulty", "correct_rate", "wrong_rate"],
        )

    def set_type_analysis_data(self, rows: list[dict[str, object]]) -> None:
        self._fill_table(self.type_table, rows, ["type", "correct_rate", "wrong_rate"])
        weakest = min(rows, key=lambda row: float(row.get("correct_rate", 100)), default={})
        self.type_graph_label.setText(self._build_rate_graph(rows, "type", f"가장 낮은 유형: {weakest.get('type', '-')}"))

    def set_sub_category_analysis_data(self, rows: list[dict[str, object]]) -> None:
        self._fill_table(self.sub_category_table, rows, ["sub_category", "correct_rate", "wrong_rate"])
        weakest = min(rows, key=lambda row: float(row.get("correct_rate", 100)), default={})
        self.sub_category_graph_label.setText(
            self._build_rate_graph(rows, "sub_category", f"취약 세부 분류: {weakest.get('sub_category', '-')}")
        )

    def set_difficulty_analysis_data(self, rows: list[dict[str, object]]) -> None:
        self._fill_table(self.difficulty_table, rows, ["difficulty", "correct_rate", "wrong_rate"])
        self.difficulty_graph_label.setText(self._build_rate_graph(rows, "difficulty", "난이도별 정답률"))

    def set_weakness_summary(self, data: dict[str, object]) -> None:
        pass

    def clear_analysis(self) -> None:
        for value_label in self._summary_value_labels.values():
            value_label.setText("-")
        for table in [self.question_table, self.type_table, self.sub_category_table, self.difficulty_table]:
            table.setRowCount(0)
        self.set_weakness_summary({})

    def show_message(self, message: str) -> None:
        QMessageBox.information(self, "안내", message)

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self, "오류", message)

    def _build_filter_card(self) -> QFrame:
        card = self._make_card("분석 조건 선택")
        layout = card.layout()
        row = QHBoxLayout()
        row.setSpacing(10)

        self.exam_combo = QComboBox()
        self.class_combo = QComboBox()
        self.basis_combo = QComboBox()
        self.basis_combo.addItems(["전체", "문제 유형별", "세부 분류별", "난이도별"])
        self.search_button = QPushButton("분석 조회")
        self.search_button.setObjectName("primaryButton")
        self.reset_button = QPushButton("초기화")

        row.addWidget(self._make_labeled_widget("시험 선택", self.exam_combo), 2)
        row.addWidget(self._make_labeled_widget("반 선택", self.class_combo), 1)
        row.addWidget(self._make_labeled_widget("분석 기준", self.basis_combo), 1)
        row.addWidget(self.search_button, 0, Qt.AlignBottom)
        row.addWidget(self.reset_button, 0, Qt.AlignBottom)
        layout.addLayout(row)
        return card

    def _build_summary_cards(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        titles = ["응시 학생 수", "반 전체 평균 점수", "전체 정답률", "전체 오답률", "가장 취약한 문제 유형"]
        for index, title in enumerate(titles):
            card = QFrame()
            card.setObjectName("card")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(16, 14, 16, 14)
            label = QLabel(title)
            label.setObjectName("metricLabel")
            value = QLabel("-")
            value.setObjectName("metricValue")
            layout.addWidget(label)
            layout.addWidget(value)
            self._summary_value_labels[title] = value
            grid.addWidget(card, index // 3, index % 3)
        return grid

    def _build_question_analysis_card(self) -> QFrame:
        card = self._make_card("문항별 정답률/오답률 분석")
        layout = card.layout()
        self.question_table = QTableWidget(0, 7)
        self.question_table.setHorizontalHeaderLabels(["문항 번호", "문제 내용", "문제 유형", "세부 분류", "난이도", "정답률", "오답률"])
        self._setup_table(self.question_table)
        self.question_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.question_table.setColumnWidth(1, 360)
        layout.addWidget(self.question_table)
        return card

    def _build_type_analysis_card(self) -> QFrame:
        card = self._make_card("문제 유형별 정답률 분석")
        layout = card.layout()
        self.type_table = QTableWidget(0, 3)
        self.type_table.setHorizontalHeaderLabels(["유형", "정답률", "오답률"])
        self._setup_table(self.type_table)
        self.type_graph_label = self._make_graph_placeholder()
        layout.addWidget(self.type_table)
        layout.addWidget(self.type_graph_label)
        return card

    def _build_sub_category_analysis_card(self) -> QFrame:
        card = self._make_card("세부 분류별 정답률 분석")
        layout = card.layout()
        self.sub_category_table = QTableWidget(0, 3)
        self.sub_category_table.setHorizontalHeaderLabels(["세부 분류", "정답률", "오답률"])
        self._setup_table(self.sub_category_table)
        self.sub_category_graph_label = self._make_graph_placeholder()
        layout.addWidget(self.sub_category_table)
        layout.addWidget(self.sub_category_graph_label)
        return card

    def _build_difficulty_analysis_card(self) -> QFrame:
        card = self._make_card("난이도별 정답률 분석")
        layout = card.layout()
        self.difficulty_table = QTableWidget(0, 3)
        self.difficulty_table.setHorizontalHeaderLabels(["난이도", "정답률", "오답률"])
        self._setup_table(self.difficulty_table)
        self.difficulty_graph_label = self._make_graph_placeholder()
        layout.addWidget(self.difficulty_table)
        layout.addWidget(self.difficulty_graph_label)
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

    def _make_metric_inline(self, title: str) -> QLabel:
        label = QLabel("-")
        label.setObjectName("metricValue")
        return label

    def _make_graph_placeholder(self) -> QLabel:
        label = QLabel("그래프 placeholder")
        label.setObjectName("graphPlaceholder")
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumHeight(96)
        return label

    def _setup_table(self, table: QTableWidget) -> None:
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)

    def _fill_table(self, table: QTableWidget, rows: list[dict[str, object]], keys: list[str]) -> None:
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, key in enumerate(keys):
                item = QTableWidgetItem(str(row.get(key, "")))
                alignment = Qt.AlignLeft | Qt.AlignVCenter if key == "content" else Qt.AlignCenter
                item.setTextAlignment(alignment)
                table.setItem(row_index, column_index, item)
            table.setRowHeight(row_index, 36)

    def _build_rate_graph(self, rows: list[dict[str, object]], label_key: str, title: str) -> str:
        if not rows:
            return f"{title}\n분석할 데이터가 없습니다."

        lines = [title]
        for row in rows:
            label = str(row.get(label_key, "-"))
            try:
                rate = float(row.get("correct_rate", 0))
            except (TypeError, ValueError):
                rate = 0
            bar = "█" * max(1, int(rate // 10)) if rate > 0 else "-"
            lines.append(f"{label:<8} {bar} {rate:.1f}%")
        return "\n".join(lines)

    def _get_selected_id(self, ids: list[object], index: int) -> object | None:
        if 0 <= index < len(ids):
            return ids[index]
        return None
