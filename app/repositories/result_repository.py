from typing import List, Optional
from app.models.exam_result_model import ExamResult
from app.repositories.db import get_db_connection, close_db_connection
import sqlite3


class ResultRepository:
    """
    시험 결과 데이터에 대한 CRUD 작업을 수행하는 Repository
    """
    
    @staticmethod
    def create(result: ExamResult) -> int:
        """
        시험 결과를 데이터베이스에 저장한다.
        
        Args:
            result (ExamResult): 저장할 시험 결과 객체
            
        Returns:
            int: 생성된 결과의 ID
            
        Raises:
            sqlite3.Error: 데이터베이스 오류 발생 시
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO exam_results (exam_id, student_id, correct_count, wrong_count, score, accuracy)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (result.exam_id, result.student_id, result.correct_count, result.wrong_count, result.score, result.accuracy))
            
            conn.commit()
            result_id = cursor.lastrowid
            print(f"✓ ExamResult created successfully (ID: {result_id})")
            return result_id
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_exam_and_student(exam_id: int, student_id: int) -> Optional[ExamResult]:
        """
        특정 학생의 시험 결과를 조회한다.
        
        Args:
            exam_id (int): 시험 ID
            student_id (int): 학생 ID
            
        Returns:
            Optional[ExamResult]: 조회된 시험 결과 객체, 없으면 None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT * FROM exam_results WHERE exam_id = ? AND student_id = ?',
                (exam_id, student_id)
            )
            row = cursor.fetchone()
            
            if row:
                return ExamResult.from_dict(dict(row))
            return None
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_exam(exam_id: int) -> List[ExamResult]:
        """
        시험의 모든 학생 결과를 조회한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            List[ExamResult]: 시험 결과 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT * FROM exam_results WHERE exam_id = ? ORDER BY score DESC',
                (exam_id,)
            )
            rows = cursor.fetchall()
            results = [ExamResult.from_dict(dict(row)) for row in rows]
            return results
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_student(student_id: int) -> List[ExamResult]:
        """
        학생의 모든 시험 결과를 조회한다.
        
        Args:
            student_id (int): 학생 ID
            
        Returns:
            List[ExamResult]: 시험 결과 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT * FROM exam_results WHERE student_id = ? ORDER BY created_at DESC',
                (student_id,)
            )
            rows = cursor.fetchall()
            results = [ExamResult.from_dict(dict(row)) for row in rows]
            return results
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def get_exam_average_score(exam_id: int) -> float:
        """
        시험의 평균 점수를 반환한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            float: 평균 점수 (응시자가 없으면 0.0)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT AVG(score) FROM exam_results WHERE exam_id = ?', (exam_id,))
            result = cursor.fetchone()[0]
            return result if result else 0.0
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def get_exam_average_accuracy(exam_id: int) -> float:
        """
        시험의 평균 정답률을 반환한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            float: 평균 정답률 (응시자가 없으면 0.0)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT AVG(accuracy) FROM exam_results WHERE exam_id = ?', (exam_id,))
            result = cursor.fetchone()[0]
            return result if result else 0.0
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def count_by_exam(exam_id: int) -> int:
        """
        시험의 응시자 수를 반환한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            int: 응시자 수
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM exam_results WHERE exam_id = ?', (exam_id,))
            count = cursor.fetchone()[0]
            return count
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
