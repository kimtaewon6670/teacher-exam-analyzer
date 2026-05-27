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
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(16)

        title = QLabel("결과 분석")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        layout.addWidget(self._build_filter_card())
        layout.addLayout(self._build_summary_cards())
        layout.addWidget(self._build_class_analysis_card())
        layout.addWidget(self._build_question_analysis_card())

        middle_row = QHBoxLayout()
        middle_row.setSpacing(16)
        middle_row.addWidget(self._build_type_analysis_card(), 1)
        middle_row.addWidget(self._build_difficulty_analysis_card(), 1)
        layout.addLayout(middle_row)

        layout.addWidget(self._build_sub_category_analysis_card())
        layout.addWidget(self._build_weakness_card())
        layout.addStretch()

        self._load_sample_data()
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
            "weak_difficulty": "가장 취약한 난이도",
        }
        for key, title in label_map.items():
            value_label = self._summary_value_labels.get(title)
            if value_label is not None:
                value_label.setText(str(summary.get(key, "-")))

        self.class_average_label.setText(str(summary.get("average_score", "-")))
        self.class_correct_rate_label.setText(str(summary.get("correct_rate", "-")))
        self.class_wrong_rate_label.setText(str(summary.get("wrong_rate", "-")))
        self.class_interpretation_label.setText(str(summary.get("interpretation", "")))

    def set_question_analysis_data(self, rows: list[dict[str, object]]) -> None:
        self._fill_table(
            self.question_table,
            rows,
            ["question_number", "content", "type", "sub_category", "difficulty", "correct_rate", "wrong_rate", "is_weak"],
        )

    def set_type_analysis_data(self, rows: list[dict[str, object]]) -> None:
        self._fill_table(self.type_table, rows, ["type", "correct_rate", "wrong_rate", "note"])
        weakest = min(rows, key=lambda row: float(row.get("correct_rate", 100)), default={})
        self.type_graph_label.setText(f"그래프 placeholder\n가장 낮은 유형: {weakest.get('type', '-')}")

    def set_sub_category_analysis_data(self, rows: list[dict[str, object]]) -> None:
        self._fill_table(self.sub_category_table, rows, ["sub_category", "correct_rate", "wrong_rate", "note"])
        weakest = min(rows, key=lambda row: float(row.get("correct_rate", 100)), default={})
        self.sub_category_graph_label.setText(f"그래프 placeholder\n취약 세부 분류: {weakest.get('sub_category', '-')}")

    def set_difficulty_analysis_data(self, rows: list[dict[str, object]]) -> None:
        self._fill_table(self.difficulty_table, rows, ["difficulty", "correct_rate", "wrong_rate", "achievement_gap"])
        self.difficulty_graph_label.setText("그래프 placeholder\n난이도별 성취 차이를 표시합니다.")

    def set_weakness_summary(self, data: dict[str, object]) -> None:
        self.weak_type_label.setText(str(data.get("weak_type", "-")))
        self.weak_sub_category_label.setText(str(data.get("weak_sub_category", "-")))
        self.weak_difficulty_label.setText(str(data.get("weak_difficulty", "-")))
        self.guidance_label.setText(str(data.get("guidance", "-")))
        self.feedback_label.setText(str(data.get("feedback", "-")))

    def clear_analysis(self) -> None:
        for value_label in self._summary_value_labels.values():
            value_label.setText("-")
        self.class_average_label.setText("-")
        self.class_correct_rate_label.setText("-")
        self.class_wrong_rate_label.setText("-")
        self.class_interpretation_label.setText("")
        for table in [self.question_table, self.type_table, self.sub_category_table, self.difficulty_table]:
            table.setRowCount(0)
        self.set_weakness_summary({})

    def show_message(self, message: str) -> None:
        QMessageBox.information(self, "안내", message)

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self, "오류", message)

    def _load_sample_data(self) -> None:
        self.set_exam_options(
            [
                {"id": 1, "name": "2024년 1학기 중간고사"},
                {"id": 2, "name": "2024년 1학기 기말고사"},
            ]
        )
        self.set_class_options(
            [
                {"id": "1-1", "name": "1학년 1반"},
                {"id": "1-2", "name": "1학년 2반"},
                {"id": "1-3", "name": "1학년 3반"},
            ]
        )
        self.set_summary_data(
            {
                "student_count": "28명",
                "average_score": "72.35점",
                "correct_rate": "72.45%",
                "wrong_rate": "27.55%",
                "weak_type": "문법",
                "weak_difficulty": "어려움",
                "interpretation": "현재 반은 문법 유형과 어려움 난이도에서 낮은 정답률을 보입니다.",
            }
        )
        self.set_question_analysis_data(
            [
                {"question_number": 1, "content": "빈칸에 들어갈 알맞은 단어", "type": "어휘", "sub_category": "동의어", "difficulty": "쉬움", "correct_rate": "85.1%", "wrong_rate": "14.9%", "is_weak": "아니오"},
                {"question_number": 2, "content": "어법상 틀린 부분 찾기", "type": "문법", "sub_category": "시제", "difficulty": "보통", "correct_rate": "58.3%", "wrong_rate": "41.7%", "is_weak": "예"},
                {"question_number": 3, "content": "글의 주제 찾기", "type": "독해", "sub_category": "주제", "difficulty": "어려움", "correct_rate": "52.0%", "wrong_rate": "48.0%", "is_weak": "예"},
            ]
        )
        self.set_type_analysis_data(
            [
                {"type": "어휘", "correct_rate": 78.1, "wrong_rate": 21.9, "note": "양호"},
                {"type": "문법", "correct_rate": 65.2, "wrong_rate": 34.8, "note": "취약"},
                {"type": "독해", "correct_rate": 74.3, "wrong_rate": 25.7, "note": "보통"},
            ]
        )
        self.set_sub_category_analysis_data(
            [
                {"sub_category": "시제", "correct_rate": 58.3, "wrong_rate": 41.7, "note": "취약"},
                {"sub_category": "관계대명사", "correct_rate": 65.2, "wrong_rate": 34.8, "note": "보완 필요"},
                {"sub_category": "주제 찾기", "correct_rate": 72.6, "wrong_rate": 27.4, "note": "보통"},
            ]
        )
        self.set_difficulty_analysis_data(
            [
                {"difficulty": "쉬움", "correct_rate": 85.1, "wrong_rate": 14.9, "achievement_gap": "기준 이상"},
                {"difficulty": "보통", "correct_rate": 72.4, "wrong_rate": 27.6, "achievement_gap": "보통"},
                {"difficulty": "어려움", "correct_rate": 56.3, "wrong_rate": 43.7, "achievement_gap": "보충 필요"},
            ]
        )
        self.set_weakness_summary(
            {
                "weak_type": "문법",
                "weak_sub_category": "시제",
                "weak_difficulty": "어려움",
                "guidance": "문법 개념 복습과 난이도 높은 문항의 단계별 풀이 지도가 필요합니다.",
                "feedback": "시제 문제를 짧은 문장 단위로 다시 연습한 뒤 독해 지문에 적용해 보세요.",
            }
        )

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
        titles = ["응시 학생 수", "반 전체 평균 점수", "전체 정답률", "전체 오답률", "가장 취약한 문제 유형", "가장 취약한 난이도"]
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

    def _build_class_analysis_card(self) -> QFrame:
        card = self._make_card("반 전체 분석")
        layout = card.layout()
        row = QHBoxLayout()
        self.class_average_label = self._make_metric_inline("반 전체 평균 점수")
        self.class_correct_rate_label = self._make_metric_inline("전체 정답률")
        self.class_wrong_rate_label = self._make_metric_inline("전체 오답률")
        row.addWidget(self.class_average_label)
        row.addWidget(self.class_correct_rate_label)
        row.addWidget(self.class_wrong_rate_label)
        row.addStretch()
        layout.addLayout(row)
        self.class_interpretation_label = QLabel("")
        self.class_interpretation_label.setObjectName("interpretationLabel")
        layout.addWidget(self.class_interpretation_label)
        return card

    def _build_question_analysis_card(self) -> QFrame:
        card = self._make_card("문항별 정답률/오답률 분석")
        layout = card.layout()
        self.question_table = QTableWidget(0, 8)
        self.question_table.setHorizontalHeaderLabels(["문항 번호", "문제 내용", "문제 유형", "세부 분류", "난이도", "정답률", "오답률", "취약 여부"])
        self._setup_table(self.question_table)
        self.question_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.question_table.setColumnWidth(1, 360)
        layout.addWidget(self.question_table)
        return card

    def _build_type_analysis_card(self) -> QFrame:
        card = self._make_card("문제 유형별 정답률 분석")
        layout = card.layout()
        self.type_table = QTableWidget(0, 4)
        self.type_table.setHorizontalHeaderLabels(["유형", "정답률", "오답률", "강조"])
        self._setup_table(self.type_table)
        self.type_graph_label = self._make_graph_placeholder()
        layout.addWidget(self.type_table)
        layout.addWidget(self.type_graph_label)
        return card

    def _build_sub_category_analysis_card(self) -> QFrame:
        card = self._make_card("세부 분류별 정답률 분석")
        layout = card.layout()
        self.sub_category_table = QTableWidget(0, 4)
        self.sub_category_table.setHorizontalHeaderLabels(["세부 분류", "정답률", "오답률", "강조"])
        self._setup_table(self.sub_category_table)
        self.sub_category_graph_label = self._make_graph_placeholder()
        layout.addWidget(self.sub_category_table)
        layout.addWidget(self.sub_category_graph_label)
        return card

    def _build_difficulty_analysis_card(self) -> QFrame:
        card = self._make_card("난이도별 정답률 분석")
        layout = card.layout()
        self.difficulty_table = QTableWidget(0, 4)
        self.difficulty_table.setHorizontalHeaderLabels(["난이도", "정답률", "오답률", "성취 차이"])
        self._setup_table(self.difficulty_table)
        self.difficulty_graph_label = self._make_graph_placeholder()
        layout.addWidget(self.difficulty_table)
        layout.addWidget(self.difficulty_graph_label)
        return card

    def _build_weakness_card(self) -> QFrame:
        card = self._make_card("반 전체 취약 유형 확인")
        layout = card.layout()
        grid = QGridLayout()
        self.weak_type_label = self._make_metric_inline("취약 유형명")
        self.weak_sub_category_label = self._make_metric_inline("취약 세부 분류명")
        self.weak_difficulty_label = self._make_metric_inline("취약 난이도")
        self.guidance_label = QLabel("-")
        self.feedback_label = QLabel("-")
        for label in [self.guidance_label, self.feedback_label]:
            label.setObjectName("weaknessLabel")
            label.setWordWrap(True)
        grid.addWidget(self.weak_type_label, 0, 0)
        grid.addWidget(self.weak_sub_category_label, 0, 1)
        grid.addWidget(self.weak_difficulty_label, 0, 2)
        grid.addWidget(self._make_labeled_widget("보충 지도 필요 문구", self.guidance_label), 1, 0, 1, 3)
        grid.addWidget(self._make_labeled_widget("추천 피드백 문구", self.feedback_label), 2, 0, 1, 3)
        layout.addLayout(grid)
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

    def _get_selected_id(self, ids: list[object], index: int) -> object | None:
        if 0 <= index < len(ids):
            return ids[index]
        return None
