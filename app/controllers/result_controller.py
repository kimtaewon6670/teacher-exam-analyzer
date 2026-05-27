from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.result_input_service import ResultInputService


class ResultController:
    """Connect result-input View events to core validation and grading logic."""

    def __init__(self, view: Any, result_service: ResultInputService | None = None) -> None:
        self.view = view
        self.result_service = result_service or ResultInputService()
        self._students_by_id: dict[Any, dict[str, Any]] = {}
        self._csv_rows: list[dict[str, str]] = []

        self._connect_view_events()
        self._load_initial_data()

    def _connect_view_events(self) -> None:
        if hasattr(self.view, "validate_button"):
            self.view.validate_button.clicked.connect(self.on_validate_clicked)
        if hasattr(self.view, "save_button"):
            self.view.save_button.clicked.connect(self.on_save_clicked)
        if hasattr(self.view, "grade_button"):
            self.view.grade_button.clicked.connect(self.on_grade_clicked)
        if hasattr(self.view, "reset_button"):
            self.view.reset_button.clicked.connect(self.on_reset_clicked)
        if hasattr(self.view, "load_csv_button"):
            self.view.load_csv_button.clicked.connect(self.on_load_csv_clicked)

        if hasattr(self.view, "exam_combo"):
            self.view.exam_combo.currentIndexChanged.connect(self.on_exam_changed)
        if hasattr(self.view, "class_combo"):
            self.view.class_combo.currentIndexChanged.connect(self.on_class_changed)

    def _load_initial_data(self) -> None:
        data = self.result_service.get_initial_view_data()
        self._set_exam_options(data.get("exams", []))
        self._set_class_options(data.get("classes", []))
        self._set_student_options(data.get("students", []))
        self._refresh_exam_context()

    def on_exam_changed(self) -> None:
        self._refresh_exam_context()

    def on_class_changed(self) -> None:
        class_id = self._get_selected_class_id()
        self._set_student_options(self.result_service.get_students_by_class(class_id))

    def on_validate_clicked(self) -> None:
        is_valid, message = self.result_service.validate_input(
            self._get_selected_exam_id(),
            self._get_selected_student_id(),
            self._get_manual_answers(),
        )
        self._show_message(message, is_valid)

    def on_save_clicked(self) -> None:
        result = self.result_service.grade_answers(
            self._get_selected_exam_id(),
            self._get_selected_student_id(),
            self._get_manual_answers(),
            save_result=True,
        )
        self._show_message(result["message"], bool(result.get("success")))

    def on_grade_clicked(self) -> None:
        result = self.result_service.grade_answers(
            self._get_selected_exam_id(),
            self._get_selected_student_id(),
            self._get_manual_answers(),
            save_result=True,
        )
        self._show_message(result["message"], bool(result.get("success")))

    def on_reset_clicked(self) -> None:
        if hasattr(self.view, "clear_form"):
            self.view.clear_form()
        self._csv_rows = []
        self._refresh_exam_context()

    def on_load_csv_clicked(self) -> None:
        file_path = self._get_csv_file_path()
        if not file_path:
            return

        try:
            rows = self.result_service.parse_csv_file(file_path)
        except Exception as exc:
            self._show_message(f"CSV 파일을 읽을 수 없습니다: {exc}", False)
            return

        self._csv_rows = rows
        if hasattr(self.view, "set_csv_file_name"):
            self.view.set_csv_file_name(Path(file_path).name)
        if hasattr(self.view, "set_csv_preview_data"):
            self.view.set_csv_preview_data(rows)

        selected_answers = self._extract_answers_for_selected_student(rows)
        if selected_answers and hasattr(self.view, "set_manual_answers"):
            self.view.set_manual_answers(selected_answers)

        self._show_message(f"CSV {len(rows)}행을 불러왔습니다.", True)

    def _refresh_exam_context(self) -> None:
        exam_id = self._get_selected_exam_id()
        if hasattr(self.view, "set_exam_summary"):
            self.view.set_exam_summary(self.result_service.get_exam_summary(exam_id))
        if hasattr(self.view, "set_answer_items"):
            self.view.set_answer_items(self.result_service.get_question_count(exam_id))

    def _set_exam_options(self, exams: list[dict[str, Any]]) -> None:
        if hasattr(self.view, "set_exam_options"):
            self.view.set_exam_options(exams)

    def _set_class_options(self, classes: list[dict[str, Any]]) -> None:
        if hasattr(self.view, "set_class_options"):
            self.view.set_class_options(classes)

    def _set_student_options(self, students: list[dict[str, Any]]) -> None:
        self._students_by_id = {student.get("id"): student for student in students}
        if hasattr(self.view, "set_student_options"):
            self.view.set_student_options(students)

    def _get_selected_exam_id(self) -> Any:
        if hasattr(self.view, "get_selected_exam_id"):
            return self.view.get_selected_exam_id()
        return None

    def _get_selected_class_id(self) -> Any:
        if hasattr(self.view, "get_selected_class_id"):
            return self.view.get_selected_class_id()
        return None

    def _get_selected_student_id(self) -> Any:
        if hasattr(self.view, "get_selected_student_id"):
            return self.view.get_selected_student_id()
        return None

    def _get_manual_answers(self) -> dict[Any, Any]:
        if hasattr(self.view, "get_manual_answers"):
            return self.view.get_manual_answers()
        return {}

    def _show_message(self, message: str, is_success: bool) -> None:
        if hasattr(self.view, "show_validation_message"):
            self.view.show_validation_message(message, is_success)

    def _get_csv_file_path(self) -> str:
        if hasattr(self.view, "get_csv_file_path"):
            return self.view.get_csv_file_path()

        # TODO: Move file selection into the View when it exposes a file-picker method.
        try:
            from PySide6.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getOpenFileName(
                self.view,
                "CSV 파일 선택",
                "",
                "CSV Files (*.csv);;All Files (*)",
            )
            return file_path
        except Exception:
            self._show_message("CSV 파일 선택 기능을 사용할 수 없습니다.", False)
            return ""

    def _extract_answers_for_selected_student(
        self,
        rows: list[dict[str, str]],
    ) -> dict[int, str]:
        if not rows:
            return {}

        selected_student = self._students_by_id.get(self._get_selected_student_id(), {})
        selected_student_number = str(selected_student.get("student_id", "")).strip()

        target_row = rows[0]
        if selected_student_number:
            for row in rows:
                if str(row.get("student_id", "")).strip() == selected_student_number:
                    target_row = row
                    break

        answers = {}
        for key, value in target_row.items():
            if not key.lower().startswith("q"):
                continue
            try:
                question_number = int(key[1:])
            except ValueError:
                continue
            answers[question_number] = value

        return answers
