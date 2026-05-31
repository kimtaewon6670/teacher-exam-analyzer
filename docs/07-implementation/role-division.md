# 7.2 역할 분담

> 작성 기준: `feature/integration` 브랜치의 최종 통합 코드 구조와 기능 흐름

## 7.2.1 역할 개요

| 담당 | 역할 | 주요 책임 |
| --- | --- | --- |
| UI 담당 | PySide6 화면 구현 | 사용자가 보는 화면 구성, 입력 위젯 배치, 테이블/차트 표시, 버튼 시그널 연결이 가능한 View 구성 |
| Core 담당 | DB 및 핵심 로직 구현 | SQLite DB, Repository, Service, Controller 흐름 구현, 시험지 생성, 채점, 분석, CSV/PDF 처리 |
| Docs 담당 | 문서 작성 및 관리 | 프로젝트 개요, 요구사항, 설계 문서, 테스트 계획, 구현 일정, 진행 결과, 의사결정 기록 정리 |

## 7.2.2 UI 담당 상세 역할

| 영역 | 담당 내용 | 관련 파일 예시 |
| --- | --- | --- |
| 메인 화면 | 사이드바, 화면 전환, 전체 레이아웃 구성 | `app/views/main_window.py` |
| 대시보드 화면 | 요약 카드, 정답률 차트, 학생별 결과 표, 검색/페이지 UI 구성 | `app/views/dashboard_view.py` |
| 학생 관리 화면 | 학생 등록 입력창, 검색 영역, 학생 목록 테이블 구성 | `app/views/student_manage_view.py` |
| 문제은행 화면 | 문제 등록 폼, 문제 검색/필터, 문제 목록 테이블 구성 | `app/views/question_bank_view.py` |
| 시험지 생성 화면 | 시험 기본 정보, 문제 추출 조건, 선택 문제 목록, 저장 시험지 목록, 미리보기 UI 구성 | `app/views/exam_builder_view.py` |
| 결과 입력 화면 | 시험/반/학생 선택, 답안 입력, CSV 미리보기, 검증 메시지, 결과 보기 UI 구성 | `app/views/result_input_view.py` |
| 결과 분석 화면 | 분석 조건, 요약 카드, 문항별/유형별/세부 분류별/난이도별 분석 표 구성 | `app/views/analysis_view.py` |

UI 담당은 화면 디자인과 사용자 입력 요소를 구현한다. 버튼은 Controller에서 시그널 연결이 가능하도록 `self.register_button`, `self.search_button`, `self.save_button`처럼 인스턴스 변수로 제공한다. 화면에서 직접 DB에 접근하거나 채점/분석 로직을 처리하지 않는다.

## 7.2.3 Core 담당 상세 역할

| 영역 | 담당 내용 | 관련 파일 예시 |
| --- | --- | --- |
| DB 초기화 | SQLite 테이블 생성 및 컬럼 보정 | `app/repositories/db.py` |
| 학생 관리 로직 | 학생 CRUD, 활성/비활성 처리, 반별 학생 조회 | `student_controller.py`, `student_repository.py` |
| 문제은행 로직 | 문제 CRUD, 검색/필터, 활성/비활성 처리 | `question_controller.py`, `question_repository.py` |
| 시험지 생성 로직 | 조건 기반 자동 추출, 직접 선택 문제 병합, 저장 시험지 관리 | `exam_controller.py`, `exam_builder_service.py` |
| PDF 출력 | 학생 배부용 시험지 PDF 생성, 정답 미노출 처리 | `pdf_export_service.py` |
| 결과 입력 로직 | 직접 입력 답안 저장, CSV 파싱, 입력값 검증 | `result_controller.py`, `result_input_service.py` |
| 자동 채점 | 답안 정규화, 기준 정답/허용 답안 비교, 점수 계산 | `answer_normalizer.py`, `grading_service.py`, `result_input_service.py` |
| 결과 저장/조회 | 학생별 결과, 문항별 답안 기록 저장 및 조회 | `result_repository.py`, `answer_record_repository.py` |
| 결과 분석 | 반 평균, 정답률/오답률, 취약 유형, 대시보드 데이터 계산 | `analysis_controller.py`, `analysis_service.py`, `dashboard_controller.py` |

Core 담당은 View와 Service/Repository 사이의 흐름을 Controller에서 연결한다. DB 저장과 조회는 Repository에서 처리하고, 채점/분석/추천/시험지 생성 같은 핵심 로직은 Service에서 처리한다. View 디자인은 임의로 변경하지 않는다.

## 7.2.4 Docs 담당 상세 역할

| 영역 | 담당 내용 | 관련 문서 |
| --- | --- | --- |
| 프로젝트 개요 | 프로젝트 목적, 기획 의도, 주요 기능 정리 | `docs/01-project-overview/project-overview.md` |
| 이해관계자/사용자 | 주요 사용자, 사용자 요구, 사용 시나리오 정리 | `docs/02-stakeholders-users/stakeholders-and-users.md` |
| 요구사항 | 기능 요구사항, 비기능 요구사항, 제약사항, 추적표 작성 | `docs/03-requirements/` |
| 시스템 설계 | MVC 구조, 모듈 구성, 데이터 구조, UI 흐름 정리 | `docs/04-system-design/` |
| 테스트 계획 | 테스트 대상, 테스트 케이스, 검증 방법 정리 | `docs/05-test-plan/` |
| 위험 관리 | 개발 중 발생 가능한 위험과 대응 방안 정리 | `docs/06-risk-management/risk-management.md` |
| 구현 일정 | 마일스톤, 역할 분담, 진행 결과 정리 | `docs/07-implementation/` |
| 의사결정 기록 | 주요 설계/구현 결정과 사유 기록 | `docs/08-decisions/decision-log.md` |

Docs 담당은 통합 브랜치의 실제 코드 구조와 기능 상태를 기준으로 문서를 갱신한다. 기능이 변경되면 요구사항, 테스트 케이스, 진행 결과 문서가 함께 맞춰져야 한다.

## 7.2.5 협업 기준

| 기준 | 내용 |
| --- | --- |
| 브랜치 전략 | `main`은 최종 제출용, `feature/integration`은 통합 확인용, `feature/ui`, `feature/core`, `feature/docs`는 역할별 작업용으로 사용한다. |
| MVC 책임 분리 | View는 화면, Controller는 흐름 제어, Service는 핵심 로직, Repository는 DB 접근을 담당한다. |
| UI-Core 연결 | View는 `get_xxx_data()`, `set_xxx_data()`, `clear_xxx()` 형태의 메서드를 제공하고 Controller가 이를 호출한다. |
| 데이터 기준 | 학생, 문제, 시험지, 답안, 결과 데이터는 SQLite DB를 기준으로 관리한다. |
| 검증 기준 | 기능 구현 후 테스트 케이스와 요구사항 추적표 기준으로 동작을 확인한다. |
