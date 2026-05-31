# Teacher Exam Analyzer

교사용 단답형 문제은행 기반 시험지 생성 및 결과 분석 데스크톱 앱

---

## 1. 프로젝트 개요

Teacher Exam Analyzer는 교사가 단답형 문제를 문제은행에 등록하고, 등록된 문제를 기반으로 시험지를 생성한 뒤, 학생 답안을 채점하고 결과를 분석할 수 있도록 돕는 로컬 데스크톱 애플리케이션이다.

교사는 어휘, 문법, 독해 등 영어 학습 영역별 문제를 문제은행에 저장할 수 있으며, 문제 유형, 세부 분류, 난이도, 태그, 대상 반, 시험명 등의 조건을 활용하여 문제를 검색하거나 시험지를 구성할 수 있다. 생성된 시험지는 저장할 수 있고, 필요하면 PDF 파일로 출력하여 학생들에게 배부할 수 있다.

학생은 앱 안에서 직접 시험을 치르는 것이 아니라, 교사가 생성한 시험지를 통해 시험을 본다. 시험이 끝난 뒤 교사는 학생별 답안을 직접 입력하거나 CSV 파일로 불러와 자동 채점을 수행한다. 시스템은 학생 답안을 기준 정답 및 허용 답안과 비교하여 정답 여부를 판단하고, 정답 수, 오답 수, 점수, 정답률을 계산하여 저장한다.

저장된 결과는 대시보드와 결과 분석 화면에서 확인할 수 있다. 시스템은 반 평균 점수, 전체 정답률, 문항별 정답률, 문제 유형별 정답률, 세부 분류별 정답률, 난이도별 정답률, 학생별 점수 등을 표와 그래프 형태로 제공한다.

본 프로젝트는 웹 서비스가 아닌 로컬 기반 데스크톱 앱이다. 데이터는 사용자의 PC 내부 SQLite 데이터베이스에 저장되며, 외부 서버나 외부 LLM API를 사용하지 않는다.

---

## 2. 기획 의도

본 프로젝트는 교사가 보유한 단답형 문제를 체계적으로 관리하고, 원하는 조건에 따라 시험지를 쉽게 생성하며, 시험 결과를 데이터 기반으로 분석할 수 있도록 돕기 위해 기획되었다.

일반적으로 교사는 수업이나 시험에 사용할 문제를 한글 문서, 엑셀 파일, 개인 자료 폴더 등에 나누어 관리한다. 이 경우 시험지를 만들 때 문제를 직접 찾고, 복사하고, 유형과 난이도를 맞추는 과정이 반복적으로 발생한다.

또한 시험이 끝난 뒤에는 총점이나 평균 점수 정도만 확인하는 경우가 많아, 학생들이 어떤 유형의 문제에서 어려움을 겪었는지 구체적으로 파악하기 어렵다.

이에 본 시스템은 문제를 문제은행 형태로 등록하고, 문제 유형, 세부 분류, 난이도, 태그를 기준으로 시험지를 생성할 수 있도록 한다. 교사는 직접 문제를 선택할 수도 있고, 조건을 설정하여 문제를 자동으로 추출할 수도 있다.

시험 결과 입력 후에는 문항별 정답률, 문제 유형별 정답률, 세부 분류별 정답률, 난이도별 정답률, 반 평균 점수 등을 계산하고 이를 표와 그래프로 시각화한다. 이를 통해 교사는 단순 점수보다 구체적인 기준으로 반 전체의 학습 상태와 취약한 문제 유형을 확인할 수 있다.

---

## 3. 주요 기능

### 3.1 학생 관리 기능

- 학생 이름, 학번, 반 정보 등록
- 등록된 학생 목록 조회
- 학생 이름, 학번, 반 기준 검색
- 학생 정보 수정
- 학생 활성화 및 비활성화
- 비활성화된 학생의 기존 시험 결과 보존

### 3.2 문제은행 관리 기능

- 단답형 문제 등록
- 시험명, 대상 반, 문제 내용 입력
- 문제 유형, 세부 분류, 난이도 입력
- 기준 정답, 허용 답안, 해설, 태그 입력
- 등록된 문제 목록 조회
- 키워드, 시험명, 반, 유형, 세부 분류, 난이도, 태그 기준 검색 및 필터링
- 문제 수정
- 문제 활성화 및 비활성화

### 3.3 시험지 생성 기능

