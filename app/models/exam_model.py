from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Exam:
    """
    시험 데이터 모델
    
    Attributes:
        exam_id: 시험 고유 ID
        exam_name: 시험명
        description: 시험 설명
        exam_date: 시험 일자
        target_class: 대상 반
        total_questions: 총 문항 수
        created_at: 생성일
    """
    exam_name: str
    target_class: str
    total_questions: int
    exam_id: Optional[int] = None
    description: Optional[str] = None
    exam_date: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Exam 객체를 딕셔너리로 변환한다.
        
        Returns:
            dict: Exam 객체의 딕셔너리 표현
        """
        return {
            'exam_id': self.exam_id,
            'exam_name': self.exam_name,
            'description': self.description,
            'exam_date': self.exam_date,
            'target_class': self.target_class,
            'total_questions': self.total_questions,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Exam':
        """
        딕셔너리에서 Exam 객체를 생성한다.
        
        Args:
            data: Exam 정보를 담은 딕셔너리
            
        Returns:
            Exam: 생성된 Exam 객체
        """
        return cls(
            exam_name=data.get('exam_name'),
            target_class=data.get('target_class'),
            total_questions=data.get('total_questions'),
            exam_id=data.get('exam_id'),
            description=data.get('description'),
            exam_date=data.get('exam_date'),
            created_at=data.get('created_at')
        )
