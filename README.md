# Teacher Exam Analyzer

교사용 단답형 문제은행 기반 시험지 생성 및 결과 분석 데스크톱 앱

---

## 1. 프로젝트 개요

Teacher Exam Analyzer는 선생님을 위한 단답형 문제은행 기반 시험지 생성 및 결과 분석 데스크톱 앱이다.

선생님은 어휘, 문법, 독해 등 영어 학습 영역별 단답형 문제를 문제은행에 등록하고, 문제 유형, 세부 분류, 난이도, 태그 등의 조건을 활용하여 시험지를 생성할 수 있다. 생성된 시험지는 저장하거나 PDF 형태로 출력하여 학생들에게 배부할 수 있다.

학생들은 앱에서 직접 시험을 응시하는 것이 아니라, 선생님이 생성한 시험지를 통해 시험을 치른다. 시험이 끝난 후 선생님은 학생별 답안 또는 문항별 정답 여부를 직접 입력하거나 CSV 파일로 불러와 시험 결과를 저장할 수 있다.

시스템은 입력된 학생 답안을 기준 정답 및 허용 답안과 비교하여 정답 여부를 판단한다. 이때 대소문자, 앞뒤 공백, 간단한 문장부호는 정규화하여 처리한다. 본 시스템은 AI 기반 의미 해석 채점이 아니라, 선생님이 사전에 등록한 기준 정답과 허용 답안을 기반으로 비교하는 방식으로 동작한다.

저장된 시험 결과를 바탕으로 반 전체 평균 점수, 전체 정답률, 문항별 정답률, 문제 유형별 정답률, 세부 분류별 정답률, 난이도별 정답률 등을 분석한다. 분석 결과는 표와 그래프 형태로 시각화하여 선생님이 반 전체의 성취도와 취약 영역을 쉽게 확인할 수 있도록 한다.

본 프로젝트는 웹 서비스가 아닌 로컬 데스크톱 애플리케이션으로 구현한다. 모든 데이터는 사용자의 PC 내부 SQLite 데이터베이스에 저장되며, 외부 서버나 외부 LLM API를 사용하지 않는다.

---

## 2. 기획 의도

본 프로젝트는 선생님이 보유한 단답형 문제를 체계적으로 관리하고, 원하는 조건에 따라 시험지를 쉽게 생성하며, 시험 결과를 데이터 기반으로 분석할 수 있도록 돕기 위해 기획되었다.

일반적으로 선생님은 수업이나 시험에 사용할 문제를 한글 문서, 엑셀 파일, 개인 자료 폴더 등에 나누어 관리하는 경우가 많다. 이 경우 시험지를 만들 때 문제를 직접 찾고, 복사하고, 유형과 난이도를 맞추는 과정이 반복적으로 발생한다.

또한 시험이 끝난 뒤에는 총점이나 평균 점수 정도만 확인하는 경우가 많아, 학생들이 어떤 유형의 문제에서 어려움을 겪었는지 구체적으로 파악하기 어렵다.

이에 본 시스템은 문제를 문제은행 형태로 등록하고, 문제 유형, 세부 분류, 난이도, 태그를 기준으로 시험지를 생성할 수 있도록 한다. 선생님은 직접 문제를 선택하거나 조건을 설정하여 문제를 자동으로 추출할 수 있다.

시험 결과 입력 후에는 문항별 정답률, 문제 유형별 정답률, 세부 분류별 정답률, 난이도별 정답률, 반 평균 점수 등을 계산하고 이를 표와 그래프로 시각화한다. 이를 통해 선생님은 단순 점수보다 구체적인 기준으로 반 전체의 학습 상태와 취약한 문제 유형을 확인할 수 있다.

---

## 3. 주요 기능

### 3.1 학생 관리 기능

- 학생 등록
- 학생 목록 조회
- 학생 정보 수정
- 학생 비활성화
- 비활성화된 학생의 기존 시험 기록 보존

---

### 3.2 문제은행 관리 기능

- 단답형 문제 등록
- 문제 유형 설정
  - 어휘
  - 문법
  - 독해
- 세부 분류 설정
  - 예: 시제, 수동태, 관계대명사, 빈칸 추론 등
- 난이도 설정
  - 쉬움
  - 보통
  - 어려움
- 기준 정답 입력
- 허용 답안 입력
- 해설 입력
- 태그 입력
- 문제 목록 조회
- 문제 검색 및 필터링
- 문제 수정
- 문제 비활성화

---

### 3.3 시험지 생성 기능

- 시험지 생성 조건 설정
- 유형별 문항 수 설정
  - 예: 어휘 5문항, 문법 5문항, 독해 5문항
