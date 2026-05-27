from typing import Any


class ExamController:
    def __init__(self, view: Any, builder_service: Any, pdf_service: Any):
        self.view = view
        self.builder_service = builder_service
        self.pdf_service = pdf_service

        self.current_questions = []
        self.cart_items = []

        self._connect_view_events()
        self._initialize_filter_options()

    def _connect_view_events(self) -> None:
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
        if hasattr(self.view, "auto_extract_requested"):
            self.view.auto_extract_requested.connect(lambda *_: self.on_generate_clicked())
        if hasattr(self.view, "manual_select_requested"):
            self.view.manual_select_requested.connect(lambda *_: self.on_manual_select_clicked())
        if hasattr(self.view, "selection_clear_requested"):
            self.view.selection_clear_requested.connect(lambda *_: self.on_clear_selection_clicked())
        if hasattr(self.view, "preview_requested"):
            self.view.preview_requested.connect(lambda *_: self.on_preview_clicked())
        if hasattr(self.view, "pdf_export_requested"):
            self.view.pdf_export_requested.connect(lambda *_: self.on_export_clicked())
        if hasattr(self.view, "save_exam_requested"):
            self.view.save_exam_requested.connect(lambda *_: self.on_generate_clicked())
        if hasattr(self.view, "question_exclude_requested"):
            self.view.question_exclude_requested.connect(self.on_question_exclude_requested)

        self._connect_count_limit_events()

    def _initialize_filter_options(self) -> None:
        """Provide initial filter choices to the View without putting data setup in the View."""
        if not hasattr(self.view, "set_filter_options"):
            return

        if hasattr(self.builder_service, "get_filter_options"):
            filter_options = self.builder_service.get_filter_options()
        else:
            filter_options = {"question_types": ["어휘", "문법", "독해"]}

        self.view.set_filter_options(filter_options)

    def on_add_cart_clicked(self) -> None:
        """Add one builder row to the in-memory cart."""
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
        criteria = self._get_exam_criteria()
        criteria["cart_items"] = self._get_cart_items()
        criteria["selected_question_ids"] = self._get_selected_question_ids()

        is_valid, message = self.builder_service.validate_exam_request(criteria)
        if not is_valid:
            self._show_error(message)
            self._update_count_limit()
            return

        self.current_questions = self.builder_service.create_random_exam(criteria)
        self._set_selected_questions(self.current_questions)

        if hasattr(self.view, "set_build_summary_data"):
            self.view.set_build_summary_data(self.builder_service.get_last_build_summary())

    def on_manual_select_clicked(self) -> None:
        criteria = self._get_exam_criteria()
        selectable_questions = self.builder_service.get_selectable_questions(criteria)
        selectable_data = [self._to_view_question(question) for question in selectable_questions]

        if hasattr(self.view, "select_questions_from_list"):
            selected_questions = self.view.select_questions_from_list(selectable_data)
            if selected_questions is not None:
                self._set_selected_questions(selected_questions)

    def on_clear_selection_clicked(self) -> None:
        self.current_questions = []
        self._set_selected_questions([])

    def on_preview_clicked(self) -> None:
        if not self.current_questions:
            self.on_generate_clicked()
            return
        self._set_selected_questions(self.current_questions)

    def on_question_exclude_requested(self, question_id: Any) -> None:
        try:
            excluded_id = int(question_id)
        except (TypeError, ValueError):
            return

        self.current_questions = [
            question
            for question in self.current_questions
            if self._get_question_id(question) != excluded_id
        ]
        self._set_selected_questions(self.current_questions)

    def on_export_clicked(self) -> None:
        if not self.current_questions:
            self.on_generate_clicked()
        if not self.current_questions:
            return

        save_path = self._get_save_path()
        if not save_path:
            return

        exam_info = self._get_exam_criteria()
        success, message = self.pdf_service.export_exam_pdf(
            save_path, exam_info, self.current_questions
        )

        if hasattr(self.view, "show_export_result"):
            self.view.show_export_result(success, message)
        else:
            print(f"PDF Export Result: {message}")

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
        if hasattr(self.view, "get_selected_question_ids"):
            return self.view.get_selected_question_ids() or []
        return [self._get_question_id(question) for question in self.current_questions if self._get_question_id(question)]

    def _set_selected_questions(self, questions: list[Any]) -> None:
        self.current_questions = list(questions)
        view_questions = [self._to_view_question(question) for question in self.current_questions]
        if hasattr(self.view, "set_selected_questions"):
            self.view.set_selected_questions(view_questions)
        if hasattr(self.view, "set_preview_data"):
            self.view.set_preview_data(view_questions)

    def _get_save_path(self) -> str:
        if hasattr(self.view, "get_pdf_save_path"):
            return self.view.get_pdf_save_path()
        if hasattr(self.view, "get_save_path"):
            return self.view.get_save_path()
        return ""

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

    def _get_question_id(self, question: Any) -> int | None:
        if isinstance(question, dict):
            value = question.get("question_id", question.get("id"))
        else:
            value = getattr(question, "question_id", None)
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _show_error(self, message: str) -> None:
        if hasattr(self.view, "show_error"):
            self.view.show_error(message)
        elif hasattr(self.view, "show_message"):
            self.view.show_message(message)
        else:
            print(message)

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

        criteria = self._get_exam_criteria()
        category = criteria.get("category") or criteria.get("type")
        difficulty = criteria.get("difficulty")
        excluded_ids = set(self._get_selected_question_ids())
        max_count = self.builder_service.count_available_questions(
            criteria,
            category=category,
            difficulty=difficulty,
            excluded_question_ids=excluded_ids,
        )
        count_input.setMaximum(max(max_count, 0))
