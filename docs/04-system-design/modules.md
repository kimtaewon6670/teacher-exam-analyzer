# 4.3 주요 기능/모듈

본 시스템은 학생 관리, 문제은행 관리, 시험지 생성, 결과 입력, 결과 분석, 대시보드 기능으로 구성된다.

## 학생 관리

학생 정보를 등록하고 관리하는 기능이다.

주요 기능:

- 학생 등록
- 학생 수정
- 학생 활성화/비활성화
- 학생 검색
- 반 필터링

관련 파일:

- student_manage_view.py
- student_controller.py
- student_repository.py
- student_model.py

## 문제은행 관리

단답형 문제를 등록하고 유형, 난이도, 세부 분류별로 관리하는 기능이다.

주요 기능:

- 문제 등록
- 문제 수정
- 문제 활성화/비활성화
- 문제 검색
- 문제 유형 필터링
- 난이도 필터링
- 기준 정답 및 허용 답안 관리

관련 파일:

- question_bank_view.py
- question_controller.py
- question_repository.py
- question_model.py

## 시험지 생성

문제은행에 등록된 문제를 바탕으로 시험지를 생성하는 기능이다.

주요 기능:

- 시험 기본 정보 입력
- 조건 기반 문제 자동 추출
- 문제 직접 선택
- 선택된 문제 목록 확인
- 문제 제외
- 시험지 저장
- PDF 출력
- 생성된 시험지 목록 조회

관련 파일:

- exam_builder_view.py
- exam_controller.py
- exam_builder_service.py
- pdf_export_service.py
- exam_repository.py
- exam_question_repository.py

## 결과 입력

시험 후 학생별 답안을 입력하고 저장하는 기능이다.

주요 기능:

- 시험 선택
- 반 선택
- 학생 선택
- 학생별 답안 입력
- CSV 답안 불러오기
- 답안 입력값 검증
- 답안 저장
- 자동 채점 실행
- 학생별/문항별 결과 확인

관련 파일:

- result_input_view.py
- result_controller.py
- result_input_service.py
- grading_service.py
- result_repository.py
- answer_record_repository.py

## 결과 분석

저장된 시험 결과를 바탕으로 반 전체와 문항별 성취도를 분석하는 기능이다.

주요 기능:

- 시험별 결과 조회
- 반별 결과 조회
- 반 전체 평균 점수 확인
- 전체 정답률/오답률 확인
- 문항별 정답률/오답률 분석
- 문제 유형별 정답률 분석
- 세부 분류별 정답률 분석
- 난이도별 정답률 분석
- 반 전체 취약 유형 확인

관련 파일:

- analysis_view.py
- analysis_controller.py
- analysis_service.py
- result_repository.py
- answer_record_repository.py

## 대시보드

전체 시험 결과를 요약해서 보여주는 화면이다.

주요 기능:

- 시험 결과 요약 표시
- 학생별 결과 조회
- 그래프 기반 결과 시각화
- 학생별 결과 CSV 내보내기

관련 파일:

- dashboard_view.py
- dashboard_controller.py
- analysis_service.py

## 공통 유틸리티

여러 기능에서 공통으로 사용하는 보조 기능이다.

주요 기능:

- 상수 관리
- 입력값 검증
- 답안 정규화
- 차트 표시 보조

관련 파일:

- constants.py
- validators.py
- answer_normalizer.py
- chart_util.py