- 문제은행 기반 시험지 생성
- 문제 유형, 세부 분류, 난이도, 태그, 반 정보 기준 문제 추출
- 유형별 문항 수 조건 지정
- 난이도별 문항 수 조건 지정
- 조건 장바구니 방식의 시험 구성
- 조건 기반 자동 문제 추출
- 교사 수동 문제 선택
- 자동 추출 문제와 수동 선택 문제 병합
- 선택된 문제 제외 및 선택 초기화
- 시험명, 설명, 학년도, 학기, 시험 유형, 시험일, 대상 반 저장
- 생성된 시험지 목록 조회
- 저장된 시험지 상세 조회
- 시험지 삭제

### 3.4 시험지 저장 및 PDF 출력 기능

- 생성된 시험지 저장
- 저장된 시험지 목록 관리
- 시험지 미리보기
- 시험지를 PDF 파일로 출력
- Windows, macOS, Linux 환경별 한글 폰트 후보 처리

### 3.5 시험 결과 입력 및 자동 채점 기능

- 시험, 반, 학생 선택
- 학생별 답안 직접 입력
- CSV 파일을 통한 답안 일괄 입력
- CSV 학생 번호와 등록 학생 매칭
- 입력값 검증
- 누락 답안 검증
- 학생 답안 저장
- 기준 정답 및 허용 답안 기반 자동 채점
- 학생별 정답 수, 오답 수, 점수, 정답률 계산

### 3.6 시험 결과 저장 기능

- 학생별 시험 결과 저장
- 문항별 학생 답안 저장
- 기준 정답과 학생 답안 함께 저장
- 문항별 정오답 여부 저장
- 재채점 시 기존 학생 결과를 교체하여 중복 결과 방지
- 시험별 결과 조회
- 학생별 결과 조회

### 3.7 시험 결과 분석 기능

- 반 전체 평균 점수 분석
- 전체 정답률 분석
- 문항별 정답률 분석
- 문제 유형별 정답률 분석
- 세부 분류별 정답률 분석
- 난이도별 정답률 분석
- 학생별 점수 및 정답률 조회
- 반 전체 취약 영역 확인

### 3.8 시각화 대시보드 기능

- 응시 학생 수 표시
- 총 문항 수 표시
- 반 평균 점수 표시
- 전체 정답률 표시
- 문항별 정답률 그래프
- 유형별 정답률 그래프
- 세부 분류별 정답률 그래프
- 난이도별 정답률 그래프
- 학생별 결과 테이블

### 3.9 예외 처리 기능

- 필수 입력값 누락 안내
- 존재하지 않는 학생, 문제, 시험 접근 안내
- 조건에 맞는 문제 부족 안내
- CSV 파일 읽기 실패 안내
- CSV 학생 번호 매칭 실패 안내
- 누락 답안 안내
- 데이터베이스 저장 실패 안내
- PDF 출력 실패 안내

---

## 4. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python |
| GUI / View | PySide6 |
| Database | SQLite |
| Data Processing | pandas |
| Visualization | matplotlib |
| PDF Export | reportlab |
| Architecture | MVC Pattern |
| Version Control | Git / GitHub |

---

## 5. 기술 선택 이유

### 5.1 Python

Python은 데이터 처리, 파일 입출력, 데스크톱 앱 개발, 통계 분석을 모두 구현할 수 있는 언어이다. 본 프로젝트는 시험 결과 데이터 처리와 분석 기능이 중요하므로 Python을 기반 언어로 사용하였다.

### 5.2 PySide6

PySide6는 Python 기반 데스크톱 GUI 라이브러리이다. 학생 관리, 문제은행 관리, 시험지 생성, 결과 입력, 결과 분석 화면을 데스크톱 앱 형태로 구현하기 위해 사용하였다.

### 5.3 SQLite

SQLite는 별도 서버 설치 없이 로컬 파일 기반으로 동작하는 데이터베이스이다. 본 프로젝트는 외부 서버 없이 사용자 PC에서 실행되는 로컬 데스크톱 앱이므로 SQLite를 사용하여 학생, 문제, 시험, 답안, 결과 데이터를 저장한다.

### 5.4 pandas

pandas는 표 형태의 데이터를 처리하고 분석하는 데 적합하다. 시험 결과 데이터를 바탕으로 평균 점수, 정답률, 문항별 정답률, 유형별 정답률, 난이도별 정답률 등을 계산하는 데 활용할 수 있다.

### 5.5 matplotlib

matplotlib는 Python 기반 그래프 시각화 라이브러리이다. 분석 결과를 문항별, 유형별, 세부 분류별, 난이도별 그래프로 표현하기 위해 사용한다.

### 5.6 reportlab

reportlab은 Python에서 PDF 파일을 생성할 수 있는 라이브러리이다. 생성된 시험지를 PDF 형태로 저장하거나 출력하기 위해 사용한다.

