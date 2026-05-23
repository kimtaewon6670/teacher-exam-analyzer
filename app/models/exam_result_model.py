from dataclasses import dataclass
from typing import Optional


@dataclass
class ExamResult:
    """
    학생별 시험 결과 데이터 모델
    
    Attributes:
        result_id: 시험 결과 ID
        exam_id: 시험 ID
        student_id: 학생 ID
        correct_count: 정답 수
        wrong_count: 오답 수
        score: 점수 (0-100)
        accuracy: 정답률 (0-1.0)
        created_at: 저장일
    """
    exam_id: int
    student_id: int
    correct_count: int
    wrong_count: int
    score: float
    accuracy: float
    result_id: Optional[int] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        ExamResult 객체를 딕셔너리로 변환한다.
        
        Returns:
            dict: ExamResult 객체의 딕셔너리 표현
        """
        return {
            'result_id': self.result_id,
            'exam_id': self.exam_id,
            'student_id': self.student_id,
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'score': self.score,
            'accuracy': self.accuracy,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ExamResult':
        """
        딕셔너리에서 ExamResult 객체를 생성한다.
        
        Args:
            data: ExamResult 정보를 담은 딕셔너리
            
        Returns:
            ExamResult: 생성된 ExamResult 객체
        """
        return cls(
            exam_id=data.get('exam_id'),
            student_id=data.get('student_id'),
            correct_count=data.get('correct_count'),
            wrong_count=data.get('wrong_count'),
            score=data.get('score'),
            accuracy=data.get('accuracy'),
            result_id=data.get('result_id'),
            created_at=data.get('created_at')
        )