- 난이도 비율 설정
  - 예: 쉬움 30%, 보통 50%, 어려움 20%
- 태그 기반 문제 추출
- 조건 기반 문제 자동 추출
- 문제 직접 선택
- 시험 정보 입력
  - 시험명
  - 시험 설명
  - 시험 일자
  - 대상 반
- 시험지 미리보기
- 시험지 저장

---

### 3.4 시험지 저장 및 출력 기능

- 생성된 시험지 저장
- PDF 형태로 시험지 출력
- 저장된 시험지 목록 조회
- 시험지 상세 조회

---

### 3.5 시험 결과 입력 기능

- 시험 선택
- 반/학생 선
- 학생 별 답안 입
- CSV 답안 파일 불러오기
- 입력값 검증
- 답안 저장 및 자동 채점 실행

---

### 3.6 정답 비교 및 점수 계산 기능

- 학생 답안 정규화
  - 앞뒤 공백 제거
  - 대소문자 통일
  - 간단한 문장부호 제거
- 기준 정답 비교
- 허용 답안 비교
- 문항별 정답 여부 판단
- 학생별 정답 수 계산
- 학생별 오답 수 계산
- 학생별 점수 계산
- 학생별 정답률 계산
- 문항별 결과 확인

---

### 3.7 시험 결과 저장 기능

- 학생별 시험 결과 저장
- 문항별 답안 기록 저장
- 기준 정답 및 학생 답안 저장
- 시험별 결과 조회
- 학생별 시험 기록 조회
- 학생이나 문제가 비활성화되어도 기존 시험 기록 보존

---

### 3.8 시험 결과 분석 기능

- 반 전체 평균 점수 분석
- 전체 정답률 분석
- 문항별 정답률 및 오답률 분석
- 문제 유형별 정답률 분석
- 세부 분류별 정답률 분석
- 난이도별 정답률 분석
- 반 전체 취약 유형 확인

---

### 3.9 시각화 대시보드 기능

- 시험 요약 정보 카드 표시
  - 응시 학생 수
  - 총 문항 수
  - 반 평균 점수
  - 전체 정답률
- 문항별 정답률 그래프
- 유형별 정답률 그래프
- 세부 분류별 정답률 그래프
- 난이도별 정답률 그래프
- 학생별 결과 표
  - 학생 이름
  - 점수
  - 정답 수
  - 오답 수
  - 정답률

---

### 3.10 예외 처리 기능

- 필수 입력값 검증
- 문제 부족 예외 처리
- CSV 형식 오류 처리
- 데이터 조회 실패 처리
- 저장 오류 처리
- 오류 발생 시 안내 메시지 제공

---

## 4. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python |
| UI / View | PySide6 |
| Database | SQLite |
| Data Processing / Analysis | pandas |
| Visualization | matplotlib |
| PDF Export | reportlab |
| Architecture | MVC Pattern |
| Version Control | Git / GitHub |

---

## 5. 기술 스택 선정 이유

### 5.1 Python

Python은 데이터 처리, 파일 입출력, 데스크톱 앱 개발, 통계 분석을 모두 구현할 수 있는 언어이다. 본 프로젝트는 시험 결과 데이터 처리와 분석 기능이 중요하므로 Python을 기반 언어로 사용한다.

### 5.2 PySide6

PySide6는 Python 기반 데스크톱 GUI 라이브러리이다. 학생 관리, 문제은행 관리, 시험지 생성, 결과 입력, 결과 분석 화면을 데스크톱 앱 형태로 구현하기 위해 사용한다.

### 5.3 SQLite

SQLite는 별도 서버 설치 없이 로컬 파일 기반으로 동작하는 데이터베이스이다. 본 프로젝트는 외부 서버 없이 로컬 PC에서 실행되는 데스크톱 앱이므로 SQLite를 사용하여 학생 정보, 문제 정보, 시험지 정보, 답안 기록, 시험 결과 데이터를 저장한다.

### 5.4 pandas

pandas는 표 형태의 데이터를 처리하고 분석하는 데 적합하다. 시험 결과를 기반으로 반 평균 점수, 정답률, 문항별 정답률, 유형별 정답률, 난이도별 정답률을 계산하기 위해 사용한다.

### 5.5 matplotlib

matplotlib는 Python 기반 그래프 시각화 라이브러리이다. 문항별 정답률, 유형별 정답률, 세부 분류별 정답률, 난이도별 정답률을 그래프로 시각화하기 위해 사용한다.

### 5.6 reportlab

