"""답안 정규화 및 정답 비교 로직"""

import re
from typing import Tuple
from app.repositories.question_repository import QuestionRepository


class AnswerNormalizer:
    """
    학생 답안을 정규화하고 정답과 비교하는 클래스
    
    정규화 규칙:
    1. 앞뒤 공백 제거
    2. 대소문자 통일 (소문자로 변환)
    3. 문장부호 제거 (. , ! ? ; : 등)
    4. 연속 공백 정리 (여러 공백을 한 공백으로)
    """
    
    # 제거할 문장부호
    PUNCTUATION = r'[.,!?;:\'"\-]'
    
    @staticmethod
    def normalize(answer: str) -> str:
        """
        답안을 정규화한다.
        
        Args:
            answer (str): 원본 답안
            
        Returns:
            str: 정규화된 답안
            
        Example:
            >>> normalize(" Went. ")
            'went'
            >>> normalize("Passive Voice")
            'passive voice'
        """
        if not answer:
            return ""
        
        # 1. 앞뒤 공백 제거
        answer = answer.strip()
        
        # 2. 대소문자 통일 (소문자로 변환)
        answer = answer.lower()
        
        # 3. 문장부호 제거
        answer = re.sub(AnswerNormalizer.PUNCTUATION, '', answer)
        
        # 4. 연속 공백 정리
        answer = re.sub(r'\s+', ' ', answer).strip()
        
        return answer
    
    @staticmethod
    def is_correct(student_answer: str, question_id: int) -> Tuple[bool, str]:
        """
        학생 답안이 정답인지 확인한다.
        
        Args:
            student_answer (str): 학생 답안
            question_id (int): 문제 ID
            
        Returns:
            Tuple[bool, str]: (정답 여부, 기준 정답)
            
        Raises:
            ValueError: 문제를 찾을 수 없을 때
            
        Example:
            >>> is_correct("went", 1)
            (True, "went")
        """
        # 문제 조회
        question = QuestionRepository.read(question_id)
        if not question:
            raise ValueError(f"Question not found: {question_id}")
        
        # 정규화
        normalized_student = AnswerNormalizer.normalize(student_answer)
        normalized_correct = AnswerNormalizer.normalize(question.answer_text)
        
        # 기준 정답과 비교
        if normalized_student == normalized_correct:
            return True, question.answer_text
        
        # 허용 답안과 비교
        if question.acceptable_answers:
            acceptable_list = question.get_acceptable_answers_list()
            for acceptable in acceptable_list:
                normalized_acceptable = AnswerNormalizer.normalize(acceptable)
                if normalized_student == normalized_acceptable:
                    return True, question.answer_text
        
        return False, question.answer_text
    
    @staticmethod
    def compare_answers(student_answer: str, correct_answer: str, acceptable_answers: str = None) -> bool:
        """
        두 답안을 비교한다 (문제 객체 없이).
        
        Args:
            student_answer (str): 학생 답안
            correct_answer (str): 기준 정답
            acceptable_answers (str): 허용 답안 (쉼표로 구분)
            
        Returns:
            bool: 정답 여부
            
        Example:
            >>> compare_answers("Went.", "went")
            True
            >>> compare_answers("the", "to", "to, the")
            True
        """
        # 정규화
        normalized_student = AnswerNormalizer.normalize(student_answer)
        normalized_correct = AnswerNormalizer.normalize(correct_answer)
        
        # 기준 정답과 비교
        if normalized_student == normalized_correct:
            return True
        
        # 허용 답안과 비교
        if acceptable_answers:
            acceptable_list = [ans.strip() for ans in acceptable_answers.split(',')]
            for acceptable in acceptable_list:
                normalized_acceptable = AnswerNormalizer.normalize(acceptable)
                if normalized_student == normalized_acceptable:
                    return True
        
        return False