---

## 6. 시스템 구조

본 프로젝트는 MVC 구조를 기반으로 하며, 화면 표시, 사용자 요청 처리, 핵심 로직, 데이터베이스 접근 역할을 분리한다.

```text
사용자
  → View
  → Controller
  → Service
  → Repository
  → SQLite Database
```

### 6.1 MVC 및 계층 구성

| 구성 요소 | 역할 |
|---|---|
| View | PySide6 기반 화면 표시 및 사용자 입력 처리 |
| Controller | View에서 발생한 사용자 요청 처리 및 기능 흐름 제어 |
| Model | 학생, 문제, 시험지, 답안, 결과 데이터 구조 관리 |
| Service | 시험지 생성, 정답 비교, 자동 채점, 결과 분석, PDF 출력 등 핵심 로직 처리 |
| Repository | SQLite 데이터베이스 접근 및 CRUD 처리 |
| Utils | 답안 정규화, 상수, 차트 등 공통 기능 제공 |

### 6.2 처리 흐름

사용자가 View에서 버튼 클릭이나 입력을 수행하면 Controller가 요청을 받아 Service를 호출한다. Service는 문제 추출, 시험지 생성, 정답 비교, 채점, 결과 분석 등의 핵심 로직을 처리하고, 필요한 데이터 조회와 저장은 Repository를 통해 SQLite DB에서 수행한다.

---

## 7. 프로젝트 폴더 구조

```text
teacher-exam-analyzer/
│
├─ main.py
├─ requirements.txt
├─ README.md
│
├─ data/
│  ├─ .gitkeep
│  └─ dashboard_student_results.csv
│
├─ docs/
│  ├─ 01-project-overview/
│  │  └─ project-overview.md
│  ├─ 02-stakeholders-users/
│  │  └─ stakeholders-and-users.md
│  ├─ 03-requirements/
│  │  ├─ requirements.md
│  │  └─ requirements-traceability.md
│  ├─ 04-system-design/
│  │  ├─ architecture.md
│  │  ├─ data-structure.md
│  │  ├─ modules.md
│  │  ├─ mvc-structure.md
│  │  └─ ui-flow.md
│  ├─ 05-test-plan/
│  │  ├─ test-case.md
│  │  └─ test-plan.md
│  ├─ 06-risk-management/
│  │  └─ risk-management.md
│  ├─ 07-implementation/
│  │  ├─ implementation-schedule.md
│  │  ├─ progress-result.md
│  │  └─ role-division.md
│  └─ 08-decisions/
│     └─ decision-log.md
│
├─ app/
│  ├─ __init__.py
│  │
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ student_model.py
│  │  ├─ question_model.py
│  │  ├─ exam_model.py
│  │  ├─ exam_question_model.py
│  │  ├─ exam_builder_model.py
│  │  ├─ exam_result_model.py
│  │  └─ answer_record_model.py
│  │
│  ├─ views/
│  │  ├─ __init__.py
│  │  ├─ main_window.py
│  │  ├─ dashboard_view.py
│  │  ├─ student_manage_view.py
│  │  ├─ question_bank_view.py
│  │  ├─ question_manage_view.py
│  │  ├─ exam_builder_view.py
│  │  ├─ result_input_view.py
│  │  ├─ analysis_view.py
│  │  └─ report_view.py
│  │
│  ├─ controllers/
│  │  ├─ __init__.py
│  │  ├─ main_controller.py
│  │  ├─ student_controller.py
│  │  ├─ question_controller.py
│  │  ├─ exam_controller.py
│  │  ├─ result_controller.py
│  │  ├─ analysis_controller.py
│  │  └─ dashboard_controller.py
│  │
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ exam_builder_service.py
│  │  ├─ grading_service.py
│  │  ├─ result_input_service.py
│  │  ├─ analysis_service.py
│  │  ├─ question_service.py
│  │  ├─ csv_import_service.py
│  │  └─ pdf_export_service.py
│  │
│  ├─ repositories/
│  │  ├─ __init__.py
│  │  ├─ db.py
│  │  ├─ student_repository.py
│  │  ├─ question_repository.py
│  │  ├─ exam_repository.py
│  │  ├─ exam_question_repository.py
│  │  ├─ result_repository.py
│  │  └─ answer_record_repository.py
│  │
│  └─ utils/
│     ├─ __init__.py
│     ├─ constants.py
│     ├─ validators.py
│     ├─ answer_normalizer.py
│     └─ chart_util.py
```

### 7.1 주요 폴더 설명

