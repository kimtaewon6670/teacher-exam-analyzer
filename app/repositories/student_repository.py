from typing import List, Optional
from app.models.student_model import Student
from app.repositories.db import get_db_connection, close_db_connection
import sqlite3


class StudentRepository:
    """
    학생 데이터에 대한 CRUD 작업을 수행하는 Repository
    """
    
    @staticmethod
    def create(student: Student) -> int:
        """
        새로운 학생을 데이터베이스에 등록한다.
        
        Args:
            student (Student): 등록할 학생 객체
            
        Returns:
            int: 생성된 학생의 ID
            
        Raises:
            sqlite3.IntegrityError: 학번이 중복되거나 필수 정보가 없을 때
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO students (name, student_number, class_name, is_active)
                VALUES (?, ?, ?, ?)
            ''', (student.name, student.student_number, student.class_name, student.is_active))
            
            conn.commit()
            student_id = cursor.lastrowid
            print(f"✓ Student created successfully (ID: {student_id})")
            return student_id
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            print(f"✗ Integrity error: {e}")
            raise
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read(student_id: int) -> Optional[Student]:
        """
        학생 ID로 학생 정보를 조회한다.
        
        Args:
            student_id (int): 학생 ID
            
        Returns:
            Optional[Student]: 조회된 학생 객체, 없으면 None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
            row = cursor.fetchone()
            
            if row:
                return Student.from_dict(dict(row))
            return None
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_number(student_number: str) -> Optional[Student]:
        """
        학번으로 학생 정보를 조회한다.
        
        Args:
            student_number (str): 학번
            
        Returns:
            Optional[Student]: 조회된 학생 객체, 없으면 None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM students WHERE student_number = ?', (student_number,))
            row = cursor.fetchone()
            
            if row:
                return Student.from_dict(dict(row))
            return None
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_all(active_only: bool = True) -> List[Student]:
        """
        모든 학생 정보를 조회한다.
        
        Args:
            active_only (bool): True일 경우 활성 학생만 조회
            
        Returns:
            List[Student]: 학생 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute('SELECT * FROM students WHERE is_active = 1 ORDER BY created_at DESC')
            else:
                cursor.execute('SELECT * FROM students ORDER BY created_at DESC')
            
            rows = cursor.fetchall()
            students = [Student.from_dict(dict(row)) for row in rows]
            return students
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_class(class_name: str, active_only: bool = True) -> List[Student]:
        """
        반 이름으로 학생들을 조회한다.
        
        Args:
            class_name (str): 반 이름
            active_only (bool): True일 경우 활성 학생만 조회
            
        Returns:
            List[Student]: 학생 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute(
                    'SELECT * FROM students WHERE class_name = ? AND is_active = 1 ORDER BY student_number',
                    (class_name,)
                )
            else:
                cursor.execute(
                    'SELECT * FROM students WHERE class_name = ? ORDER BY student_number',
                    (class_name,)
                )
            
            rows = cursor.fetchall()
            students = [Student.from_dict(dict(row)) for row in rows]
            return students
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def update(student: Student) -> bool:
        """
        학생 정보를 업데이트한다.
        
        Args:
            student (Student): 업데이트할 학생 객체 (student_id 필수)
            
        Returns:
            bool: 성공 여부
        """
        if not student.student_id:
            print("✗ student_id is required for update")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE students
                SET name = ?, student_number = ?, class_name = ?, is_active = ?
                WHERE student_id = ?
            ''', (student.name, student.student_number, student.class_name, student.is_active, student.student_id))
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"✓ Student updated successfully (ID: {student.student_id})")
                return True
            else:
                print(f"✗ No student found with ID: {student.student_id}")
                return False
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def deactivate(student_id: int) -> bool:
        """
        학생을 비활성화한다 (삭제하지 않고 비활성 처리).
        
        Args:
            student_id (int): 학생 ID
            
        Returns:
            bool: 성공 여부
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE students SET is_active = 0 WHERE student_id = ?',
                (student_id,)
            )
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"✓ Student deactivated successfully (ID: {student_id})")
                return True
            else:
                print(f"✗ No student found with ID: {student_id}")
                return False
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def activate(student_id: int) -> bool:
        """
        비활성화된 학생을 다시 활성화한다.
        
        Args:
            student_id (int): 학생 ID
            
        Returns:
            bool: 성공 여부
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE students SET is_active = 1 WHERE student_id = ?',
                (student_id,)
            )
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"✓ Student activated successfully (ID: {student_id})")
                return True
            else:
                print(f"✗ No student found with ID: {student_id}")
                return False
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def delete(student_id: int) -> bool:
        """
        학생을 데이터베이스에서 삭제한다.
        주의: 시험 기록이 있으면 삭제되지 않을 수 있다 (외래키 제약 조건).
        일반적으로 deactivate()를 사용하는 것이 권장된다.
        
        Args:
            student_id (int): 학생 ID
            
        Returns:
            bool: 성공 여부
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"✓ Student deleted successfully (ID: {student_id})")
                return True
            else:
                print(f"✗ No student found with ID: {student_id}")
                return False
                
        except sqlite3.IntegrityError:
            conn.rollback()
            print(f"✗ Cannot delete student with ID {student_id}: Has related exam records")
            return False
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
