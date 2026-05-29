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
        if hasattr(self.view, "basis_combo"):
            self.view.basis_combo.currentIndexChanged.connect(lambda *_: self.on_search_clicked())

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

        self._set_summary_data(analysis.get("summary", {}))
        self._set_question_analysis_data(analysis.get("question_analysis", []))
        self._set_type_analysis_data(analysis.get("type_analysis", []))
        self._set_sub_category_analysis_data(analysis.get("sub_category_analysis", []))
        self._set_difficulty_analysis_data(analysis.get("difficulty_analysis", []))
        self._set_weakness_summary(analysis.get("weakness_summary", {}))

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