| 폴더 | 설명 |
|---|---|
| app/models | 학생, 문제, 시험, 답안, 결과 등 데이터 객체를 정의한다. |
| app/views | PySide6 기반 화면 UI를 구성한다. |
| app/controllers | View에서 발생한 이벤트를 받아 Service 또는 Repository로 전달한다. |
| app/services | 시험지 생성, 답안 비교, 자동 채점, 결과 분석, PDF 출력 등 핵심 로직을 처리한다. |
| app/repositories | SQLite 데이터베이스 접근과 CRUD 작업을 담당한다. |
| app/utils | 답안 정규화, 상수, 차트 등 공통 유틸리티 기능을 제공한다. |
| data | 로컬 데이터베이스 및 CSV 데이터 파일을 저장한다. |
| docs | 요구사항, 설계, 테스트, 위험관리, 구현 일정, 의사결정 문서를 저장한다. |

---

## 8. 데이터베이스 구조

본 시스템은 SQLite를 사용하여 데이터를 로컬에 저장한다. 데이터베이스 파일은 실행 시 `data/teacher_exam.db` 경로에 생성된다. 데이터베이스 초기화는 `app/repositories/db.py`의 `init_database()` 함수에서 수행된다.

### 8.1 students

학생 정보를 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| student_id | 학생 고유 ID |
| name | 학생 이름 |
| student_number | 학번 |
| class_name | 반 정보 |
| is_active | 활성화 여부 |
| created_at | 등록일 |

### 8.2 questions

단답형 문제은행 데이터를 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| question_id | 문제 고유 ID |
| exam_name | 관련 시험명 |
| class_name | 대상 반 |
| question_text | 문제 내용 |
| category | 문제 유형 |
| sub_category | 세부 분류 |
| difficulty | 난이도 |
| answer_text | 기준 정답 |
| acceptable_answers | 허용 답안 |
| explanation | 해설 |
| tags | 태그 |
| is_active | 활성화 여부 |
| created_at | 등록일 |

### 8.3 exams

생성된 시험지 정보를 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| exam_id | 시험 고유 ID |
| exam_name | 시험명 |
| description | 시험 설명 |
| year | 학년도 |
| semester | 학기 |
| exam_type | 시험 유형 |
| exam_date | 시험일 |
| target_class | 대상 반 |
| total_questions | 총 문항 수 |
| created_at | 생성일 |

### 8.4 exam_questions

시험지와 문제의 연결 관계를 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| exam_question_id | 시험-문제 연결 고유 ID |
| exam_id | 시험 ID |
| question_id | 문제 ID |
| question_order | 시험지 내 문항 순서 |

### 8.5 exam_results

학생별 시험 결과를 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| result_id | 결과 고유 ID |
| exam_id | 시험 ID |
| student_id | 학생 ID |
| correct_count | 정답 수 |
| wrong_count | 오답 수 |
| score | 점수 |
| accuracy | 정답률 |
| created_at | 저장일 |

### 8.6 answer_records

학생별 문항 답안 기록을 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| answer_id | 답안 기록 고유 ID |
| exam_id | 시험 ID |
| student_id | 학생 ID |
| question_id | 문제 ID |
| student_answer | 학생 답안 |
| correct_answer | 기준 정답 |
| is_correct | 정답 여부 |

---

## 9. 정답 비교 방식

본 시스템의 자동 채점은 AI 기반 의미 해석 채점이 아니라, 사전에 등록된 기준 정답 및 허용 답안과 학생 답안을 비교하는 방식이다.

정답 비교는 `app/utils/answer_normalizer.py`의 `AnswerNormalizer`에서 처리한다.

### 9.1 답안 정규화 규칙

학생 답안과 정답을 비교하기 전에 다음 처리를 수행한다.

| 처리 | 설명 |
|---|---|
| 앞뒤 공백 제거 | `" went "`를 `"went"`로 변환 |
| 대소문자 통일 | `"Went"`를 `"went"`로 변환 |
| 문장부호 제거 | `"went."`를 `"went"`로 변환 |
| 연속 공백 정리 | `"passive  voice"`를 `"passive voice"`로 변환 |

### 9.2 정답 판정 순서

1. 학생 답안을 정규화한다.
2. 기준 정답을 정규화한다.
3. 학생 답안과 기준 정답이 같으면 정답으로 처리한다.
4. 기준 정답과 다르면 허용 답안 목록을 확인한다.
5. 허용 답안 중 하나와 일치하면 정답으로 처리한다.
6. 기준 정답과 허용 답안 모두 일치하지 않으면 오답으로 처리한다.

### 9.3 예시

