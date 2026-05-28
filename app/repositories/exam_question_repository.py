from typing import List, Optional
from app.models.exam_question_model import ExamQuestion
from app.repositories.db import get_db_connection, close_db_connection
import sqlite3


class ExamQuestionRepository:
    """
    시험-문제 매핑 데이터에 대한 CRUD 작업을 수행하는 Repository
    """
    
    @staticmethod
    def create(exam_question: ExamQuestion) -> int:
        """
        시험에 문제를 추가한다.
        
        Args:
            exam_question (ExamQuestion): 추가할 시험-문제 객체
            
        Returns:
            int: 생성된 시험-문제의 ID
            
        Raises:
            sqlite3.Error: 데이터베이스 오류 발생 시
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO exam_questions (exam_id, question_id, question_order)
                VALUES (?, ?, ?)
            ''', (exam_question.exam_id, exam_question.question_id, exam_question.question_order))
            
            conn.commit()
            exam_question_id = cursor.lastrowid
            print(f"ExamQuestion created successfully (ID: {exam_question_id})")
            return exam_question_id
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_exam(exam_id: int) -> List[ExamQuestion]:
        """
        시험에 포함된 모든 문제를 조회한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            List[ExamQuestion]: 시험-문제 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT * FROM exam_questions WHERE exam_id = ? ORDER BY question_order',
                (exam_id,)
            )
            rows = cursor.fetchall()
            exam_questions = [ExamQuestion.from_dict(dict(row)) for row in rows]
            return exam_questions
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)

    @staticmethod
    def read_question_details_by_exam(exam_id: int) -> List[dict]:
        """
        Return the questions saved in an exam in their stored order.

        This repository method only performs DB lookup/join work. The Service layer
        is responsible for shaping the result for the View.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''
                SELECT
                    eq.exam_question_id,
                    eq.exam_id,
                    eq.question_id,
                    eq.question_order,
                    q.question_text,
                    q.category,
                    q.sub_category,
                    q.difficulty,
                    q.answer_text,
                    q.acceptable_answers,
                    q.explanation,
                    q.tags,
                    q.is_active,
                    q.created_at
                FROM exam_questions eq
                LEFT JOIN questions q ON q.question_id = eq.question_id
                WHERE eq.exam_id = ?
                ORDER BY eq.question_order
                ''',
                (exam_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            print(f"??Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_question_ids_by_exam(exam_id: int) -> List[int]:
        """
        시험에 포함된 문제 ID들을 순서대로 조회한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            List[int]: 문제 ID 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT question_id FROM exam_questions WHERE exam_id = ? ORDER BY question_order',
                (exam_id,)
            )
            rows = cursor.fetchall()
            question_ids = [row[0] for row in rows]
            return question_ids
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def delete_by_exam(exam_id: int) -> bool:
        """
        시험에 포함된 모든 문제를 제거한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            bool: 성공 여부
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM exam_questions WHERE exam_id = ?', (exam_id,))
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"ExamQuestions deleted successfully (Exam ID: {exam_id}, Count: {rows_affected})")
                return True
            else:
                print(f"No exam questions found for exam ID: {exam_id}")
                return False
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def count_by_exam(exam_id: int) -> int:
        """
        시험에 포함된 문제 개수를 반환한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            int: 문제 개수
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM exam_questions WHERE exam_id = ?', (exam_id,))
            count = cursor.fetchone()[0]
            return count
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
