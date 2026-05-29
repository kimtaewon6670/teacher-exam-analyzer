from __future__ import annotations

from typing import Any

from app.services.analysis_service import AnalysisService


class AnalysisController:
    """Connect analysis View events to result-analysis Service logic."""

    def __init__(
        self,
        view: Any,
        analysis_service: AnalysisService | None = None,
        attach_dashboard: bool = True,
    ) -> None:
        self.view = view
        self.analysis_service = analysis_service or AnalysisService()
        self._exam_id_by_name: dict[str, Any] = {}
        self._class_id_by_name: dict[str, Any] = {}
        self._last_dashboard_data: dict[str, Any] = {}
        self._dashboard_page = 1
        self._dashboard_page_size = 5

        self._connect_view_events()
        self._load_initial_data()
        self._connect_dashboard_widget_events()
        if attach_dashboard:
            self._attach_dashboard_view_if_available()

    def _connect_view_events(self) -> None:
        if hasattr(self.view, "search_button"):
            self.view.search_button.clicked.connect(self.on_search_clicked)
        if hasattr(self.view, "reset_button"):
            self.view.reset_button.clicked.connect(self.on_reset_clicked)
        if hasattr(self.view, "exam_combo"):
            self.view.exam_combo.currentIndexChanged.connect(lambda *_: self.on_search_clicked())
        if hasattr(self.view, "class_combo"):
            self.view.class_combo.currentIndexChanged.connect(lambda *_: self.on_search_clicked())
        if hasattr(self.view, "date_combo"):
            self.view.date_combo.currentIndexChanged.connect(lambda *_: self.on_search_clicked())

    def _load_initial_data(self) -> None:
        data = self.analysis_service.get_initial_view_data()
        self._exam_id_by_name = {
            str(exam.get("name", "")).strip(): exam.get("id")
            for exam in data.get("exams", [])
        }
        self._class_id_by_name = {
            str(class_item.get("name", "")).strip(): class_item.get("id")
            for class_item in data.get("classes", [])
        }
        if hasattr(self.view, "set_exam_options"):
            self.view.set_exam_options(data.get("exams", []))
        else:
            self._set_combo_options_by_index(0, [exam.get("name", "") for exam in data.get("exams", [])])
        if hasattr(self.view, "set_class_options"):
            self.view.set_class_options(data.get("classes", []))
        else:
            self._set_combo_options_by_index(1, [item.get("name", "") for item in data.get("classes", [])])
        self._refresh_analysis()

    def on_search_clicked(self) -> None:
        self._refresh_analysis()

    def refresh_options(self) -> None:
        self._load_initial_data()

    def on_reset_clicked(self) -> None:
        if hasattr(self.view, "clear_analysis"):
            self.view.clear_analysis()

        data = self.analysis_service.get_initial_view_data()
        if hasattr(self.view, "set_exam_options"):
            self.view.set_exam_options(data.get("exams", []))
        else:
            self._set_combo_options_by_index(0, [exam.get("name", "") for exam in data.get("exams", [])])
        if hasattr(self.view, "set_class_options"):
            self.view.set_class_options(data.get("classes", []))
        else:
            self._set_combo_options_by_index(1, [item.get("name", "") for item in data.get("classes", [])])
        self._refresh_analysis()

    def _refresh_analysis(self) -> None:
        filters = self._get_filter_data()
        analysis = self.analysis_service.analyze(filters)
        dashboard = self.get_dashboard_data(
            filters.get("exam_id"),
            filters.get("class_id"),
            filters.get("exam_date") or filters.get("date"),
        )

        self._set_summary_data(analysis.get("summary", {}))
        self._set_question_analysis_data(analysis.get("question_analysis", []))
        self._set_type_analysis_data(analysis.get("type_analysis", []))
        self._set_sub_category_analysis_data(analysis.get("sub_category_analysis", []))
        self._set_difficulty_analysis_data(analysis.get("difficulty_analysis", []))
        self._set_weakness_summary(analysis.get("weakness_summary", {}))
        self._set_dashboard_data(dashboard)

    def get_dashboard_data(
        self,
        exam_id: Any | None = None,
        class_id: Any | None = None,
        exam_date: Any | None = None,
    ) -> dict[str, Any]:
        filters = self._get_filter_data()
        return self.analysis_service.build_dashboard_data(
            exam_id if exam_id is not None else filters.get("exam_id"),
            class_id if class_id is not None else filters.get("class_id"),
            exam_date if exam_date is not None else filters.get("exam_date") or filters.get("date"),
        )

    def _get_filter_data(self) -> dict[str, Any]:
        if hasattr(self.view, "get_analysis_filter_data"):
            return self.view.get_analysis_filter_data()
        return self._get_dashboard_filter_data_from_widgets()

    def _set_summary_data(self, summary: dict[str, Any]) -> None:
        if hasattr(self.view, "set_summary_data"):
            self.view.set_summary_data(summary)

    def _set_question_analysis_data(self, rows: list[dict[str, Any]]) -> None:
        if hasattr(self.view, "set_question_analysis_data"):
            self.view.set_question_analysis_data(rows)

    def _set_type_analysis_data(self, rows: list[dict[str, Any]]) -> None:
        if hasattr(self.view, "set_type_analysis_data"):
            self.view.set_type_analysis_data(rows)

    def _set_sub_category_analysis_data(self, rows: list[dict[str, Any]]) -> None:
        if hasattr(self.view, "set_sub_category_analysis_data"):
            self.view.set_sub_category_analysis_data(rows)

    def _set_difficulty_analysis_data(self, rows: list[dict[str, Any]]) -> None:
        if hasattr(self.view, "set_difficulty_analysis_data"):
            self.view.set_difficulty_analysis_data(rows)

    def _set_weakness_summary(self, data: dict[str, Any]) -> None:
        if hasattr(self.view, "set_weakness_summary"):
            self.view.set_weakness_summary(data)

    def _set_dashboard_data(self, data: dict[str, Any]) -> None:
        self._last_dashboard_data = data
        if hasattr(self.view, "set_dashboard_data"):
            self.view.set_dashboard_data(data)
        if hasattr(self.view, "set_dashboard_summary"):
            self.view.set_dashboard_summary(data.get("summary", {}))
        if hasattr(self.view, "set_question_accuracy_data"):
            self.view.set_question_accuracy_data(data.get("question_accuracy", []))
        if hasattr(self.view, "set_category_accuracy_data"):
            self.view.set_category_accuracy_data(data.get("category_accuracy", []))
        if hasattr(self.view, "set_subcategory_accuracy_data"):
            self.view.set_subcategory_accuracy_data(data.get("subcategory_accuracy_top5", []))
        if hasattr(self.view, "set_difficulty_accuracy_data"):
            self.view.set_difficulty_accuracy_data(data.get("difficulty_accuracy", []))
        if hasattr(self.view, "set_student_result_data"):
            self.view.set_student_result_data(data.get("student_results", []))
        self._apply_dashboard_data_to_existing_widgets(data)

    def _get_dashboard_filter_data_from_widgets(self) -> dict[str, Any]:
        combos = self._find_children_by_class_name("QComboBox")
        exam_text = self._current_text(combos[0]) if len(combos) > 0 else ""
        class_text = self._current_text(combos[1]) if len(combos) > 1 else ""
        exam_date = self._extract_date_from_view()

        return {
            "exam_id": self._exam_id_by_name.get(exam_text, exam_text),
            "class_id": self._class_id_by_name.get(class_text, class_text),
            "exam_date": exam_date,
        }

    def _set_combo_options_by_index(self, index: int, labels: list[Any]) -> None:
        combos = self._find_children_by_class_name("QComboBox")
        if len(combos) <= index or not labels:
            return

        combo = combos[index]
        current = self._current_text(combo)
        try:
            combo.blockSignals(True)
            combo.clear()
            combo.addItems([str(label) for label in labels if str(label)])
            if current:
                found_index = combo.findText(current)
                if found_index >= 0:
                    combo.setCurrentIndex(found_index)
        finally:
            try:
                combo.blockSignals(False)
            except Exception:
                pass

    def _apply_dashboard_data_to_existing_widgets(self, data: dict[str, Any]) -> None:
        self._apply_metric_cards(data.get("metrics", []))
        self._apply_dashboard_charts(data.get("charts", {}))
        self._apply_student_table(data.get("student_results", []))

    def _attach_dashboard_view_if_available(self) -> None:
        dashboard_views = self._find_children_by_class_name_from_root("DashboardView")
        for dashboard_view in dashboard_views:
            if dashboard_view is self.view or hasattr(dashboard_view, "_dashboard_controller"):
                continue
            try:
                from app.controllers.dashboard_controller import DashboardController

                dashboard_view._dashboard_controller = DashboardController(
                    dashboard_view,
                    self.analysis_service,
                )
            except Exception:
                continue

    def _connect_dashboard_widget_events(self) -> None:
        if getattr(self.view, "_dashboard_events_connected", False):
            return
        if self.view.__class__.__name__ != "DashboardView":
            return

        self.view._dashboard_events_connected = True
        for combo in self._find_children_by_class_name("QComboBox"):
            try:
                combo.currentIndexChanged.connect(lambda *_: self.on_search_clicked())
            except Exception:
                pass

        for button in self._find_children_by_class_name("QPushButton"):
            text = str(button.text() if hasattr(button, "text") else "").strip()
            try:
                if text == "엑셀 내보내기":
                    button.clicked.connect(self.export_dashboard_student_results)
                elif text == "전체 보기":
                    button.clicked.connect(self.show_all_dashboard_results)
                elif text in {"‹", "<"}:
                    button.clicked.connect(lambda *_: self.move_dashboard_page(-1))
                elif text in {"›", ">"}:
                    button.clicked.connect(lambda *_: self.move_dashboard_page(1))
                elif text.isdigit():
                    page = int(text)
                    button.clicked.connect(lambda *_args, page=page: self.set_dashboard_page(page))
            except Exception:
                continue

        for line_edit in self._find_children_by_class_name("QLineEdit"):
            try:
                line_edit.textChanged.connect(lambda *_: self.set_dashboard_page(1))
            except Exception:
                pass

    def show_all_dashboard_results(self) -> None:
        self._clear_dashboard_search()
        self._dashboard_page = 1
        self._set_dashboard_data(self.get_dashboard_data())

    def set_dashboard_page(self, page: int) -> None:
        self._dashboard_page = max(int(page or 1), 1)
        self._apply_student_table(self._last_dashboard_data.get("student_results", []))

    def move_dashboard_page(self, delta: int) -> None:
        self.set_dashboard_page(self._dashboard_page + delta)

    def export_dashboard_student_results(self) -> dict[str, Any]:
        rows = self._last_dashboard_data.get("student_results", [])
        if not rows:
            result = {"success": False, "message": "내보낼 학생별 결과가 없습니다."}
            self._show_dashboard_message(result["message"])
            return result

        from csv import DictWriter
        from pathlib import Path

        export_dir = Path("data")
        export_dir.mkdir(exist_ok=True)
        file_path = export_dir / "dashboard_student_results.csv"
        fieldnames = [
            "row_no",
            "student_id",
            "student_name",
            "student_number",
            "correct_count",
            "wrong_count",
            "score",
            "accuracy",
        ]
        with file_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
            writer = DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key, "") for key in fieldnames})

        result = {
            "success": True,
            "message": "학생별 결과를 내보냈습니다.",
            "file_path": str(file_path),
        }
        self._show_dashboard_message(f"{result['message']} ({file_path})")
        return result

    def _apply_metric_cards(self, metrics: list[dict[str, Any]]) -> None:
        values = self._find_children_by_object_name("metricValue")
        units = self._find_children_by_object_name("metricUnit")
        labels = self._find_children_by_object_name("smallMuted")

        for index, metric in enumerate(metrics):
            if index < len(labels):
                self._set_text(labels[index], metric.get("label", ""))
            if index < len(values):
                self._set_text(values[index], metric.get("value", "0"))
            if index < len(units):
                self._set_text(units[index], metric.get("unit", ""))

    def _apply_dashboard_charts(self, charts: dict[str, Any]) -> None:
        bar_charts = self._find_children_by_class_name("BarChart")
        horizontal_charts = self._find_children_by_class_name("HorizontalBarChart")
        donut_charts = self._find_children_by_class_name("DonutChart")

        if bar_charts:
            self._set_chart_attrs(
                bar_charts[0],
                values=charts.get("question_values", []),
            )
        if donut_charts:
            self._set_chart_attrs(
                donut_charts[0],
                values=charts.get("category_values", []),
                labels=charts.get("category_labels", []),
                colors=charts.get("donut_colors", [])[: len(charts.get("category_values", []))],
            )
        if horizontal_charts:
            self._set_chart_attrs(
                horizontal_charts[0],
                values=charts.get("subcategory_values", []),
            )
        if len(donut_charts) > 1:
            self._set_chart_attrs(
                donut_charts[1],
                values=charts.get("difficulty_values", []),
                labels=charts.get("difficulty_labels", []),
                colors=charts.get("donut_colors", [])[: len(charts.get("difficulty_values", []))],
            )

    def _apply_student_table(self, rows: list[dict[str, Any]]) -> None:
        tables = self._find_children_by_class_name("QTableWidget")
        if not tables:
            return

        table = tables[0]
        try:
            from PySide6.QtCore import Qt
            from PySide6.QtWidgets import QTableWidgetItem
        except Exception:
            return

        filtered_rows = self._filter_dashboard_rows(rows)
        page_rows, page_count = self._get_dashboard_page_rows(filtered_rows)
        table_rows = [
            [
                row.get("row_no", index),
                row.get("student_name", ""),
                row.get("student_number", ""),
                row.get("correct_count", 0),
                row.get("wrong_count", 0),
                f"{float(row.get('score', 0) or 0):.2f}",
                f"{float(row.get('accuracy', 0) or 0):.2f}%",
            ]
            for index, row in enumerate(page_rows, start=1)
        ]

        table.setRowCount(len(table_rows))
        for row_index, row_values in enumerate(table_rows):
            for column_index, value in enumerate(row_values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_index, column_index, item)
        self._update_dashboard_page_buttons(page_count)

    def _filter_dashboard_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        keyword = self._get_dashboard_search_text()
        if not keyword:
            return list(rows)

        return [
            row
            for row in rows
            if keyword in str(row.get("student_name", "")).lower()
            or keyword in str(row.get("student_number", "")).lower()
        ]

    def _get_dashboard_page_rows(self, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
        page_size = max(int(self._dashboard_page_size or 5), 1)
        page_count = max(((len(rows) - 1) // page_size) + 1, 1)
        self._dashboard_page = min(max(int(self._dashboard_page or 1), 1), page_count)
        start = (self._dashboard_page - 1) * page_size
        return rows[start:start + page_size], page_count

    def _get_dashboard_search_text(self) -> str:
        line_edits = self._find_children_by_class_name("QLineEdit")
        if not line_edits:
            return ""
        try:
            return str(line_edits[0].text()).strip().lower()
        except Exception:
            return ""

    def _clear_dashboard_search(self) -> None:
        for line_edit in self._find_children_by_class_name("QLineEdit"):
            try:
                line_edit.clear()
            except Exception:
                pass

    def _update_dashboard_page_buttons(self, page_count: int) -> None:
        prev_text = "\u2039"
        next_text = "\u203a"
        for button in self._find_children_by_class_name("QPushButton"):
            text = str(button.text() if hasattr(button, "text") else "").strip()
            try:
                if text in {prev_text, "<"}:
                    button.setEnabled(self._dashboard_page > 1)
                elif text in {next_text, ">"}:
                    button.setEnabled(self._dashboard_page < page_count)
                elif text.isdigit():
                    page = int(text)
                    button.setEnabled(page <= page_count)
                    if hasattr(button, "setChecked"):
                        button.setChecked(page == self._dashboard_page)
            except Exception:
                continue

    def _show_dashboard_message(self, message: str) -> None:
        for method_name in ("show_message", "show_validation_message", "set_status_message"):
            method = getattr(self.view, method_name, None)
            if callable(method):
                try:
                    method(message)
                    return
                except Exception:
                    continue

    def _set_chart_attrs(self, chart: Any, **attrs: Any) -> None:
        for key, value in attrs.items():
            if value is not None:
                setattr(chart, key, value)
        if hasattr(chart, "update"):
            chart.update()

    def _find_children_by_class_name(self, class_name: str) -> list[Any]:
        if not hasattr(self.view, "findChildren"):
            return []
        try:
            from PySide6.QtCore import QObject

            return [
                child
                for child in self.view.findChildren(QObject)
                if child.__class__.__name__ == class_name
            ]
        except Exception:
            return []

    def _find_children_by_object_name(self, object_name: str) -> list[Any]:
        if not hasattr(self.view, "findChildren"):
            return []
        try:
            from PySide6.QtCore import QObject

            return [
                child
                for child in self.view.findChildren(QObject)
                if hasattr(child, "objectName") and child.objectName() == object_name
            ]
        except Exception:
            return []

    def _find_children_by_class_name_from_root(self, class_name: str) -> list[Any]:
        root = self.view
        try:
            if hasattr(self.view, "window"):
                root = self.view.window()
        except Exception:
            root = self.view

        if not hasattr(root, "findChildren"):
            return []
        try:
            from PySide6.QtCore import QObject

            return [
                child
                for child in root.findChildren(QObject)
                if child.__class__.__name__ == class_name
            ]
        except Exception:
            return []

    def _current_text(self, combo: Any) -> str:
        if hasattr(combo, "currentText"):
            return str(combo.currentText()).strip()
        return ""

    def _set_text(self, widget: Any, value: Any) -> None:
        if hasattr(widget, "setText"):
            widget.setText(str(value))

    def _extract_date_from_view(self) -> str:
        import re

        if hasattr(self.view, "get_selected_exam_date"):
            return str(self.view.get_selected_exam_date() or "").strip()

        for label in self._find_children_by_class_name("QLabel"):
            text = str(label.text() if hasattr(label, "text") else "")
            match = re.search(r"\d{4}-\d{2}-\d{2}", text)
            if match:
                return match.group(0)
        return ""