reportlab은 Python에서 PDF 파일을 생성할 수 있는 라이브러리이다. 생성된 시험지를 PDF 형태로 저장하거나 출력하기 위해 사용한다.

---

## 6. 시스템 구조

본 프로젝트는 MVC 구조를 기반으로 개발하며, 화면 표시, 사용자 요청 처리, 핵심 로직, 데이터베이스 접근 역할을 분리한다.

```text
View → Controller → Service → Repository → SQLite DB
```

### 6.1 MVC 및 계층 구성

| 구성요소 | 역할 |
|---|---|
| View | PySide6 기반 화면 표시 및 사용자 입력 처리 |
| Controller | View에서 발생한 사용자 요청 처리 및 기능 흐름 제어 |
| Model | 학생, 문제, 시험지, 답안, 결과 데이터 구조 관리 |
| Service | 문제 관리, 시험지 생성, 정답 비교, 결과 분석, PDF 출력 등 핵심 로직 처리 |
| Repository | SQLite 데이터베이스 접근 및 CRUD 처리 |

### 6.2 처리 흐름

사용자가 View에서 버튼 클릭이나 입력을 수행하면 Controller가 요청을 받아 Service를 호출한다. Service는 문제 등록, 시험지 생성, 정답 비교, 결과 분석 등의 핵심 로직을 처리하고, 필요한 데이터 조회와 저장은 Repository를 통해 SQLite DB에서 수행한다.

---

## 7. 프로젝트 폴더 구조

```text
teacher-exam-analyzer/
│
├─ main.py
├─ requirements.txt
├─ README.md
│
├─ app/
│  ├─ models/
│  │  ├─ student_model.py
│  │  ├─ question_model.py
│  │  ├─ exam_model.py
│  │  ├─ exam_question_model.py
│  │  ├─ exam_result_model.py
│  │  └─ answer_record_model.py
│  │
│  ├─ views/
│  │  ├─ main_window.py
│  │  ├─ dashboard_view.py
│  │  ├─ student_manage_view.py
│  │  ├─ question_bank_view.py
│  │  ├─ exam_builder_view.py
│  │  ├─ result_input_view.py
│  │  ├─ analysis_view.py
│  │  └─ report_view.py
│  │
│  ├─ controllers/
│  │  ├─ main_controller.py
│  │  ├─ student_controller.py
│  │  ├─ question_controller.py
│  │  ├─ exam_controller.py
│  │  ├─ result_controller.py
│  │  └─ analysis_controller.py
│  │
│  ├─ services/
│  │  ├─ question_service.py
│  │  ├─ exam_builder_service.py
│  │  ├─ grading_service.py
│  │  ├─ analysis_service.py
│  │  ├─ csv_import_service.py
│  │  └─ pdf_export_service.py
│  │
│  ├─ repositories/
│  │  ├─ db.py
│  │  ├─ student_repository.py
│  │  ├─ question_repository.py
│  │  ├─ exam_repository.py
│  │  ├─ result_repository.py
│  │  └─ answer_record_repository.py
│  │
│  └─ utils/
│     ├─ constants.py
│     ├─ validators.py
│     ├─ answer_normalizer.py
│     └─ chart_util.py
│
├─ data/
│  └─ .gitkeep
│
└─ docs/
   ├─ images/
   ├─ requirements.md
   ├─ erd.md
   ├─ usecase.md
   ├─ sequence.md
   └─ test_case.md
```

---

## 8. 데이터베이스 주요 테이블

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

---

### 8.2 questions

단답형 문제은행 데이터를 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| question_id | 문제 고유 ID |
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

---

### 8.3 exams

시험지 정보를 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| exam_id | 시험 고유 ID |
| exam_name | 시험명 |
| description | 시험 설명 |
| exam_date | 시험 일자 |
| target_class | 대상 반 |
| total_questions | 총 문항 수 |
| created_at | 생성일 |

---

### 8.4 exam_questions

시험지에 포함된 문제 목록을 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| exam_question_id | 시험 문항 고유 ID |
| exam_id | 시험 ID |
| question_id | 문제 ID |
| question_order | 문항 순서 |

---

### 8.5 exam_results

학생별 시험 결과 요약 정보를 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| result_id | 시험 결과 ID |
| exam_id | 시험 ID |
| student_id | 학생 ID |
| correct_count | 정답 수 |
| wrong_count | 오답 수 |
| score | 점수 |
| accuracy | 정답률 |
| created_at | 저장일 |

---

### 8.6 answer_records

학생별 문항 답안 기록을 저장하는 테이블이다.

