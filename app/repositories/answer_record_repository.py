from typing import List, Optional, Dict
from app.models.answer_record_model import AnswerRecord
from app.repositories.db import get_db_connection, close_db_connection
import sqlite3


class AnswerRecordRepository:
    """
    학생 답안 기록 데이터에 대한 CRUD 작업을 수행하는 Repository
    """
    
    @staticmethod
    def create(record: AnswerRecord) -> int:
        """
        답안 기록을 데이터베이스에 저장한다.
        
        Args:
            record (AnswerRecord): 저장할 답안 기록 객체
            
        Returns:
            int: 생성된 답안 기록의 ID
            
        Raises:
            sqlite3.Error: 데이터베이스 오류 발생 시
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO answer_records (exam_id, student_id, question_id, student_answer, correct_answer, is_correct)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (record.exam_id, record.student_id, record.question_id, record.student_answer, record.correct_answer, record.is_correct))
            
            conn.commit()
            answer_id = cursor.lastrowid
            return answer_id
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def create_batch(records: List[AnswerRecord]) -> int:
        """
        여러 답안 기록을 한 번에 데이터베이스에 저장한다.
        
        Args:
            records (List[AnswerRecord]): 저장할 답안 기록 객체 리스트
            
        Returns:
            int: 저장된 기록의 개수
            
        Raises:
            sqlite3.Error: 데이터베이스 오류 발생 시
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            data = [
                (r.exam_id, r.student_id, r.question_id, r.student_answer, r.correct_answer, r.is_correct)
                for r in records
            ]
            
            cursor.executemany('''
                INSERT INTO answer_records (exam_id, student_id, question_id, student_answer, correct_answer, is_correct)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', data)
            
            conn.commit()
            count = cursor.rowcount
            print(f"✓ {count} AnswerRecords created successfully")
            return count
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_exam_and_student(exam_id: int, student_id: int) -> List[AnswerRecord]:
        """
        특정 학생의 특정 시험 답안 기록을 조회한다.
        
        Args:
            exam_id (int): 시험 ID
            student_id (int): 학생 ID
            
        Returns:
            List[AnswerRecord]: 답안 기록 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM answer_records 
                WHERE exam_id = ? AND student_id = ? 
                ORDER BY question_id
            ''', (exam_id, student_id))
            rows = cursor.fetchall()
            records = [AnswerRecord.from_dict(dict(row)) for row in rows]
            return records
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_exam(exam_id: int) -> List[AnswerRecord]:
        """
        시험의 모든 답안 기록을 조회한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            List[AnswerRecord]: 답안 기록 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT * FROM answer_records WHERE exam_id = ? ORDER BY student_id, question_id',
                (exam_id,)
            )
            rows = cursor.fetchall()
            records = [AnswerRecord.from_dict(dict(row)) for row in rows]
            return records
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_question(question_id: int) -> List[AnswerRecord]:
        """
        특정 문제의 모든 답안 기록을 조회한다.
        
        Args:
            question_id (int): 문제 ID
            
        Returns:
            List[AnswerRecord]: 답안 기록 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT * FROM answer_records WHERE question_id = ? ORDER BY exam_id, student_id',
                (question_id,)
            )
            rows = cursor.fetchall()
            records = [AnswerRecord.from_dict(dict(row)) for row in rows]
            return records
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def get_question_accuracy(question_id: int) -> float:
        """
        특정 문제의 정답률을 반환한다.
        
        Args:
            question_id (int): 문제 ID
            
        Returns:
            float: 정답률 (0.0 ~ 1.0)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT AVG(is_correct) FROM answer_records WHERE question_id = ?',
                (question_id,)
            )
            result = cursor.fetchone()[0]
            return result if result else 0.0
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def count_correct_by_exam_and_student(exam_id: int, student_id: int) -> int:
        """
        특정 학생의 시험 정답 개수를 반환한다.
        
        Args:
            exam_id (int): 시험 ID
            student_id (int): 학생 ID
            
        Returns:
            int: 정답 개수
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT COUNT(*) FROM answer_records WHERE exam_id = ? AND student_id = ? AND is_correct = 1',
                (exam_id, student_id)
            )
            count = cursor.fetchone()[0]
            return count
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def count_wrong_by_exam_and_student(exam_id: int, student_id: int) -> int:
        """
        특정 학생의 시험 오답 개수를 반환한다.
        
        Args:
            exam_id (int): 시험 ID
            student_id (int): 학생 ID
            
        Returns:
            int: 오답 개수
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT COUNT(*) FROM answer_records WHERE exam_id = ? AND student_id = ? AND is_correct = 0',
                (exam_id, student_id)
            )
            count = cursor.fetchone()[0]
            return count
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
