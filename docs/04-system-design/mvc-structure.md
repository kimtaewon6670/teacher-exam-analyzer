# 4.2 MVC 구조

본 프로젝트는 View, Controller, Service, Repository를 분리한 MVC 기반 구조를 따른다. 이를 통해 화면 표시, 이벤트 처리, 비즈니스 로직, 데이터베이스 접근 역할을 명확히 구분한다.

## View

위치:

app/views

역할:

- 화면 표시
- 사용자 입력값 제공
- 버튼, 입력창, 콤보박스, 테이블 등 UI 구성
- Controller가 사용할 수 있는 get/set 메서드 제공
- DB나 Repository 직접 호출 금지

주요 View 파일:

- main_window.py
- dashboard_view.py
- student_manage_view.py
- question_bank_view.py
- exam_builder_view.py
- result_input_view.py
- analysis_view.py
- report_view.py

## Controller

위치:

app/controllers

역할:

- View 이벤트 연결
- 사용자 입력값 수집
- Service 또는 Repository 호출
- 처리 결과를 View에 전달
- 화면과 Core 로직 사이의 흐름 제어

주요 Controller 파일:

- main_controller.py
- dashboard_controller.py
- student_controller.py
- question_controller.py
- exam_controller.py
- result_controller.py
- analysis_controller.py

## Service

위치:

app/services

역할:

- 핵심 비즈니스 로직 처리
- 시험지 생성
- 답안 저장 처리
- 자동 채점
- 결과 분석
- CSV 처리
- PDF 출력 처리

주요 Service 파일:

- exam_builder_service.py
- result_input_service.py
- grading_service.py
- analysis_service.py
- csv_import_service.py
- pdf_export_service.py

## Repository

위치:

app/repositories

역할:

- SQLite DB 접근
- CRUD 처리
- SQL 로직 관리
- View에서 직접 호출하지 않고 Controller 또는 Service를 통해 사용

주요 Repository 파일:

- db.py
- student_repository.py
- question_repository.py
- exam_repository.py
- exam_question_repository.py
- result_repository.py
- answer_record_repository.py

## Model

위치:

app/models

역할:

- 데이터 구조 정의
- 학생, 문제, 시험, 답안, 결과 관련 데이터 객체 관리

주요 Model 파일:

- student_model.py
- question_model.py
- exam_model.py
- exam_question_model.py
- exam_result_model.py
- answer_record_model.py

## MVC 적용 원칙

- View는 화면 표시와 입력값 제공만 담당한다.
- View는 DB, Repository, Service를 직접 호출하지 않는다.
- Controller는 View와 Core 로직을 연결한다.
- Service는 핵심 기능 로직을 담당한다.
- Repository는 데이터베이스 접근만 담당한다.
- Model은 데이터 구조를 정의한다.
