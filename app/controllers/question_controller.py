from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QMessageBox

from app.models.question_model import Question
from app.repositories.question_repository import QuestionRepository


class QuestionController:
    def __init__(self, view: Any) -> None:
        self.view = view
        self.editing_question_id: int | None = None
        self._connect_view_events()
        self.refresh_questions()

    def _connect_view_events(self) -> None:
        self.view.on_edit_question = self.edit_question
        self.view.on_status_change_question = self.change_question_status
        self.view.register_button.clicked.connect(self.create_question)
        self.view.search_button.clicked.connect(self.refresh_questions)
        self.view.reset_filter_button.clicked.connect(self.reset_filters)
        self.view.keyword_input.textChanged.connect(self.refresh_questions)
        self.view.exam_filter.currentTextChanged.connect(self.refresh_questions)
        self.view.class_filter.currentTextChanged.connect(self.refresh_questions)
        self.view.type_filter.currentTextChanged.connect(self.refresh_questions)
        self.view.sub_category_filter.textChanged.connect(self.refresh_questions)
        self.view.difficulty_filter.currentTextChanged.connect(self.refresh_questions)
        self.view.tag_filter.textChanged.connect(self.refresh_questions)

    def refresh_questions(self) -> None:
        questions = QuestionRepository.read_all(active_only=False)
        filters = self.view.get_selected_filters()
        filtered_questions = [question for question in questions if self._matches_filters(question, filters)]
        self.view.set_questions_data([self._to_view_data(question) for question in filtered_questions])

    def create_question(self) -> None:
        form_data = self.view.get_question_form_data()
        missing_fields = self._get_missing_required_fields(form_data)
        if missing_fields:
            QMessageBox.warning(self.view, "입력 확인", f"{', '.join(missing_fields)}을(를) 입력해주세요.")
            return

        question = Question(
            question_id=self.editing_question_id,
            exam_name=form_data["exam_name"],
            class_name=form_data["class_name"],
            question_text=form_data["content"],
            category=form_data["type"],
            sub_category=form_data["sub_category"],
            difficulty=form_data["difficulty"],
            answer_text=form_data["answer"],
            acceptable_answers=form_data["allowed_answers"],
            explanation=form_data["explanation"],
            tags=form_data["tags"],
            is_active=1,
        )

        try:
            if self.editing_question_id is None:
                QuestionRepository.create(question)
            else:
                existing_question = QuestionRepository.read(self.editing_question_id)
                if existing_question is None:
                    QMessageBox.warning(self.view, "수정 실패", "수정할 문제를 찾을 수 없습니다.")
                    return
                question.is_active = existing_question.is_active
                question.created_at = existing_question.created_at
                QuestionRepository.update(question)
        except Exception as exc:
            action_text = "등록" if self.editing_question_id is None else "수정"
            QMessageBox.warning(self.view, f"{action_text} 실패", f"문제 {action_text} 중 오류가 발생했습니다.\n{exc}")
            return

        self.view.clear_form()
        self.editing_question_id = None
        self.view.set_submit_button_text("문제 등록")
        self.refresh_questions()

    def reset_filters(self) -> None:
        self.view.clear_filters()
        self.refresh_questions()

    def change_question_status(self, question_id: int, is_active: bool) -> None:
        action_text = "비활성화" if is_active else "활성화"
        answer = QMessageBox.question(
            self.view,
            f"{action_text} 확인",
            f"선택한 문제를 {action_text}하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        try:
            changed = (
                QuestionRepository.deactivate(question_id)
                if is_active
                else QuestionRepository.activate(question_id)
            )
        except Exception as exc:
            QMessageBox.warning(self.view, f"{action_text} 실패", f"문제 {action_text} 중 오류가 발생했습니다.\n{exc}")
            return

        if not changed:
            QMessageBox.warning(self.view, f"{action_text} 실패", f"{action_text}할 문제를 찾을 수 없습니다.")
            return

        self.refresh_questions()

    def edit_question(self, question_id: int) -> None:
        question = QuestionRepository.read(question_id)
        if question is None:
            QMessageBox.warning(self.view, "수정 실패", "수정할 문제를 찾을 수 없습니다.")
            return

        self.editing_question_id = question_id
        self.view.set_question_form_data(self._to_view_data(question))
        self.view.set_submit_button_text("문제 수정")
        self.view.close_question_list_window()

    def _matches_filters(self, question: Question, filters: dict[str, str]) -> bool:
        keyword = filters.get("keyword", "").lower()
        question_text = question.question_text or ""
        answer_text = question.answer_text or ""
        explanation = question.explanation or ""
        tags = question.tags or ""

        if keyword and not (
            keyword in question_text.lower()
            or keyword in answer_text.lower()
            or keyword in explanation.lower()
            or keyword in tags.lower()
        ):
            return False

        if filters.get("type") and question.category != filters["type"]:
            return False
        if filters.get("exam") and question.exam_name != filters["exam"]:
            return False
        if filters.get("class_name") and question.class_name != filters["class_name"]:
            return False
        if filters.get("sub_category") and filters["sub_category"].lower() not in (question.sub_category or "").lower():
            return False
        if filters.get("difficulty") and question.difficulty != filters["difficulty"]:
            return False
        if filters.get("tag") and filters["tag"].lower() not in tags.lower():
            return False

        return True

    def _get_missing_required_fields(self, form_data: dict[str, str]) -> list[str]:
        required_fields = {
            "content": "문제 내용",
            "type": "문제 유형",
            "difficulty": "난이도",
            "answer": "기준 정답",
        }
        return [label for key, label in required_fields.items() if not form_data.get(key)]

    def _to_view_data(self, question: Question) -> dict[str, Any]:
        return {
            "id": question.question_id,
            "exam": question.exam_name or "미지정",
            "class_name": question.class_name or "미지정",
            "content": question.question_text,
            "type": question.category,
            "sub_category": question.sub_category or "",
            "difficulty": question.difficulty,
            "answer": question.answer_text,
            "allowed_answers": question.acceptable_answers or "",
            "explanation": question.explanation or "",
            "tags": question.tags or "",
            "status": "활성" if question.is_active else "비활성",
        }
