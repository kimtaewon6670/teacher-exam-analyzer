from dataclasses import dataclass
from typing import Optional


@dataclass
class AnswerRecord:
    """
    학생별 문항 답안 기록 데이터 모델
    
    Attributes:
        answer_id: 답안 기록 ID
        exam_id: 시험 ID
        student_id: 학생 ID
        question_id: 문제 ID
        student_answer: 학생 답안
        correct_answer: 기준 정답
        is_correct: 정답 여부 (1: 정답, 0: 오답)
    """
    exam_id: int
    student_id: int
    question_id: int
    student_answer: str
    correct_answer: str
    is_correct: int
    answer_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        """
        AnswerRecord 객체를 딕셔너리로 변환한다.
        
        Returns:
            dict: AnswerRecord 객체의 딕셔너리 표현
        """
        return {
            'answer_id': self.answer_id,
            'exam_id': self.exam_id,
            'student_id': self.student_id,
            'question_id': self.question_id,
            'student_answer': self.student_answer,
            'correct_answer': self.correct_answer,
            'is_correct': self.is_correct
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AnswerRecord':
        """
        딕셔너리에서 AnswerRecord 객체를 생성한다.
        
        Args:
            data: AnswerRecord 정보를 담은 딕셔너리
            
        Returns:
            AnswerRecord: 생성된 AnswerRecord 객체
        """
        return cls(
            exam_id=data.get('exam_id'),
            student_id=data.get('student_id'),
            question_id=data.get('question_id'),
            student_answer=data.get('student_answer'),
            correct_answer=data.get('correct_answer'),
            is_correct=data.get('is_correct'),
            answer_id=data.get('answer_id')
        )
