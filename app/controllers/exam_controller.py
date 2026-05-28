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
        self.current_questions: list[dict[str, Any]] = []
        self.selected_questions: list[dict[str, Any]] = []
        self.auto_extracted_questions: list[dict[str, Any]] = []
        self.manual_selected_questions: list[dict[str, Any]] = []
        self.saved_exam_id: int | None = None

        self._connect_view_events()
        self._initialize_filter_options()
        self._refresh_generated_exams()

    def _connect_view_events(self) -> None:
        if hasattr(self.view, "auto_extract_requested"):
            self.view.auto_extract_requested.connect(self.auto_extract_questions)
        if hasattr(self.view, "manual_select_requested"):
            self.view.manual_select_requested.connect(self.manual_select_questions)
        if hasattr(self.view, "selection_clear_requested"):
            self.view.selection_clear_requested.connect(self.clear_manual_selected_questions)
        if hasattr(self.view, "auto_selection_clear_requested"):
            self.view.auto_selection_clear_requested.connect(self.clear_auto_extracted_questions)
        if hasattr(self.view, "manual_selection_clear_requested"):
            self.view.manual_selection_clear_requested.connect(self.clear_manual_selected_questions)
        if hasattr(self.view, "question_exclude_requested"):
            self.view.question_exclude_requested.connect(self.exclude_question)
        if hasattr(self.view, "auto_question_exclude_requested"):
            self.view.auto_question_exclude_requested.connect(self.exclude_auto_question)
        if hasattr(self.view, "manual_question_exclude_requested"):
            self.view.manual_question_exclude_requested.connect(self.exclude_manual_question)
        if hasattr(self.view, "save_exam_requested"):
            self.view.save_exam_requested.connect(self.save_exam)
        if hasattr(self.view, "pdf_export_requested"):
            self.view.pdf_export_requested.connect(self.export_pdf)
        if hasattr(self.view, "preview_requested"):
            self.view.preview_requested.connect(self.preview_exam)
        if hasattr(self.view, "exam_delete_requested"):
            self.view.exam_delete_requested.connect(self.delete_exam)

        for button_name in ("auto_clear_button", "clear_auto_button", "auto_selection_clear_button"):
            button = getattr(self.view, button_name, None)
            if button is not None and hasattr(button, "clicked"):
                button.clicked.connect(self.clear_auto_extracted_questions)

        for button_name in ("manual_clear_button", "clear_manual_button", "manual_selection_clear_button"):
            button = getattr(self.view, button_name, None)
            if button is not None and hasattr(button, "clicked"):
                button.clicked.connect(self.clear_manual_selected_questions)

        for button_name in ("preview_button", "exam_preview_button", "preview_exam_button", "preview_btn"):
            button = getattr(self.view, button_name, None)
            if button is not None and hasattr(button, "clicked"):
                button.clicked.connect(self.preview_exam)

        self._connect_count_limit_events()

    def _initialize_filter_options(self) -> None:
        if not hasattr(self.view, "set_filter_options"):
            return

        filter_options = (
            self.builder_service.get_filter_options()
            if hasattr(self.builder_service, "get_filter_options")
            else {}
        )
        questions = QuestionRepository.read_all(active_only=True)

        filter_options = {
            **filter_options,
            "question_types": sorted({question.category for question in questions if question.category})
            or filter_options.get("question_types", ["어휘", "문법", "독해"]),
            "sub_categories": self._with_all_option(
                "전체 분류",
                sorted({question.sub_category for question in questions if question.sub_category})
                or filter_options.get("sub_categories", []),
            ),
            "tags": self._with_all_option(
                "전체 태그",
                sorted(
                    {
                        tag.strip()
                        for question in questions
                        for tag in (question.tags or "").split(",")
                        if tag.strip()
                    }
                )
                or filter_options.get("tags", []),
            ),
            "classes": sorted({question.class_name for question in questions if question.class_name})
            or filter_options.get("classes", ["1학년 1반", "1학년 2반", "1학년 3반"]),
        }
        self.view.set_filter_options(filter_options)

    def auto_extract_questions(self) -> None:
        criteria = self._build_service_criteria()
        requested_count = self._get_requested_auto_count(criteria)
        if requested_count <= 0:
            self._show_error("추출할 문항 수를 입력해주세요.")
            return

        if self._to_count(criteria.get("total_count")) <= 0:
            criteria["total_count"] = requested_count
        criteria["selected_question_ids"] = self._get_manual_question_ids()
        criteria["selected_questions"] = []

        if hasattr(self.builder_service, "validate_exam_request"):
            is_valid, message = self.builder_service.validate_exam_request(criteria)
            if not is_valid:
                self._show_error(message)
                self._update_count_limit()
                return

        self._set_auto_extracted_questions(self.builder_service.create_random_exam(criteria))

        if hasattr(self.view, "set_build_summary_data"):
            self.view.set_build_summary_data(self.builder_service.get_last_build_summary())
        if not self.auto_extracted_questions:
            self._show_message("조건에 맞는 문제가 없습니다.")

    def manual_select_questions(self) -> None:
        questions = [self._to_view_question(question) for question in QuestionRepository.read_all(active_only=True)]
        selected_questions = self.view.select_questions_from_list(questions)
        if not selected_questions:
            return

        self._set_manual_selected_questions(
            self._merge_selected_questions(self.manual_selected_questions, selected_questions)
        )

    def clear_selection(self) -> None:
        self._clear_selected_questions()
        self.saved_exam_id = None

    def clear_auto_extracted_questions(self) -> None:
        self.auto_extracted_questions = []
        self._sync_selected_questions_to_view()

    def clear_manual_selected_questions(self) -> None:
        self.manual_selected_questions = []
        self._sync_selected_questions_to_view()

    def exclude_question(self, question_id: object) -> None:
        excluded_id = self._normalize_question_id(question_id)
        if excluded_id is None:
            return
        self._remove_question_from_group("auto", excluded_id)
        self._remove_question_from_group("manual", excluded_id)
        self._sync_selected_questions_to_view()

    def exclude_auto_question(self, question_id: object) -> None:
        excluded_id = self._normalize_question_id(question_id)
        if excluded_id is None:
            return
        self._remove_question_from_group("auto", excluded_id)
        self._sync_selected_questions_to_view()

    def exclude_manual_question(self, question_id: object) -> None:
        excluded_id = self._normalize_question_id(question_id)
        if excluded_id is None:
            return
        self._remove_question_from_group("manual", excluded_id)
        self._sync_selected_questions_to_view()

    def save_exam(self) -> None:
        exam_data = self.view.get_exam_form_data()
        question_ids = self._get_selected_question_ids()
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
        self._sync_selected_questions_to_view()
        self._refresh_generated_exams()
        self._show_message("시험지가 저장되었습니다.")

    def delete_exam(self, exam_id: object) -> None:
        target_exam_id = self._normalize_question_id(exam_id)
        if target_exam_id is None:
            self._show_error("삭제할 시험지 정보를 찾을 수 없습니다.")
            return

        try:
            deleted = ExamRepository.delete(target_exam_id)
        except Exception as exc:
            self._show_error(f"시험지 삭제 중 오류가 발생했습니다: {exc}")
            return

        self._refresh_generated_exams()
        if deleted:
            self._show_message("시험지가 삭제되었습니다.")
        else:
            self._show_error("삭제할 시험지를 찾을 수 없습니다.")

    def export_pdf(self) -> None:
        questions = self._get_exam_paper_questions(self._get_selected_view_questions())
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

    def on_manual_select_clicked(self) -> None:
        self.manual_select_questions()

    def on_clear_selection_clicked(self) -> None:
        self.clear_manual_selected_questions()

    def on_question_exclude_requested(self, question_id: Any) -> None:
        self.exclude_question(question_id)

    def preview_exam(self) -> None:
        questions = self._get_selected_view_questions()
        if not questions:
            self._show_error("미리보기할 문제가 없습니다.")
            return

        self._show_exam_preview(questions)

    def on_preview_clicked(self) -> None:
        self.preview_exam()

    def _build_service_criteria(self) -> dict[str, Any]:
        condition_data = self.view.get_exam_condition_data()
        type_counts = condition_data.get("type_counts", {})
        difficulty_counts = condition_data.get("difficulty_counts", {})
        return {
            "category_counts": {
                "어휘": self._to_count(type_counts.get("vocabulary", 0)),
                "문법": self._to_count(type_counts.get("grammar", 0)),
                "독해": self._to_count(type_counts.get("reading", 0)),
            },
            "difficulty_counts": {
                "쉬움": self._to_count(difficulty_counts.get("easy", 0)),
                "보통": self._to_count(difficulty_counts.get("normal", 0)),
                "어려움": self._to_count(difficulty_counts.get("hard", 0)),
            },
            "cart_items": condition_data.get("cart_items", []),
            "category": condition_data.get("category") or condition_data.get("type") or condition_data.get("question_type", ""),
            "difficulty": condition_data.get("difficulty", ""),
            "sub_category": self._normalize_filter_value(str(condition_data.get("sub_category", "")), "전체 분류"),
            "tag": self._normalize_filter_value(str(condition_data.get("tag", "")), "전체 태그"),
            "total_count": self._to_count(condition_data.get("total_count", 0)),
        }

    def _get_requested_auto_count(self, criteria: dict[str, Any]) -> int:
        total_count = self._to_count(criteria.get("total_count", criteria.get("count", 0)))
        if total_count:
            return total_count

        cart_count = 0
        for item in criteria.get("cart_items", []) or []:
            if not isinstance(item, dict):
                continue
            item_total = self._to_count(item.get("total_count", item.get("count", item.get("total", 0))))
            if item_total:
                cart_count += item_total
                continue
            difficulty_counts = item.get("difficulty_counts", {})
            if isinstance(difficulty_counts, dict):
                cart_count += sum(self._to_count(count) for count in difficulty_counts.values())
        if cart_count:
            return cart_count

        category_count = sum(self._to_count(count) for count in criteria.get("category_counts", {}).values())
        difficulty_count = sum(self._to_count(count) for count in criteria.get("difficulty_counts", {}).values())
        return max(category_count, difficulty_count)

    def _to_count(self, value: Any) -> int:
        if value in (None, ""):
            return 0
        try:
            return max(int(value), 0)
        except (TypeError, ValueError):
            return 0

    def _refresh_generated_exams(self) -> None:
        if not hasattr(self.view, "set_generated_exams"):
            return

        try:
            exams = ExamRepository.read_all()
        except Exception:
            exams = []

        self.view.set_generated_exams(
            [
                {
                    "exam_id": exam.exam_id,
                    "exam_name": exam.exam_name,
                    "class_name": exam.target_class,
                    "exam_date": exam.exam_date or "",
                    "question_count": exam.total_questions,
                    "status": "저장됨",
                }
                for exam in exams
                if exam.exam_id is not None
            ]
        )

    def _with_all_option(self, all_label: str, values: list[str]) -> list[str]:
        deduped_values = [value for value in values if value and value != all_label]
        return [all_label] + deduped_values

    def _normalize_filter_value(self, value: str, empty_label: str) -> str:
        return "" if value == empty_label else value

    def _get_exam_criteria(self) -> dict[str, Any]:
        criteria: dict[str, Any] = {}
        if hasattr(self.view, "get_exam_form_data"):
            criteria.update(self.view.get_exam_form_data() or {})
        if hasattr(self.view, "get_exam_condition_data"):
            criteria.update(self.view.get_exam_condition_data() or {})
        if not criteria and hasattr(self.view, "get_exam_criteria"):
            criteria.update(self.view.get_exam_criteria() or {})
        return criteria

    def _get_selected_question_ids(self) -> list[int]:
        return [
            question_id
            for question in self._get_selected_view_questions()
            if (question_id := self._get_question_id(question)) is not None
        ]

    def _set_selected_questions(self, questions: list[Any]) -> None:
        self._set_auto_extracted_questions(questions)

    def _set_auto_extracted_questions(self, questions: list[Any]) -> None:
        self.auto_extracted_questions = [self._to_view_question(question) for question in questions]
        self._sync_selected_questions_to_view()

    def _set_manual_selected_questions(self, questions: list[Any]) -> None:
        self.manual_selected_questions = [self._to_view_question(question) for question in questions]
        self._sync_selected_questions_to_view()

    def _clear_selected_questions(self) -> None:
        self.auto_extracted_questions = []
        self.manual_selected_questions = []
        self._sync_selected_questions_to_view()

    def _sync_selected_questions_to_view(self) -> None:
        combined_questions = self._merge_selected_questions(
            self.auto_extracted_questions,
            self.manual_selected_questions,
        )
        self.current_questions = list(combined_questions)
        self.selected_questions = combined_questions

        if hasattr(self.view, "set_auto_extracted_questions"):
            self.view.set_auto_extracted_questions(self._get_exam_paper_questions(self.auto_extracted_questions))
        if hasattr(self.view, "set_manual_selected_questions"):
            self.view.set_manual_selected_questions(self._get_exam_paper_questions(self.manual_selected_questions))
        if hasattr(self.view, "set_selected_question_groups"):
            self.view.set_selected_question_groups(
                {
                    "auto": self._get_exam_paper_questions(self.auto_extracted_questions),
                    "manual": self._get_exam_paper_questions(self.manual_selected_questions),
                    "combined": self._get_exam_paper_questions(combined_questions),
                }
            )
        if hasattr(self.view, "set_selected_questions"):
            self.view.set_selected_questions(self._get_exam_paper_questions(combined_questions))
        if hasattr(self.view, "set_preview_data"):
            self.view.set_preview_data(self._get_exam_paper_questions(combined_questions))

    def _get_selected_view_questions(self) -> list[dict[str, Any]]:
        if self.auto_extracted_questions or self.manual_selected_questions:
            return self._merge_selected_questions(
                self.auto_extracted_questions,
                self.manual_selected_questions,
            )

        view_selected = getattr(self.view, "selected_questions", None)
        if view_selected:
            return [self._to_view_question(question) for question in view_selected]
        if self.selected_questions:
            return [self._to_view_question(question) for question in self.selected_questions]
        return [self._to_view_question(question) for question in self.current_questions]

    def _merge_selected_questions(
        self,
        base_questions: list[Any],
        added_questions: list[Any],
    ) -> list[dict[str, Any]]:
        merged = [self._to_view_question(question) for question in base_questions]
        existing_ids = {
            question_id
            for question in merged
            if (question_id := self._get_question_id(question)) is not None
        }

        for question in added_questions:
            question_id = self._get_question_id(question)
            if question_id is not None and question_id in existing_ids:
                continue
            merged.append(self._to_view_question(question))
            if question_id is not None:
                existing_ids.add(question_id)

        return merged

    def _get_manual_question_ids(self) -> list[int]:
        return [
            question_id
            for question in self.manual_selected_questions
            if (question_id := self._get_question_id(question)) is not None
        ]

    def _remove_question_from_group(self, group: str, question_id: int) -> None:
        if group == "auto":
            self.auto_extracted_questions = [
                question
                for question in self.auto_extracted_questions
                if self._get_question_id(question) != question_id
            ]
        elif group == "manual":
            self.manual_selected_questions = [
                question
                for question in self.manual_selected_questions
                if self._get_question_id(question) != question_id
            ]

    def _normalize_question_id(self, question_id: object) -> int | None:
        try:
            return int(question_id)
        except (TypeError, ValueError):
            return None

    def _to_view_question(self, question: Any) -> dict[str, Any]:
        if isinstance(question, dict):
            return dict(question)

        return {
            "id": getattr(question, "question_id", None),
            "question_id": getattr(question, "question_id", None),
            "content": getattr(question, "question_text", ""),
            "question_text": getattr(question, "question_text", ""),
            "type": getattr(question, "category", ""),
            "category": getattr(question, "category", ""),
            "sub_category": getattr(question, "sub_category", "") or "",
            "difficulty": getattr(question, "difficulty", ""),
            "answer": getattr(question, "answer_text", ""),
            "answer_text": getattr(question, "answer_text", ""),
            "tags": getattr(question, "tags", "") or "",
        }

    def _to_exam_paper_question(self, question: Any) -> dict[str, Any]:
        question_data = self._to_view_question(question)
        for key in (
            "answer",
            "answer_text",
            "correct_answer",
            "acceptable_answers",
            "allowed_answers",
            "explanation",
        ):
            question_data.pop(key, None)
        return question_data

    def _get_exam_paper_questions(self, questions: list[Any]) -> list[dict[str, Any]]:
        exam_questions = []
        for index, question in enumerate(questions, start=1):
            question_data = self._to_exam_paper_question(question)
            content = str(
                question_data.get("content")
                or question_data.get("question_text")
                or ""
            )
            answer_lines = self._build_answer_lines(content)
            question_data.update(
                {
                    "number": index,
                    "question_number": index,
                    "display_text": f"{index}. {content}",
                    "answer_blank": answer_lines[0],
                    "answer_lines": answer_lines,
                    "student_answer": "",
                    "points": question_data.get("points", ""),
                    "exam_item_type": "question_with_blank",
                }
            )
            exam_questions.append(question_data)
        return exam_questions

    def _build_answer_lines(self, content: str) -> list[str]:
        if "____" in content or "()" in content:
            return ["____________________________________"]
        return [
            "____________________________________",
            "____________________________________",
        ]

    def _get_question_id(self, question: Any) -> int | None:
        if isinstance(question, dict):
            value = question.get(
                "question_id",
                question.get("id", question.get("question_no", question.get("no"))),
            )
        else:
            value = getattr(question, "question_id", None)
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _show_exam_preview(self, questions: list[Any]) -> None:
        view_questions = self._get_exam_paper_questions(questions)
        self.current_questions = list(view_questions)
        self.selected_questions = view_questions

        if hasattr(self.view, "set_selected_questions"):
            self.view.set_selected_questions(view_questions)
        if hasattr(self.view, "set_preview_data"):
            self.view.set_preview_data(view_questions)

        exam_data = self._get_exam_criteria()
        preview_payload = {
            "exam_info": exam_data,
            "questions": view_questions,
            "total_questions": len(view_questions),
            "mode": "student_exam_paper",
        }
        preview_method_names = (
            "show_exam_preview",
            "show_exam_preview_dialog",
            "show_exam_paper_preview",
            "open_exam_preview",
            "open_exam_preview_dialog",
            "open_exam_paper_preview",
            "show_preview",
            "show_preview_dialog",
            "open_preview",
            "open_preview_dialog",
            "display_exam_preview",
            "display_preview",
        )
        for method_name in preview_method_names:
            method = getattr(self.view, method_name, None)
            if method is None:
                continue
            if self._call_preview_method(method, exam_data, view_questions, preview_payload):
                return

    def _call_preview_method(
        self,
        method: Any,
        exam_data: dict[str, Any],
        questions: list[dict[str, Any]],
        preview_payload: dict[str, Any] | None = None,
    ) -> bool:
        call_patterns = (
            (preview_payload,) if preview_payload is not None else None,
            (exam_data, questions, preview_payload) if preview_payload is not None else None,
            (exam_data, questions),
            (questions, exam_data),
            (questions,),
            (),
        )
        for args in call_patterns:
            if args is None:
                continue
            try:
                method(*args)
                return True
            except TypeError:
                continue

        return False

    def _show_message(self, message: str) -> None:
        if hasattr(self.view, "show_message"):
            self.view.show_message(message)
        else:
            print(message)

    def _show_error(self, message: str) -> None:
        if hasattr(self.view, "show_error"):
            self.view.show_error(message)
        elif hasattr(self.view, "show_message"):
            self.view.show_message(message)
        else:
            print(message)

    def _show_export_result(self, success: bool, message: str) -> None:
        if hasattr(self.view, "show_export_result"):
            self.view.show_export_result(success, message)
        elif success:
            self._show_message(message)
        else:
            self._show_error(message)

    def _connect_count_limit_events(self) -> None:
        for combo_name in ("question_type_combo", "difficulty_combo", "sub_category_combo", "tag_combo"):
            combo = getattr(self.view, combo_name, None)
            if combo is not None and hasattr(combo, "currentIndexChanged"):
                combo.currentIndexChanged.connect(lambda *_: self._update_count_limit())
        self._update_count_limit()

    def _update_count_limit(self) -> None:
        count_input = getattr(self.view, "count_input", None)
        if count_input is None or not hasattr(count_input, "setMaximum"):
            return

        criteria = self._build_service_criteria() if hasattr(self.view, "get_exam_condition_data") else self._get_exam_criteria()
        category = self._get_combo_text("question_type_combo") or criteria.get("category") or criteria.get("type")
        difficulty = self._get_combo_text("difficulty_combo") or criteria.get("difficulty")
        criteria["sub_category"] = self._normalize_filter_value(str(criteria.get("sub_category", "")), "전체 분류")
        criteria["tag"] = self._normalize_filter_value(str(criteria.get("tag", "")), "전체 태그")
        excluded_ids = set(self._get_manual_question_ids())
        max_count = self.builder_service.count_available_questions(
            criteria,
            category=category,
            difficulty=difficulty,
            excluded_question_ids=excluded_ids,
        )
        count_input.setMaximum(max(max_count, 0))

    def _get_combo_text(self, combo_name: str) -> str:
        combo = getattr(self.view, combo_name, None)
        if combo is None or not hasattr(combo, "currentText"):
            return ""
        return str(combo.currentText()).strip()
