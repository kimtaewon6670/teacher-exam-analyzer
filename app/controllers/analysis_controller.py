from __future__ import annotations

from typing import Any

from app.services.analysis_service import AnalysisService


class AnalysisController:
    """Connect analysis View events to result-analysis Service logic."""

    def __init__(self, view: Any, analysis_service: AnalysisService | None = None) -> None:
        self.view = view
        self.analysis_service = analysis_service or AnalysisService()

        self._connect_view_events()
        self._load_initial_data()

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
        if hasattr(self.view, "set_exam_options"):
            self.view.set_exam_options(data.get("exams", []))
        if hasattr(self.view, "set_class_options"):
            self.view.set_class_options(data.get("classes", []))
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
        if hasattr(self.view, "set_class_options"):
            self.view.set_class_options(data.get("classes", []))
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
        return {}

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