| 학생 답안 | 기준 정답 | 허용 답안 | 판정 |
|---|---|---|---|
| Went. | went | 없음 | 정답 |
| passive voice | passive voice | 없음 | 정답 |
| the | to | to, the | 정답 |
| go | went | 없음 | 오답 |

### 9.4 채점 결과 계산

정답 비교 결과를 바탕으로 다음 값을 계산한다.

| 항목 | 설명 |
|---|---|
| 정답 수 | 정답으로 판정된 문항 수 |
| 오답 수 | 전체 문항 수에서 정답 수를 뺀 값 |
| 점수 | `(정답 수 / 전체 문항 수) * 100` |
| 정답률 | `정답 수 / 전체 문항 수` |

계산된 결과는 `exam_results` 테이블에 저장되며, 문항별 답안 기록은 `answer_records` 테이블에 저장된다.

---

## 10. 실행 방법

### 10.1 패키지 설치

```bash
pip install -r requirements.txt
```

### 10.2 프로그램 실행

```bash
python main.py
```

---

## 11. 사용 흐름

1. 학생 관리 화면에서 학생 정보를 등록한다.
2. 문제은행 관리 화면에서 단답형 문제를 등록한다.
3. 시험지 생성 화면에서 조건을 설정하거나 문제를 직접 선택한다.
4. 생성된 시험지를 저장하고 필요하면 PDF로 출력한다.
5. 시험 후 결과 입력 화면에서 학생 답안을 입력하거나 CSV 파일을 불러온다.
6. 자동 채점을 실행하여 학생별 결과를 저장한다.
7. 대시보드와 결과 분석 화면에서 시험 결과를 확인한다.

---

## 12. 브랜치 전략

본 프로젝트는 기능별 개발과 통합을 분리하기 위해 Git 브랜치를 나누어 사용한다.

### 12.1 브랜치 구성

| 브랜치 | 역할 |
|---|---|
| main | 최종 안정 버전 관리 |
| develop | 개발 통합 브랜치 |
| feature/core | 모델, 데이터베이스, Repository, Service 등 핵심 로직 개발 |
| feature/ui | PySide6 기반 화면 및 사용자 인터페이스 개발 |
| feature/integration | Core 기능과 UI 기능을 통합하고 전체 흐름을 연결 |
| feature/docs | 문서 작성 및 정리 |

### 12.2 개발 흐름

```text
feature/core
        \
         \
feature/ui ----> feature/integration ----> develop ----> main
         /
        /
feature/docs
```

### 12.3 브랜치별 작업 내용

| 브랜치 | 주요 작업 |
|---|---|
| feature/core | 학생, 문제, 시험, 결과 모델 작성 및 DB 저장 로직 구현 |
| feature/ui | 학생 관리, 문제은행, 시험지 생성, 결과 입력, 분석 화면 구현 |
| feature/integration | UI와 Controller, Service, Repository 연결 및 실제 동작 통합 |
| feature/docs | README, 요구사항, 설계, 테스트, 위험관리, 구현 일정, 의사결정 문서 작성 |
| develop | 기능 브랜치 병합 후 전체 테스트 |
| main | 제출 또는 배포 가능한 최종 버전 유지 |

### 12.4 통합 브랜치 사용 이유

`feature/integration` 브랜치는 단순히 코드를 합치는 용도가 아니라, 실제 사용 흐름이 정상적으로 이어지는지 확인하는 브랜치이다.

예를 들어 다음 흐름을 통합 브랜치에서 확인한다.

```text
학생 등록
  → 문제 등록
  → 시험지 생성
  → 시험지 저장
  → 답안 입력
  → 자동 채점
  → 결과 분석
  → 대시보드 표시
```

이를 통해 Core 로직과 UI 화면이 따로 동작하는 수준을 넘어, 실제 교사가 사용할 수 있는 하나의 프로그램으로 연결되는지를 검증한다.

---

## 13. 제약사항

- 본 시스템은 로컬 데스크톱 앱이며 웹 서비스가 아니다.
- 모든 데이터는 사용자 PC의 SQLite 데이터베이스에 저장된다.
- 외부 서버, 외부 API, 외부 LLM을 사용하지 않는다.
- 자동 채점은 의미 기반 AI 채점이 아니라 기준 정답 및 허용 답안 비교 방식이다.
- 주관식 서술형 답안의 의미 해석이나 부분 점수 처리는 지원하지 않는다.
- CSV 답안 입력 시 학생 번호와 등록 학생 정보가 일치해야 한다.
- PDF 출력 품질은 실행 환경의 한글 폰트 설치 상태에 영향을 받을 수 있다.

