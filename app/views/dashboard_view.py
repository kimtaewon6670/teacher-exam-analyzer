from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class DashboardView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("dashboard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 18)
        layout.setSpacing(16)

        layout.addLayout(self._build_header())
        layout.addLayout(self._build_metrics())
        layout.addLayout(self._build_charts())
        layout.addLayout(self._build_bottom())
        layout.addWidget(self._build_footer())

        self.setStyleSheet(
            """
            #dashboard {
                background: #f4f7fb;
                color: #172033;
                font-family: "Malgun Gothic", "Segoe UI", Arial;
            }
            #pageTitle {
                font-size: 26px;
                font-weight: 800;
                color: #18263a;
            }
            QComboBox, QLineEdit {
                background: white;
                border: 1px solid #d8e0ea;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 28px;
                color: #28384c;
            }
            QPushButton {
                background: white;
                border: 1px solid #d8e0ea;
                border-radius: 6px;
                padding: 7px 12px;
                color: #27384c;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #eef5ff;
            }
            #card {
                background: white;
                border: 1px solid #dfe6ef;
                border-radius: 8px;
            }
            #cardTitle {
                font-size: 15px;
                font-weight: 800;
                color: #172033;
            }
            #smallMuted {
                color: #75849a;
                font-size: 12px;
            }
            #metricValue {
                font-size: 28px;
                font-weight: 800;
                color: #1b293b;
            }
            #metricUnit {
                font-size: 13px;
                color: #53657a;
            }
            #footer {
                color: #63758c;
                font-size: 12px;
            }
            QTableWidget {
                background: white;
                border: 1px solid #dfe6ef;
                border-radius: 6px;
                gridline-color: #e6ecf3;
                color: #233348;
                selection-background-color: #e8f2ff;
            }
            QHeaderView::section {
                background: #f7f9fc;
                color: #2a3a50;
                border: 0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
                padding: 8px;
                font-weight: 700;
            }
            """
        )

    def show_message(self, message: str) -> None:
        QMessageBox.information(self, "안내", message)

    def show_dashboard_student_results(self, rows: list[dict[str, object]]) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("학생별 결과 전체 보기")
        dialog.resize(1100, 720)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 22, 24, 24)
        layout.setSpacing(14)

        title = QLabel("학생별 결과")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels(["순번", "이름", "학번", "정답 수", "오답 수", "점수"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                row.get("row_no", row_index + 1),
                row.get("student_name", ""),
                row.get("student_number", ""),
                row.get("correct_count", 0),
                row.get("wrong_count", 0),
                f"{float(row.get('score', 0) or 0):.2f}",
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_index, column_index, item)
            table.setRowHeight(row_index, 36)
        layout.addWidget(table, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.setStyleSheet(self.styleSheet())
        dialog.exec()

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(14)

        title = QLabel("대시보드")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch()

        exam = QComboBox()
        exam.addItems(["2024년 1학기 중간고사", "2024년 1학기 기말고사"])
        exam.setFixedWidth(230)
        klass = QComboBox()
        klass.addItems(["1학년 1반", "1학년 2반", "1학년 3반"])
        klass.setFixedWidth(160)
        date = QLabel("▣  2024-05-20")
        date.setStyleSheet("color: #40536b; font-weight: 600;")

        header.addWidget(exam)
        header.addWidget(klass)
        header.addWidget(date)
        return header

    def _build_metrics(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        metrics = [
            ("●", "#3d8be8", "응시 학생 수", "28", "명"),
            ("▣", "#35b86b", "총 문항 수", "30", "문항"),
            ("▤", "#8c63d9", "반 평균 점수", "72.35", "점 /100"),
            ("✓", "#18b6bd", "평균 정답 수", "21.74", "개"),
        ]
        for icon, color, label, value, unit in metrics:
            row.addWidget(MetricCard(icon, color, label, value, unit), 1)
        return row

    def _build_charts(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        row.addWidget(
            ChartCard(
                "문항별 결과",
                BarChart(
                    [48, 64, 38, 76, 88, 61, 72, 50, 42, 57, 68, 46, 34, 39, 75,
                     49, 43, 89, 70, 32, 58, 77, 46, 72, 54, 80, 61, 49, 73, 84],
                    "#3d8be8",
                    "문항 번호",
                    "(%)",
                ),
            ),
            1,
        )
        row.addWidget(
            ChartCard(
                "유형별 결과",
                DonutChart(
                    [78.1, 65.2, 74.3],
                    ["어휘", "문법", "독해"],
                    ["#3d8be8", "#43bd6e", "#f59a23"],
                ),
            ),
            1,
        )
        row.addWidget(
            ChartCard(
                "세부 분류별 결과 (상위 5개)",
                HorizontalBarChart(
                    [
                        ("시제", 58.3),
                        ("수동태", 61.4),
                        ("관계대명사", 65.2),
                        ("접속사", 72.6),
                        ("분사/분사구문", 78.9),
                    ],
                    "#8360cc",
                ),
            ),
            1,
        )
        return row

    def _build_bottom(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(
            ChartCard(
                "난이도별 결과",
                DonutChart(
                    [85.1, 72.4, 56.3],
                    ["쉬움", "보통", "어려움"],
                    ["#3d8be8", "#43bd6e", "#f59a23"],
                ),
            ),
            1,
        )
        row.addWidget(StudentResultCard(), 2)
        return row

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setObjectName("footer")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("데이터베이스: local_exam.db"))
        layout.addWidget(QLabel("버전: 1.0.0"))
        layout.addStretch()
        layout.addWidget(QLabel("마지막 백업: 2024-05-20 14:30"))
        ok = QLabel("● 정상")
        ok.setStyleSheet("color: #20b15a; font-weight: 700;")
        layout.addWidget(ok)
        return footer


class MetricCard(QFrame):
    def __init__(self, icon: str, color: str, label: str, value: str, unit: str) -> None:
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(100)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(48, 48)
        icon_label.setStyleSheet(
            f"background: {color}; color: white; border-radius: 24px; font-size: 22px; font-weight: 800;"
        )

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        caption = QLabel(label)
        caption.setObjectName("smallMuted")
        number_row = QHBoxLayout()
        number_row.setSpacing(4)
        number = QLabel(value)
        number.setObjectName("metricValue")
        unit_label = QLabel(unit)
        unit_label.setObjectName("metricUnit")
        number_row.addWidget(number)
        number_row.addWidget(unit_label)
        number_row.addStretch()

        text_layout.addWidget(caption)
        text_layout.addLayout(number_row)
        text_layout.addStretch()
        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)


class ChartCard(QFrame):
    def __init__(self, title: str, chart: QWidget) -> None:
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(250)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        header = QHBoxLayout()
        label = QLabel(title)
        label.setObjectName("cardTitle")
        header.addWidget(label)
        header.addStretch()

        layout.addLayout(header)
        layout.addWidget(chart, 1)


class StudentResultCard(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("학생별 결과")
        title.setObjectName("cardTitle")
        header.addWidget(title)
        header.addStretch()
        export = QPushButton("엑셀 내보내기")
        export.setObjectName("dashboardExportButton")
        export.setStyleSheet("color: #087f3e;")
        header.addWidget(export)
        full_view = QPushButton("전체 보기")
        full_view.setObjectName("dashboardFullViewButton")
        header.addWidget(full_view)
        layout.addLayout(header)

        tools = QHBoxLayout()
        search = QLineEdit()
        search.setPlaceholderText("학생 이름 또는 학번 검색")
        search.setFixedWidth(280)
        tools.addWidget(search)
        tools.addStretch()
        layout.addLayout(tools)

        table = QTableWidget(5, 6)
        table.setHorizontalHeaderLabels(["순번", "이름", "학번", "정답 수", "오답 수", "점수"])
        rows = [
            ["1", "김민수", "2024001", "25", "5", "83.33"],
            ["2", "이서연", "2024002", "22", "8", "73.33"],
            ["3", "박지훈", "2024003", "24", "6", "80.00"],
            ["4", "최유진", "2024004", "18", "12", "60.00"],
            ["5", "정하랑", "2024005", "20", "10", "66.67"],
        ]
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_index, col_index, item)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(table, 1)

        pager = QHBoxLayout()
        pager.addStretch()
        for text in ["‹", "1", "2", "3", "›"]:
            button = QPushButton(text)
            button.setFixedSize(30, 30)
            if text == "1":
                button.setStyleSheet("background: #2f85dc; color: white; border-color: #2f85dc;")
            pager.addWidget(button)
        pager.addStretch()
        layout.addLayout(pager)


class BarChart(QWidget):
    def __init__(self, values: list[int], color: str, x_label: str, y_label: str) -> None:
        super().__init__()
        self.values = values
        self.color = QColor(color)
        self.x_label = x_label
        self.y_label = y_label
        self.setMinimumHeight(190)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(34, 10, -12, -32)
        if not self.values:
            painter.setPen(QColor("#75849a"))
            painter.drawText(rect, Qt.AlignCenter, "표시할 데이터가 없습니다.")
            return

        painter.setPen(QPen(QColor("#dfe6ef"), 1))
        for i in range(5):
            y = rect.bottom() - rect.height() * i / 4
            painter.drawLine(rect.left(), int(y), rect.right(), int(y))
            painter.setPen(QColor("#6b7b90"))
            painter.drawText(0, int(y) - 8, 28, 16, Qt.AlignRight, str(i * 25))
            painter.setPen(QPen(QColor("#dfe6ef"), 1))

        gap = 5
        bar_width = max(3, int((rect.width() - gap * (len(self.values) - 1)) / len(self.values)))
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        for index, value in enumerate(self.values):
            x = rect.left() + index * (bar_width + gap)
            height = rect.height() * value / 100
            painter.drawRoundedRect(x, int(rect.bottom() - height), bar_width, int(height), 2, 2)

        painter.setPen(QColor("#52647a"))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        for label in [1, 5, 10, 15, 20, 25, 30]:
            x = rect.left() + (label - 1) * (bar_width + gap)
            painter.drawText(int(x) - 8, rect.bottom() + 6, 20, 16, Qt.AlignCenter, str(label))
        painter.drawText(rect, Qt.AlignBottom | Qt.AlignHCenter, self.x_label)
        painter.drawText(0, 0, 28, 18, Qt.AlignRight, self.y_label)


class HorizontalBarChart(QWidget):
    def __init__(self, values: list[tuple[str, float]], color: str) -> None:
        super().__init__()
        self.values = values
        self.color = QColor(color)
        self.setMinimumHeight(190)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(90, 8, -44, -24)
        if not self.values:
            painter.setPen(QColor("#75849a"))
            painter.drawText(rect, Qt.AlignCenter, "표시할 데이터가 없습니다.")
            return
        row_height = rect.height() / len(self.values)

        painter.setPen(QPen(QColor("#dfe6ef"), 1))
        for i in range(5):
            x = rect.left() + rect.width() * i / 4
            painter.drawLine(int(x), rect.top(), int(x), rect.bottom())
            painter.setPen(QColor("#6b7b90"))
            painter.drawText(int(x) - 12, rect.bottom() + 4, 24, 16, Qt.AlignCenter, str(i * 25))
            painter.setPen(QPen(QColor("#dfe6ef"), 1))

        painter.setPen(QColor("#33445a"))
        painter.setBrush(self.color)
        for index, (label, value) in enumerate(self.values):
            y = rect.top() + row_height * index + 7
            painter.setPen(QColor("#33445a"))
            painter.drawText(0, int(y), 82, 18, Qt.AlignRight | Qt.AlignVCenter, label)
            painter.setPen(Qt.NoPen)
            width = rect.width() * value / 100
            painter.drawRoundedRect(rect.left(), int(y), int(width), 14, 2, 2)
            painter.setPen(QColor("#33445a"))
            painter.drawText(rect.left() + int(width) + 8, int(y) - 1, 42, 18, Qt.AlignLeft, f"{value:.1f}%")

        painter.drawText(rect.right() - 10, rect.bottom() + 18, 40, 16, Qt.AlignLeft, "(%)")


class DonutChart(QWidget):
    def __init__(self, values: list[float], labels: list[str], colors: list[str]) -> None:
        super().__init__()
        self.values = values
        self.labels = labels
        self.colors = [QColor(color) for color in colors]
        self.setMinimumHeight(190)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.height() - 16, self.width() // 2)
        chart = QRectF(20, 8, side, side)
        total = sum(self.values)
        if total <= 0:
            painter.setPen(QColor("#75849a"))
            painter.drawText(self.rect(), Qt.AlignCenter, "표시할 데이터가 없습니다.")
            return
        start = 90 * 16
        for value, color in zip(self.values, self.colors):
            span = -int(value / total * 360 * 16)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawPie(chart, start, span)
            start += span

        inner = chart.adjusted(side * 0.28, side * 0.28, -side * 0.28, -side * 0.28)
        painter.setBrush(QColor("white"))
        painter.drawEllipse(inner)

        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.setPen(QColor("white"))
        center = chart.center()
        for idx, value in enumerate(self.values):
            angle = 90 - (sum(self.values[:idx]) + value / 2) / total * 360
            radius = side * 0.34
            point = QPointF(
                center.x() + radius * math.cos(math.radians(angle)),
                center.y() - radius * math.sin(math.radians(angle)),
            )
            painter.drawText(QRectF(point.x() - 20, point.y() - 8, 40, 16), Qt.AlignCenter, f"{value:.1f}%")

        legend_x = chart.right() + 26
        legend_y = chart.top() + 34
        painter.setFont(QFont("Malgun Gothic", 9))
        for index, (label, value, color) in enumerate(zip(self.labels, self.values, self.colors)):
            y = legend_y + index * 30
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(legend_x), int(y), 10, 10)
            painter.setPen(QColor("#233348"))
            painter.drawText(int(legend_x + 18), int(y - 4), 58, 18, Qt.AlignLeft, label)
            painter.drawText(int(legend_x + 76), int(y - 4), 54, 18, Qt.AlignRight, f"{value:.1f}%")
