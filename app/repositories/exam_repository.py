from typing import List, Optional
from app.models.exam_model import Exam
from app.repositories.db import get_db_connection, close_db_connection
import sqlite3


class ExamRepository:
    """
    시험 데이터에 대한 CRUD 작업을 수행하는 Repository
    """
    
    @staticmethod
    def create(exam: Exam) -> int:
        """
        새로운 시험을 데이터베이스에 등록한다.
        
        Args:
            exam (Exam): 등록할 시험 객체
            
        Returns:
            int: 생성된 시험의 ID
            
        Raises:
            sqlite3.Error: 데이터베이스 오류 발생 시
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO exams (
                    exam_name, description, year, semester, exam_type,
                    exam_date, target_class, total_questions
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                exam.exam_name,
                exam.description,
                exam.year,
                exam.semester,
                exam.exam_type,
                exam.exam_date,
                exam.target_class,
                exam.total_questions,
            ))
            
            conn.commit()
            exam_id = cursor.lastrowid
            print(f"✓ Exam created successfully (ID: {exam_id})")
            return exam_id
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read(exam_id: int) -> Optional[Exam]:
        """
        시험 ID로 시험 정보를 조회한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            Optional[Exam]: 조회된 시험 객체, 없으면 None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM exams WHERE exam_id = ?', (exam_id,))
            row = cursor.fetchone()
            
            if row:
                return Exam.from_dict(dict(row))
            return None
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_all() -> List[Exam]:
        """
        모든 시험 정보를 조회한다.
        
        Returns:
            List[Exam]: 시험 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM exams ORDER BY created_at DESC')
            rows = cursor.fetchall()
            exams = [Exam.from_dict(dict(row)) for row in rows]
            return exams
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_class(class_name: str) -> List[Exam]:
        """
        반 이름으로 시험들을 조회한다.
        
        Args:
            class_name (str): 반 이름
            
        Returns:
            List[Exam]: 시험 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT * FROM exams WHERE target_class = ? ORDER BY created_at DESC',
                (class_name,)
            )
            rows = cursor.fetchall()
            exams = [Exam.from_dict(dict(row)) for row in rows]
            return exams
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def update(exam: Exam) -> bool:
        """
        시험 정보를 업데이트한다.
        
        Args:
            exam (Exam): 업데이트할 시험 객체 (exam_id 필수)
            
        Returns:
            bool: 성공 여부
        """
        if not exam.exam_id:
            print("✗ exam_id is required for update")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE exams
                SET exam_name = ?, description = ?, year = ?, semester = ?, exam_type = ?,
                    exam_date = ?, target_class = ?, total_questions = ?
                WHERE exam_id = ?
            ''', (
                exam.exam_name,
                exam.description,
                exam.year,
                exam.semester,
                exam.exam_type,
                exam.exam_date,
                exam.target_class,
                exam.total_questions,
                exam.exam_id,
            ))
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"✓ Exam updated successfully (ID: {exam.exam_id})")
                return True
            else:
                print(f"✗ No exam found with ID: {exam.exam_id}")
                return False
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def delete(exam_id: int) -> bool:
        """
        시험을 데이터베이스에서 삭제한다.
        주의: 시험에 포함된 문제 기록도 함께 삭제된다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            bool: 성공 여부
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM exams WHERE exam_id = ?', (exam_id,))
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"✓ Exam deleted successfully (ID: {exam_id})")
                return True
            else:
                print(f"✗ No exam found with ID: {exam_id}")
                return False
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def count_all() -> int:
        """
        전체 시험 개수를 반환한다.
        
        Returns:
            int: 시험 개수
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM exams')
            count = cursor.fetchone()[0]
            return count
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
