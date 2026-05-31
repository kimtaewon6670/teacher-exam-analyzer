# 4.1 전체 아키텍처

프로젝트는 PySide6 기반 데스크톱 애플리케이션이며, SQLite를 로컬 데이터베이스로 사용한다.

전체 흐름은 다음과 같다.

View → Controller → Service / Repository → SQLite

## 주요 구성

### View

PySide6 기반 UI 화면을 담당한다.

역할:

- 화면 표시
- 사용자 입력값 제공
- 버튼, 콤보박스, 테이블 등 UI 구성
- Controller가 사용할 수 있는 메서드 제공

### Controller

View와 Core 로직을 연결한다.

역할:

- 버튼 클릭 이벤트 연결
- 사용자 입력값 수집
- Service 또는 Repository 호출
- 처리 결과를 다시 View에 전달

### Service

시험지 생성, 채점, 분석 등 핵심 비즈니스 로직을 처리한다.

역할:

- 조건 기반 문제 추출
- 학생 답안 처리
- 자동 채점
- 결과 분석
- PDF 출력 데이터 처리

### Repository

SQLite 데이터베이스 접근을 담당한다.

역할:

- 학생, 문제, 시험, 결과 데이터 저장
- 조회, 수정, 삭제 처리
- SQL 로직 관리

### Model

학생, 문제, 시험, 답안, 결과 데이터 구조를 정의한다.

### SQLite

로컬 데이터 저장소로 사용된다. 별도 서버 없이 학생 정보, 문제은행, 시험지, 답안, 결과 데이터를 저장한다.

## 전체 처리 흐름

사용자가 View에서 버튼을 클릭하거나 데이터를 입력하면 Controller가 이를 받아 Service 또는 Repository에 전달한다. Service는 필요한 비즈니스 로직을 처리하고, Repository는 SQLite 데이터베이스에 접근하여 데이터를 저장하거나 조회한다. 처리 결과는 다시 Controller를 통해 View에 전달되어 화면에 표시된다.

## 구조적 특징

- View는 DB 또는 Repository를 직접 호출하지 않는다.
- Controller는 View와 Core 로직 사이의 연결 역할을 한다.
- Service는 핵심 기능 로직을 담당한다.
- Repository는 데이터베이스 접근만 담당한다.
- SQLite는 로컬 환경에서 데이터를 저장한다.