| 컬럼 | 설명 |
|---|---|
| answer_id | 답안 기록 ID |
| exam_id | 시험 ID |
| student_id | 학생 ID |
| question_id | 문제 ID |
| student_answer | 학생 답안 |
| correct_answer | 기준 정답 |
| is_correct | 정답 여부 |

---

## 9. 정답 비교 방식

본 시스템은 AI 기반 의미 해석 채점을 사용하지 않는다. 학생 답안은 선생님이 사전에 등록한 기준 정답 및 허용 답안과 비교하여 정답 여부를 판단한다.

### 9.1 답안 정규화 기준

정답 비교 전 다음 기준을 적용한다.

- 앞뒤 공백 제거
- 대소문자 통일
- 간단한 문장부호 제거
- 연속 공백 정리

### 9.2 정답 처리 예시

| 기준 정답 | 허용 답안 | 학생 답안 | 처리 결과 |
|---|---|---|---|
| went | Went, went. | Went. | 정답 |
| 관계대명사 | 관계 대명사 | 관계 대명사 | 정답 |
| passive voice | Passive Voice | passive voice | 정답 |

---

## 10. 실행 방법

### 10.1 저장소 클론

```bash
git clone https://github.com/kimtaewon6670/teacher-exam-analyzer.git
cd teacher-exam-analyzer
```

---

### 10.2 가상환경 생성

```bash
python -m venv venv
```

---

### 10.3 가상환경 실행

Windows PowerShell 기준:

```bash
.\venv\Scripts\activate
```

---

### 10.4 패키지 설치

```bash
pip install -r requirements.txt
```

---

### 10.5 프로그램 실행

```bash
python main.py
```

---

## 11. requirements.txt

```txt
PySide6
pandas
matplotlib
reportlab
```

---

## 12. 브랜치 전략

| 브랜치 | 용도 |
|---|---|
| main | 최종 제출용 안정 버전 |
| develop | 개발 통합 브랜치 |
| feature/ui | PySide6 화면 및 View 작업 |
| feature/core | DB, Controller, Service, 분석 로직 작업 |
| feature/docs | 요구사항, README, ERD, 테스트 문서 작업 |

---

## 13. 역할 분담

| 담당 | 역할 |
|---|---|
| UI 담당 | PySide6 화면 구현, 사이드바, 대시보드, 학생 관리 화면, 문제은행 화면, 시험지 생성 화면, 결과 입력 화면, 분석 화면 구현 |
| Core 담당 | SQLite DB 설계, 문제 CRUD, 학생 CRUD, 시험지 생성 로직, 정답 비교, 점수 계산, 결과 분석 로직 구현 |
| Docs 담당 | 요구사항 명세서, ERD, 유스케이스, 시퀀스 다이어그램, 테스트 케이스 문서 작성 |

---

## 14. 개발 일정

| 주차 | 목표 |
|---|---|
| 1주차 | 프로젝트 구조 생성, DB 설계, 학생 관리 및 문제은행 관리 기능 구현 |
| 2주차 | 시험지 생성, PDF 출력, 결과 입력, 정답 비교 및 점수 계산 기능 구현 |
| 3주차 | 결과 분석, 시각화 대시보드, CSV 불러오기, 테스트 및 문서 정리 |

---

## 15. 제약사항

- 웹 서비스가 아닌 로컬 데스크톱 앱으로 구현한다.
- 학생이 앱에서 직접 시험을 응시하는 구조는 제외한다.
- 모든 데이터는 SQLite 로컬 데이터베이스에 저장한다.
- 외부 서버를 사용하지 않는다.
- ChatGPT, Gemini, Claude 등 외부 LLM API를 사용하지 않는다.
- AI 기반 의미 해석 채점을 사용하지 않는다.
- 정답 비교는 기준 정답 및 허용 답안 비교 방식으로 수행한다.
- 문제 관리, 시험지 생성, 정답 비교, 결과 분석, 시각화 로직은 모듈화하여 구현한다.

---

## 16. 프로젝트 최종 목표

본 프로젝트의 최종 목표는 선생님이 단답형 문제를 문제은행 형태로 관리하고, 원하는 조건에 따라 시험지를 생성하며, 시험 결과를 입력하여 반 전체와 학생별 학습 결과를 분석할 수 있는 로컬 데스크톱 기반 교사용 도구를 구현하는 것이다.

이를 통해 선생님은 시험지 제작 시간을 줄이고, 시험 결과를 단순 점수가 아닌 문항별, 유형별, 세부 분류별, 난이도별 데이터로 분석하여 수업 개선과 보충 지도에 활용할 수 있다.
