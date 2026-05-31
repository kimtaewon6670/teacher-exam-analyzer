# 4.4 데이터 구조

본 프로젝트는 SQLite를 사용하여 학생, 문제, 시험, 답안, 결과 데이터를 저장한다.

## students

학생 정보를 저장하는 테이블이다.

주요 컬럼:

| 컬럼명 | 설명 |
|---|---|
| student_id | 학생 고유 ID |
| name | 학생 이름 |
| student_number | 학번 |
| class_name | 반 이름 |
| is_active | 활성화 여부 |
| created_at | 생성일 |

## questions

문제은행 데이터를 저장하는 테이블이다.

주요 컬럼:

| 컬럼명 | 설명 |
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
| created_at | 생성일 |

## exams

생성된 시험지 정보를 저장하는 테이블이다.

주요 컬럼:

| 컬럼명 | 설명 |
|---|---|
| exam_id | 시험 고유 ID |
| exam_name | 시험명 |
| description | 시험 설명 |
| year | 연도 |
| semester | 학기 |
| exam_type | 시험 구분 |
| exam_date | 시험 일자 |
| target_class | 대상 반 |
| total_questions | 총 문항 수 |
| created_at | 생성일 |

## exam_questions

시험지와 문제의 관계를 저장하는 테이블이다.

주요 컬럼:

| 컬럼명 | 설명 |
|---|---|
| exam_question_id | 시험-문제 관계 고유 ID |
| exam_id | 시험 ID |
| question_id | 문제 ID |
| question_order | 시험지 내 문제 순서 |

## exam_results

학생별 시험 결과를 저장하는 테이블이다.

주요 컬럼:

| 컬럼명 | 설명 |
|---|---|
| result_id | 결과 고유 ID |
| exam_id | 시험 ID |
| student_id | 학생 ID |
| correct_count | 정답 수 |
| wrong_count | 오답 수 |
| score | 점수 |
| accuracy | 정답률 |
| created_at | 생성일 |

## answer_records

학생의 문항별 답안 기록을 저장하는 테이블이다.

주요 컬럼:

| 컬럼명 | 설명 |
|---|---|
| answer_id | 답안 기록 고유 ID |
| exam_id | 시험 ID |
| student_id | 학생 ID |
| question_id | 문제 ID |
| student_answer | 학생 답안 |
| correct_answer | 기준 정답 |
| is_correct | 정답 여부 |

## 테이블 관계

students 1 - N exam_results

students 1 - N answer_records

exams 1 - N exam_questions

exams 1 - N exam_results

exams 1 - N answer_records

questions 1 - N exam_questions

questions 1 - N answer_records

## 데이터 흐름

1. 학생 관리 화면에서 학생 정보를 등록한다.
2. 문제은행 관리 화면에서 문제를 등록한다.
3. 시험지 생성 화면에서 문제를 선택하면 exams와 exam_questions에 저장된다.
4. 결과 입력 화면에서 학생 답안을 입력하면 answer_records에 저장된다.
5. 자동 채점 결과는 exam_results에 저장된다.
6. 결과 분석 화면과 대시보드는 exam_results와 answer_records를 기반으로 분석 결과를 표시한다.
