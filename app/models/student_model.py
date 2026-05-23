from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Student:
    """
    학생 데이터 모델
    
    Attributes:
        student_id: 학생 고유 ID
        name: 학생 이름
        student_number: 학번
        class_name: 반 정보
        is_active: 활성화 여부 (1: 활성, 0: 비활성)
        created_at: 등록일
    """
    name: str
    student_number: str
    class_name: str
    student_id: Optional[int] = None
    is_active: int = 1
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Student 객체를 딕셔너리로 변환한다.
        
        Returns:
            dict: Student 객체의 딕셔너리 표현
        """
        return {
            'student_id': self.student_id,
            'name': self.name,
            'student_number': self.student_number,
            'class_name': self.class_name,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        """
        딕셔너리에서 Student 객체를 생성한다.
        
        Args:
            data: Student 정보를 담은 딕셔너리
            
        Returns:
            Student: 생성된 Student 객체
        """
        return cls(
            name=data.get('name'),
            student_number=data.get('student_number'),
            class_name=data.get('class_name'),
            student_id=data.get('student_id'),
            is_active=data.get('is_active', 1),
            created_at=data.get('created_at')
        )
