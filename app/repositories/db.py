import sqlite3
import os
from datetime import datetime
from pathlib import Path

# 데이터베이스 파일 경로
DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'teacher_exam.db'


def get_db_connection():
    """
    SQLite 데이터베이스 연결을 반환한다.
    
    Returns:
        sqlite3.Connection: 데이터베이스 연결 객체
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리처럼 접근 가능하게
    return conn


def init_database():
    """
    데이터베이스가 없으면 생성하고 필요한 테이블을 생성한다.
    """
    # 데이터 폴더가 없으면 생성
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # students 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                student_number TEXT UNIQUE NOT NULL,
                class_name TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # questions 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                category TEXT NOT NULL,
                sub_category TEXT,
                difficulty TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                acceptable_answers TEXT,
                explanation TEXT,
                tags TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # exams 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_name TEXT NOT NULL,
                description TEXT,
                exam_date DATE,
                target_class TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # exam_questions 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_questions (
                exam_question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                question_order INTEGER NOT NULL,
                FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE
            )
        ''')
        
        # exam_results 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                wrong_count INTEGER NOT NULL,
                score REAL NOT NULL,
                accuracy REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            )
        ''')
        
        # answer_records 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answer_records (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                student_answer TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        print(f"✓ Database initialized successfully at {DB_PATH}")
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def close_db_connection(conn):
    """
    데이터베이스 연결을 종료한다.
    
    Args:
        conn (sqlite3.Connection): 데이터베이스 연결 객체
    """
    if conn:
        conn.close()
