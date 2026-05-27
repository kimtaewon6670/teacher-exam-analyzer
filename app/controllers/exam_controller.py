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
        criteria = self.view.get_exam_criteria()
        criteria["cart_items"] = self._get_cart_items()

        self.current_questions = self.builder_service.create_random_exam(criteria)
        self.view.set_preview_data(self.current_questions)

        if hasattr(self.view, "set_build_summary_data"):
            self.view.set_build_summary_data(self.builder_service.get_last_build_summary())

    def on_export_clicked(self) -> None:
        if not self.current_questions:
            return

        save_path = self.view.get_save_path()
        if not save_path:
            return

        exam_info = self.view.get_exam_criteria()
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
