from __future__ import annotations

from pathlib import Path
from typing import Any


class PdfExportService:
    def export_exam_pdf(self, file_path: str, exam_info: dict, questions: list[Any]) -> tuple[bool, str]:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.pdfgen import canvas

            font_name = self._register_korean_font(pdfmetrics, TTFont)
            pdf = canvas.Canvas(file_path, pagesize=A4)
            pdf.setFont(font_name, 11)
            _, height = A4
            y = height - 50

            pdf.setFont(font_name, 15)
            pdf.drawString(50, y, f"시험명: {self._get_exam_value(exam_info, 'exam_name', 'title')}")
            y -= 22
            pdf.setFont(font_name, 10)
            pdf.drawString(50, y, f"대상 반: {self._get_exam_value(exam_info, 'class_name', 'target_class')}")
            y -= 22
            pdf.drawString(50, y, f"시험 일자: {self._get_exam_value(exam_info, 'exam_date')}")
            y -= 34

            for index, question in enumerate(questions, start=1):
                if y < 80:
                    pdf.showPage()
                    pdf.setFont(font_name, 10)
                    y = height - 50

                content = self._get_question_value(question, "content", "question_text")

                for line_index, line in enumerate(self._wrap_text(f"{index}. {content}", 86)):
                    if y < 80:
                        pdf.showPage()
                        pdf.setFont(font_name, 10)
                        y = height - 50
                    x = 50 if line_index == 0 else 66
                    pdf.drawString(x, y, line)
                    y -= 16

                y -= 10

            pdf.save()
            return True, "PDF 저장 완료"
        except Exception as exc:
            return False, str(exc)

    def _register_korean_font(self, pdfmetrics: Any, ttfont_cls: Any) -> str:
        font_candidates = [
            Path("C:/Windows/Fonts/malgun.ttf"),
            Path("C:/Windows/Fonts/malgunbd.ttf"),
            Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
            Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        ]

        for font_path in font_candidates:
            if font_path.exists():
                font_name = "TeacherExamKorean"
                pdfmetrics.registerFont(ttfont_cls(font_name, str(font_path)))
                return font_name

        return "Helvetica"

    def _get_exam_value(self, exam_info: dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = exam_info.get(key)
            if value not in (None, ""):
                return str(value)
        return ""

    def _get_question_value(self, question: Any, *keys: str) -> str:
        for key in keys:
            if isinstance(question, dict):
                value = question.get(key)
            else:
                attr_name = "question_text" if key == "content" else key
                value = getattr(question, attr_name, None)
            if value not in (None, ""):
                return str(value)
        return ""

    def _wrap_text(self, text: str, max_chars: int) -> list[str]:
        if len(text) <= max_chars:
            return [text]

        lines = []
        current = ""
        for word in text.split():
            next_value = f"{current} {word}".strip()
            if len(next_value) <= max_chars:
                current = next_value
                continue
            if current:
                lines.append(current)
            current = word

        if current:
            lines.append(current)
        return lines or [text[:max_chars]]
