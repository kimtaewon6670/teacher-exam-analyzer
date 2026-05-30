# 3.4 요구사항 추적표

| 요구 ID | 관련 기능 | 관련 계층/파일 예시 | 검증 방법 |
| --- | --- | --- | --- |
| UR-01, FR-01~FR-04 | 학생 관리 | `student_controller.py`, `student_repository.py`, `student_model.py` | 학생 등록/수정/비활성화 테스트 |
| UR-02, FR-05~FR-10 | 문제은행 관리 | `question_controller.py`, `question_repository.py`, `question_model.py` | 문제 CRUD 및 검색/필터 테스트 |
| UR-04, FR-11~FR-15 | 시험지 생성 | `exam_controller.py`, `exam_builder_service.py`, `exam_repository.py` | 조건 추출, 직접 선택, 미리보기 테스트 |
| UR-06, FR-16~FR-18 | 시험지 저장/출력 | `exam_repository.py`, `exam_question_repository.py`, `pdf_export_service.py` | 저장 목록, 상세 조회, PDF 출력 테스트 |
| UR-07, FR-19~FR-22 | 결과 입력 | `result_controller.py`, `result_input_service.py`, `answer_record_repository.py` | 직접 입력, CSV 업로드, 입력 검증 테스트 |
| UR-08, FR-23~FR-25 | 정답 비교/채점 | `answer_normalizer.py`, `result_input_service.py`, `grading_service.py` | 정규화, 허용 답안, 점수 계산 테스트 |
| UR-09, FR-26 | 결과 조회 | `result_controller.py`, `result_input_service.py`, `result_repository.py` | 시험별/학생별 결과 조회 테스트 |
| UR-10, FR-27~FR-30 | 결과 분석/대시보드 | `analysis_controller.py`, `analysis_service.py`, `dashboard_controller.py` | 통계 계산, 차트 데이터, 학생별 결과 테스트 |
| UR-12, FR-31 | 예외 처리 | Controller/Service 전반 | 데이터 없음, 저장 실패, CSV 오류 테스트 |
| NFR-03~NFR-06 | MVC 구조 | `app/models`, `app/controllers`, `app/services`, `app/repositories` | 코드 리뷰 및 계층별 책임 확인 |
| CON-01~CON-06 | 시스템 제약 | 전체 프로젝트 | 실행 환경 및 외부 의존성 확인 |
