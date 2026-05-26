from __future__ import annotations


class PdfExportService:
    def export_exam_pdf(self, file_path: str, exam_info: dict, questions: list[dict]) -> tuple[bool, str]:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas

            pdf = canvas.Canvas(file_path, pagesize=A4)
            _, height = A4
            y = height - 50

            pdf.drawString(50, y, self._safe_pdf_text(f"Exam: {exam_info.get('exam_name', '')}"))
            y -= 22
            pdf.drawString(50, y, self._safe_pdf_text(f"Class: {exam_info.get('class_name', '')}"))
            y -= 22
            pdf.drawString(50, y, self._safe_pdf_text(f"Date: {exam_info.get('exam_date', '')}"))
            y -= 34

            for index, question in enumerate(questions, start=1):
                if y < 80:
                    pdf.showPage()
                    y = height - 50

                content = str(question.get("content", ""))
                answer = str(question.get("answer", ""))
                pdf.drawString(50, y, self._safe_pdf_text(f"{index}. {content[:90]}"))
                y -= 18
                pdf.drawString(70, y, self._safe_pdf_text(f"Answer: {answer[:80]}"))
                y -= 26

            pdf.save()
            return True, "PDF 저장 완료"
        except Exception as exc:
            return False, str(exc)

    def _safe_pdf_text(self, text: str) -> str:
        return text.encode("latin-1", "replace").decode("latin-1")
