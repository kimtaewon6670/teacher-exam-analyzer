import random
from app.models.exam_model import Question

class ExamBuilderService:
    def __init__(self, repository):
        self.repository = repository

    def create_random_exam(self, criteria):
        """알고리즘: 문제은행에서 조건에 맞는 문제를 무작위로 추출합니다."""
        # 1. Repository를 통해 후보 문제 조회
        all_candidates = self.repository.get_questions_by_filter(
            category=criteria.get('category'),
            difficulty=criteria.get('difficulty')
        )

        # 2. 데이터가 없을 경우를 대비한 샘플 데이터 로직 (Core 팀원용)
        if not all_candidates:
            all_candidates = self._get_sample_pool()

        # 3. 무작위 추출 알고리즘
        count = min(len(all_candidates), criteria.get('count', 0))
        selected = random.sample(all_candidates, count)
        
        return selected

    def _get_sample_pool(self):
        """DB 연결 전 테스트를 위한 샘플 문제 생성 메서드"""
        return [
            Question(i, f"영어 문장 {i}의 빈칸에 알맞은 것은?", "문법", "보통", "answer")
            for i in range(1, 21)
        ]

class PdfExportService:
    def export_exam_pdf(self, file_path, exam_info, questions):
        """PDF 생성 및 파일 저장 로직 (reportlab 활용)"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            
            c = canvas.Canvas(file_path, pagesize=A4)
            # TODO: 한글 폰트 등록 (reportlab.pdfbase.pdfmetrics)
            
            # PDF 그리기 로직 (생략 - 핵심 로직 집중)
            c.drawString(100, 800, f"Test Title: {exam_info.get('title')}")
            for i, q in enumerate(questions, 1):
                c.drawString(100, 800 - (i*30), f"{i}. {q.question_text}")
            
            c.save()
            return True, "저장 완료"
        except Exception as e:
            return False, str(e)