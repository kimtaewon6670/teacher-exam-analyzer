from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Question:
    """
    문제 데이터 모델
    
    Attributes:
        question_id: 문제 고유 ID
        exam_name: 시험명
        class_name: 반 정보
        question_text: 문제 내용
        category: 문제 유형 (어휘, 문법, 독해)
        sub_category: 세부 분류
        difficulty: 난이도 (쉬움, 보통, 어려움)
        answer_text: 기준 정답
        acceptable_answers: 허용 답안 (쉼표로 구분)
        explanation: 해설
        tags: 태그 (쉼표로 구분)
        is_active: 활성화 여부 (1: 활성, 0: 비활성)
        created_at: 등록일
    """
    question_text: str
    category: str
    difficulty: str
    answer_text: str
    question_id: Optional[int] = None
    exam_name: Optional[str] = None
    class_name: Optional[str] = None
    sub_category: Optional[str] = None
    acceptable_answers: Optional[str] = None
    explanation: Optional[str] = None
    tags: Optional[str] = None
    is_active: int = 1
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Question 객체를 딕셔너리로 변환한다.
        
        Returns:
            dict: Question 객체의 딕셔너리 표현
        """
        return {
            'question_id': self.question_id,
            'exam_name': self.exam_name,
            'class_name': self.class_name,
            'question_text': self.question_text,
            'category': self.category,
            'sub_category': self.sub_category,
            'difficulty': self.difficulty,
            'answer_text': self.answer_text,
            'acceptable_answers': self.acceptable_answers,
            'explanation': self.explanation,
            'tags': self.tags,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        """
        딕셔너리에서 Question 객체를 생성한다.
        
        Args:
            data: Question 정보를 담은 딕셔너리
            
        Returns:
            Question: 생성된 Question 객체
        """
        return cls(
            question_text=data.get('question_text'),
            category=data.get('category'),
            difficulty=data.get('difficulty'),
            answer_text=data.get('answer_text'),
            question_id=data.get('question_id'),
            exam_name=data.get('exam_name'),
            class_name=data.get('class_name'),
            sub_category=data.get('sub_category'),
            acceptable_answers=data.get('acceptable_answers'),
            explanation=data.get('explanation'),
            tags=data.get('tags'),
            is_active=data.get('is_active', 1),
            created_at=data.get('created_at')
        )
    
    def get_acceptable_answers_list(self) -> List[str]:
        """
        허용 답안을 리스트로 반환한다.
        
        Returns:
            List[str]: 허용 답안 리스트
        """
        if not self.acceptable_answers:
            return []
        return [answer.strip() for answer in self.acceptable_answers.split(',')]
    
    def get_tags_list(self) -> List[str]:
        """
        태그를 리스트로 반환한다.
        
        Returns:
            List[str]: 태그 리스트
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
