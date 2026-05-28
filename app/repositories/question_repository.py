from typing import List, Optional
from app.models.question_model import Question
from app.repositories.db import get_db_connection, close_db_connection
import sqlite3


class QuestionRepository:
    """
    문제 데이터에 대한 CRUD 작업을 수행하는 Repository
    """
    
    @staticmethod
    def create(question: Question) -> int:
        """
        새로운 문제를 데이터베이스에 등록한다.
        
        Args:
            question (Question): 등록할 문제 객체
            
        Returns:
            int: 생성된 문제의 ID
            
        Raises:
            sqlite3.Error: 필수 정보가 없거나 데이터베이스 오류 발생 시
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO questions 
                (exam_name, class_name, question_text, category, sub_category, difficulty, answer_text, 
                 acceptable_answers, explanation, tags, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                question.exam_name,
                question.class_name,
                question.question_text,
                question.category,
                question.sub_category,
                question.difficulty,
                question.answer_text,
                question.acceptable_answers,
                question.explanation,
                question.tags,
                question.is_active
            ))
            
            conn.commit()
            question_id = cursor.lastrowid
            print(f"Question created successfully (ID: {question_id})")
            return question_id
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read(question_id: int) -> Optional[Question]:
        """
        문제 ID로 문제 정보를 조회한다.
        
        Args:
            question_id (int): 문제 ID
            
        Returns:
            Optional[Question]: 조회된 문제 객체, 없으면 None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM questions WHERE question_id = ?', (question_id,))
            row = cursor.fetchone()
            
            if row:
                return Question.from_dict(dict(row))
            return None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_all(active_only: bool = True) -> List[Question]:
        """
        모든 문제 정보를 조회한다.
        
        Args:
            active_only (bool): True일 경우 활성 문제만 조회
            
        Returns:
            List[Question]: 문제 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute('SELECT * FROM questions WHERE is_active = 1 ORDER BY created_at DESC')
            else:
                cursor.execute('SELECT * FROM questions ORDER BY created_at DESC')
            
            rows = cursor.fetchall()
            questions = [Question.from_dict(dict(row)) for row in rows]
            return questions
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_category(category: str, active_only: bool = True) -> List[Question]:
        """
        문제 유형별로 문제들을 조회한다.
        
        Args:
            category (str): 문제 유형 (어휘, 문법, 독해)
            active_only (bool): True일 경우 활성 문제만 조회
            
        Returns:
            List[Question]: 문제 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute(
                    'SELECT * FROM questions WHERE category = ? AND is_active = 1 ORDER BY created_at DESC',
                    (category,)
                )
            else:
                cursor.execute(
                    'SELECT * FROM questions WHERE category = ? ORDER BY created_at DESC',
                    (category,)
                )
            
            rows = cursor.fetchall()
            questions = [Question.from_dict(dict(row)) for row in rows]
            return questions
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_difficulty(difficulty: str, active_only: bool = True) -> List[Question]:
        """
        난이도별로 문제들을 조회한다.
        
        Args:
            difficulty (str): 난이도 (쉬움, 보통, 어려움)
            active_only (bool): True일 경우 활성 문제만 조회
            
        Returns:
            List[Question]: 문제 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute(
                    'SELECT * FROM questions WHERE difficulty = ? AND is_active = 1 ORDER BY created_at DESC',
                    (difficulty,)
                )
            else:
                cursor.execute(
                    'SELECT * FROM questions WHERE difficulty = ? ORDER BY created_at DESC',
                    (difficulty,)
                )
            
            rows = cursor.fetchall()
            questions = [Question.from_dict(dict(row)) for row in rows]
            return questions
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_sub_category(sub_category: str, active_only: bool = True) -> List[Question]:
        """
        세부 분류별로 문제들을 조회한다.
        
        Args:
            sub_category (str): 세부 분류
            active_only (bool): True일 경우 활성 문제만 조회
            
        Returns:
            List[Question]: 문제 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute(
                    'SELECT * FROM questions WHERE sub_category = ? AND is_active = 1 ORDER BY created_at DESC',
                    (sub_category,)
                )
            else:
                cursor.execute(
                    'SELECT * FROM questions WHERE sub_category = ? ORDER BY created_at DESC',
                    (sub_category,)
                )
            
            rows = cursor.fetchall()
            questions = [Question.from_dict(dict(row)) for row in rows]
            return questions
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def read_by_category_and_difficulty(category: str, difficulty: str, active_only: bool = True) -> List[Question]:
        """
        문제 유형과 난이도로 문제들을 조회한다.
        
        Args:
            category (str): 문제 유형
            difficulty (str): 난이도
            active_only (bool): True일 경우 활성 문제만 조회
            
        Returns:
            List[Question]: 문제 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute('''
                    SELECT * FROM questions 
                    WHERE category = ? AND difficulty = ? AND is_active = 1 
                    ORDER BY created_at DESC
                ''', (category, difficulty))
            else:
                cursor.execute('''
                    SELECT * FROM questions 
                    WHERE category = ? AND difficulty = ? 
                    ORDER BY created_at DESC
                ''', (category, difficulty))
            
            rows = cursor.fetchall()
            questions = [Question.from_dict(dict(row)) for row in rows]
            return questions
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def search_by_text(search_text: str, active_only: bool = True) -> List[Question]:
        """
        문제 텍스트로 문제들을 검색한다 (부분 일치).
        
        Args:
            search_text (str): 검색 텍스트
            active_only (bool): True일 경우 활성 문제만 검색
            
        Returns:
            List[Question]: 문제 객체 리스트
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            search_pattern = f"%{search_text}%"
            if active_only:
                cursor.execute('''
                    SELECT * FROM questions 
                    WHERE question_text LIKE ? AND is_active = 1 
                    ORDER BY created_at DESC
                ''', (search_pattern,))
            else:
                cursor.execute('''
                    SELECT * FROM questions 
                    WHERE question_text LIKE ? 
                    ORDER BY created_at DESC
                ''', (search_pattern,))
            
            rows = cursor.fetchall()
            questions = [Question.from_dict(dict(row)) for row in rows]
            return questions
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def update(question: Question) -> bool:
        """
        문제 정보를 업데이트한다.
        
        Args:
            question (Question): 업데이트할 문제 객체 (question_id 필수)
            
        Returns:
            bool: 성공 여부
        """
        if not question.question_id:
            print("question_id is required for update")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE questions 
                SET exam_name = ?, class_name = ?, question_text = ?, category = ?, sub_category = ?, difficulty = ?,
                    answer_text = ?, acceptable_answers = ?, explanation = ?, tags = ?, is_active = ?
                WHERE question_id = ?
            ''', (
                question.exam_name,
                question.class_name,
                question.question_text,
                question.category,
                question.sub_category,
                question.difficulty,
                question.answer_text,
                question.acceptable_answers,
                question.explanation,
                question.tags,
                question.is_active,
                question.question_id
            ))
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"Question updated successfully (ID: {question.question_id})")
                return True
            else:
                print(f"No question found with ID: {question.question_id}")
                return False
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def deactivate(question_id: int) -> bool:
        """
        문제를 비활성화한다 (삭제하지 않고 비활성 처리).
        
        Args:
            question_id (int): 문제 ID
            
        Returns:
            bool: 성공 여부
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE questions SET is_active = 0 WHERE question_id = ?',
                (question_id,)
            )
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"Question deactivated successfully (ID: {question_id})")
                return True
            else:
                print(f"No question found with ID: {question_id}")
                return False
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def activate(question_id: int) -> bool:
        """
        비활성화된 문제를 다시 활성화한다.
        
        Args:
            question_id (int): 문제 ID
            
        Returns:
            bool: 성공 여부
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE questions SET is_active = 1 WHERE question_id = ?',
                (question_id,)
            )
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"Question activated successfully (ID: {question_id})")
                return True
            else:
                print(f"No question found with ID: {question_id}")
                return False
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def delete(question_id: int) -> bool:
        """
        문제를 데이터베이스에서 삭제한다.
        주의: 시험에 포함된 문제는 삭제되지 않을 수 있다 (외래키 제약 조건).
        일반적으로 deactivate()를 사용하는 것이 권장된다.
        
        Args:
            question_id (int): 문제 ID
            
        Returns:
            bool: 성공 여부
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM questions WHERE question_id = ?', (question_id,))
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                print(f"Question deleted successfully (ID: {question_id})")
                return True
            else:
                print(f"No question found with ID: {question_id}")
                return False
                
        except sqlite3.IntegrityError:
            conn.rollback()
            print(f"Cannot delete question with ID {question_id}: Used in exams")
            return False
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def count_all(active_only: bool = True) -> int:
        """
        총 문제 개수를 반환한다.
        
        Args:
            active_only (bool): True일 경우 활성 문제만 카운트
            
        Returns:
            int: 문제 개수
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute('SELECT COUNT(*) FROM questions WHERE is_active = 1')
            else:
                cursor.execute('SELECT COUNT(*) FROM questions')
            
            count = cursor.fetchone()[0]
            return count
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def count_by_category(category: str, active_only: bool = True) -> int:
        """
        카테고리별 문제 개수를 반환한다.
        
        Args:
            category (str): 문제 유형
            active_only (bool): True일 경우 활성 문제만 카운트
            
        Returns:
            int: 문제 개수
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute(
                    'SELECT COUNT(*) FROM questions WHERE category = ? AND is_active = 1',
                    (category,)
                )
            else:
                cursor.execute(
                    'SELECT COUNT(*) FROM questions WHERE category = ?',
                    (category,)
                )
            
            count = cursor.fetchone()[0]
            return count
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)

    @staticmethod
    def get_questions_by_filter(
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        exam_name: Optional[str] = None,
        class_name: Optional[str] = None,
        sub_category: Optional[str] = None,
        tag: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Question]:
        """
        Exam builder에서 사용하는 공통 문제 조회 메서드.
        Service가 문제 생성 조건을 넘기면 DB 조회 조건은 Repository에서만 처리한다.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        conditions = []
        params = []

        if active_only:
            conditions.append("is_active = 1")
        if category:
            conditions.append("category = ?")
            params.append(category)
        if difficulty:
            conditions.append("difficulty = ?")
            params.append(difficulty)
        if exam_name:
            conditions.append("exam_name = ?")
            params.append(exam_name)
        if class_name:
            conditions.append("class_name = ?")
            params.append(class_name)
        if sub_category:
            conditions.append("sub_category = ?")
            params.append(sub_category)
        if tag:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        try:
            cursor.execute(
                f"SELECT * FROM questions {where_clause} ORDER BY created_at DESC",
                params,
            )
            rows = cursor.fetchall()
            return [Question.from_dict(dict(row)) for row in rows]

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            close_db_connection(conn)
