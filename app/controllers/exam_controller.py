class ExamController:
    def __init__(self, view, builder_service, pdf_service):
        self.view = view
        self.builder_service = builder_service
        self.pdf_service = pdf_service
        
        self.current_questions = [] # 현재 추출된 문항 임시 보관

        # View에 정의된 인스턴스 변수(버튼)에 시그널 연결
        self.view.generate_button.clicked.connect(self.on_generate_clicked)
        self.view.export_button.clicked.connect(self.on_export_clicked)

    def on_generate_clicked(self):
        """시험지 생성 버튼 클릭 시 흐름 제어"""
        # 1. View에서 입력값 수집 (이미 정의된 get_xxx 메서드 활용)
        criteria = self.view.get_exam_criteria()
        
        # 2. Service에 알고리즘 처리 요청
        self.current_questions = self.builder_service.create_random_exam(criteria)
        
        # 3. View에 데이터 주입 (이미 정의된 set_xxx 메서드 활용)
        self.view.set_preview_data(self.current_questions)

    def on_export_clicked(self):
        """PDF 내보내기 버튼 클릭 시 흐름 제어"""
        if not self.current_questions:
            return

        # 1. View로부터 저장 경로 획득
        save_path = self.view.get_save_path()
        if not save_path:
            return

        # 2. Service에 PDF 파일 생성 요청
        exam_info = self.view.get_exam_criteria()
        success, msg = self.pdf_service.export_exam_pdf(
            save_path, exam_info, self.current_questions
        )
        
        # 3. 결과 알림 (필요 시 View 메서드 호출)
        print(f"PDF Export Result: {msg}")