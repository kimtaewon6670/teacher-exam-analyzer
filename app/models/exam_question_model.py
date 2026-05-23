from dataclasses import dataclass
from typing import Optional


@dataclass
class ExamQuestion:
    """
    시험에 포함된 문제 데이터 모델
    
    Attributes:
        exam_question_id: 시험 문항 고유 ID
        exam_id: 시험 ID
        question_id: 문제 ID
        question_order: 문항 순서
    """
    exam_id: int
    question_id: int
    question_order: int
    exam_question_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        """
        ExamQuestion 객체를 딕셔너리로 변환한다.
        
        Returns:
            dict: ExamQuestion 객체의 딕셔너리 표현
        """
        return {
            'exam_question_id': self.exam_question_id,
            'exam_id': self.exam_id,
            'question_id': self.question_id,
            'question_order': self.question_order
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ExamQuestion':
        """
        딕셔너리에서 ExamQuestion 객체를 생성한다.
        
        Args:
            data: ExamQuestion 정보를 담은 딕셔너리
            
        Returns:
            ExamQuestion: 생성된 ExamQuestion 객체
        """
        return cls(
            exam_id=data.get('exam_id'),
            question_id=data.get('question_id'),
            question_order=data.get('question_order'),
            exam_question_id=data.get('exam_question_id')
        )
