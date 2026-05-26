from __future__ import annotations

from typing import Any

from app.models.exam_model import Exam
from app.models.exam_question_model import ExamQuestion
from app.repositories.exam_question_repository import ExamQuestionRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository


class ExamController:
    def __init__(self, view: Any, builder_service: Any, pdf_service: Any) -> None:
        self.view = view
        self.builder_service = builder_service
        self.pdf_service = pdf_service
        self.current_questions: list[Any] = []
        self.selected_questions: list[dict[str, object]] = []
        self.cart_items: list[dict[str, Any]] = []
        self.saved_exam_id: int | None = None

        self._connect_view_events()
        self._load_filter_options()

    def _connect_view_events(self) -> None:
        if hasattr(self.view, "auto_extract_requested"):
            self.view.auto_extract_requested.connect(self.auto_extract_questions)
        if hasattr(self.view, "manual_select_requested"):
            self.view.manual_select_requested.connect(self.manual_select_questions)
        if hasattr(self.view, "selection_clear_requested"):
            self.view.selection_clear_requested.connect(self.clear_selection)
        if hasattr(self.view, "question_exclude_requested"):
            self.view.question_exclude_requested.connect(self.exclude_question)
        if hasattr(self.view, "save_exam_requested"):
            self.view.save_exam_requested.connect(self.save_exam)
        if hasattr(self.view, "pdf_export_requested"):
            self.view.pdf_export_requested.connect(self.export_pdf)
        if hasattr(self.view, "preview_requested"):
            self.view.preview_requested.connect(self.preview_exam)

        if hasattr(self.view, "generate_button"):
            self.view.generate_button.clicked.connect(self.on_generate_clicked)
        if hasattr(self.view, "export_button"):
            self.view.export_button.clicked.connect(self.on_export_clicked)
        if hasattr(self.view, "add_cart_button"):
            self.view.add_cart_button.clicked.connect(self.on_add_cart_clicked)
        if hasattr(self.view, "remove_cart_button"):
            self.view.remove_cart_button.clicked.connect(self.on_remove_cart_clicked)
        if hasattr(self.view, "clear_cart_button"):
            self.view.clear_cart_button.clicked.connect(self.on_clear_cart_clicked)

    def _load_filter_options(self) -> None:
        if not hasattr(self.view, "set_filter_options"):
            return

        questions = QuestionRepository.read_all(active_only=True)
        self.view.set_filter_options(
            {
                "question_types": sorted({question.category for question in questions if question.category}),
                "sub_categories": sorted({question.sub_category for question in questions if question.sub_category}),
                "tags": sorted(
                    {
                        tag.strip()
                        for question in questions
                        for tag in (question.tags or "").split(",")
                        if tag.strip()
                    }
                ),
                "classes": sorted({question.class_name for question in questions if question.class_name})
                or ["1학년 1반", "1학년 2반", "1학년 3반"],
            }
        )

    def auto_extract_questions(self) -> None:
        criteria = self._build_service_criteria()
        if criteria["total_count"] <= 0:
            self._show_error("추출할 문항 수를 입력해주세요.")
            return

        self.current_questions = self.builder_service.create_random_exam(criteria)
        self.selected_questions = [self._to_view_question(question) for question in self.current_questions]
        self.view.set_selected_questions(self.selected_questions)

        if hasattr(self.view, "set_build_summary_data"):
            self.view.set_build_summary_data(self.builder_service.get_last_build_summary())
        if not self.selected_questions:
            self._show_message("조건에 맞는 문제가 없습니다.")

    def manual_select_questions(self) -> None:
        questions = [self._to_view_question(question) for question in QuestionRepository.read_all(active_only=True)]
        selected_questions = self.view.select_questions_from_list(questions)
        if not selected_questions:
            return

        existing_ids = set(self.view.get_selected_question_ids())
        for question in selected_questions:
            if question.get("question_id") not in existing_ids:
                self.selected_questions.append(question)
                existing_ids.add(question.get("question_id"))

        self.view.set_selected_questions(self.selected_questions)

    def clear_selection(self) -> None:
        self.selected_questions = []
        self.current_questions = []
        self.saved_exam_id = None

    def exclude_question(self, question_id: object) -> None:
        self.selected_questions = [
            question for question in self.selected_questions if question.get("question_id") != question_id
        ]
        self.current_questions = [
            question for question in self.current_questions if getattr(question, "question_id", None) != question_id
        ]

    def save_exam(self) -> None:
        exam_data = self.view.get_exam_form_data()
        question_ids = self.view.get_selected_question_ids()
        if not exam_data.get("exam_name"):
            self._show_error("시험명을 입력해주세요.")
            return
        if not question_ids:
            self._show_error("시험지에 포함할 문제를 선택해주세요.")
            return

        exam = Exam(
            exam_name=exam_data["exam_name"],
            description=exam_data.get("description"),
            exam_date=exam_data.get("exam_date"),
            target_class=exam_data["class_name"],
            total_questions=len(question_ids),
        )
        exam_id = ExamRepository.create(exam)
        for order, question_id in enumerate(question_ids, start=1):
            ExamQuestionRepository.create(
                ExamQuestion(exam_id=exam_id, question_id=int(question_id), question_order=order)
            )

        self.saved_exam_id = exam_id
        self.selected_questions = list(self.view.selected_questions)
        self.view.set_selected_questions(self.selected_questions)
        self._show_message("시험지가 저장되었습니다.")

    def export_pdf(self) -> None:
        questions = list(getattr(self.view, "selected_questions", []))
        if not questions:
            self._show_error("PDF로 출력할 문제가 없습니다.")
            return

        save_path = self.view.get_pdf_save_path()
        if not save_path:
            return
        if not save_path.lower().endswith(".pdf"):
            save_path = f"{save_path}.pdf"

        success, message = self.pdf_service.export_exam_pdf(save_path, self.view.get_exam_form_data(), questions)
        self._show_export_result(success, message)

    def preview_exam(self) -> None:
        count = len(self.view.get_selected_question_ids())
        self._show_message(f"선택된 문제 {count}문항으로 시험지를 구성합니다.")

    def on_add_cart_clicked(self) -> None:
        if hasattr(self.view, "get_exam_cart_item_data"):
            raw_item = self.view.get_exam_cart_item_data()
        else:
            raw_item = self.view.get_exam_criteria()

        items = self.builder_service.normalize_cart_items([raw_item])
        if not items:
            return

        self.cart_items.extend(item.to_dict() for item in items)
        self._set_cart_data()

        if hasattr(self.view, "clear_exam_cart_item"):
            self.view.clear_exam_cart_item()

    def on_remove_cart_clicked(self) -> None:
        selected_index = self._get_selected_cart_index()
        if selected_index is None:
            return

        if 0 <= selected_index < len(self.cart_items):
            self.cart_items.pop(selected_index)
            self._set_cart_data()

    def on_clear_cart_clicked(self) -> None:
        self.cart_items.clear()
        if hasattr(self.view, "clear_cart"):
            self.view.clear_cart()
        else:
            self._set_cart_data()

    def on_generate_clicked(self) -> None:
        criteria = self.view.get_exam_criteria()
        criteria["cart_items"] = self._get_cart_items()

        self.current_questions = self.builder_service.create_random_exam(criteria)
        if hasattr(self.view, "set_preview_data"):
            self.view.set_preview_data(self.current_questions)

        if hasattr(self.view, "set_build_summary_data"):
            self.view.set_build_summary_data(self.builder_service.get_last_build_summary())

    def on_export_clicked(self) -> None:
        if not self.current_questions:
            return

        save_path = self.view.get_save_path()
        if not save_path:
            return
        if not save_path.lower().endswith(".pdf"):
            save_path = f"{save_path}.pdf"

        exam_info = self.view.get_exam_criteria()
        success, message = self.pdf_service.export_exam_pdf(save_path, exam_info, self.current_questions)
        self._show_export_result(success, message)

    def _build_service_criteria(self) -> dict[str, Any]:
        condition_data = self.view.get_exam_condition_data()
        exam_data = self.view.get_exam_form_data()
        return {
            "category_counts": {
                "어휘": int(condition_data["type_counts"].get("vocabulary", 0)),
                "문법": int(condition_data["type_counts"].get("grammar", 0)),
                "독해": int(condition_data["type_counts"].get("reading", 0)),
            },
            "difficulty_counts": {
                "쉬움": int(condition_data["difficulty_counts"].get("easy", 0)),
                "보통": int(condition_data["difficulty_counts"].get("normal", 0)),
                "어려움": int(condition_data["difficulty_counts"].get("hard", 0)),
            },
            "sub_category": self._normalize_filter_value(str(condition_data.get("sub_category", "")), "전체 분류"),
            "tag": self._normalize_filter_value(str(condition_data.get("tag", "")), "전체 태그"),
            "class_name": exam_data.get("class_name", ""),
            "exam_name": exam_data.get("exam_name", ""),
            "total_count": int(condition_data.get("total_count", 0)),
        }

    def _get_cart_items(self) -> list[dict[str, Any]]:
        if hasattr(self.view, "get_exam_cart_data"):
            raw_items = self.view.get_exam_cart_data()
            if raw_items:
                return [item.to_dict() if hasattr(item, "to_dict") else item for item in raw_items]

        return list(self.cart_items)

    def _set_cart_data(self) -> None:
        if hasattr(self.view, "set_cart_data"):
            self.view.set_cart_data(self.cart_items)

    def _get_selected_cart_index(self) -> int | None:
        if hasattr(self.view, "get_selected_cart_index"):
            return self.view.get_selected_cart_index()
        if hasattr(self.view, "get_selected_cart_item_index"):
            return self.view.get_selected_cart_item_index()
        return None

    def _normalize_filter_value(self, value: str, empty_label: str) -> str:
        return "" if value == empty_label else value

    def _to_view_question(self, question: Any) -> dict[str, object]:
        return {
            "question_id": question.question_id,
            "content": question.question_text,
            "type": question.category,
            "sub_category": question.sub_category or "",
            "difficulty": question.difficulty,
            "answer": question.answer_text,
            "tags": question.tags or "",
        }

    def _show_message(self, message: str) -> None:
        if hasattr(self.view, "show_message"):
            self.view.show_message(message)

    def _show_error(self, message: str) -> None:
        if hasattr(self.view, "show_error"):
            self.view.show_error(message)
        elif hasattr(self.view, "show_message"):
            self.view.show_message(message)

    def _show_export_result(self, success: bool, message: str) -> None:
        if hasattr(self.view, "show_export_result"):
            self.view.show_export_result(success, message)
        elif success:
            self._show_message(message)
        else:
            self._show_error(message)
