"""정답 비교 및 점수 계산 서비스"""

from typing import Dict, List, Optional
from app.models.exam_result_model import ExamResult
from app.models.answer_record_model import AnswerRecord
from app.repositories.question_repository import QuestionRepository
from app.repositories.exam_question_repository import ExamQuestionRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.answer_record_repository import AnswerRecordRepository
from app.utils.answer_normalizer import AnswerNormalizer
from app.utils.constants import TOTAL_SCORE, CORRECT, WRONG


class GradingService:
    """
    시험 채점, 점수 계산, 통계 제공 서비스
    """
    
    @staticmethod
    def check_answer(student_answer: str, question_id: int) -> tuple[bool, str]:
        """
        단일 문제에 대한 학생 답안이 정답인지 확인한다.
        
        Args:
            student_answer (str): 학생 답안
            question_id (int): 문제 ID
            
        Returns:
            tuple[bool, str]: (정답 여부, 기준 정답)
            
        Raises:
            ValueError: 문제를 찾을 수 없을 때
        """
        return AnswerNormalizer.is_correct(student_answer, question_id)
    
    @staticmethod
    def grade_exam(exam_id: int, student_id: int, student_answers: Dict[int, str]) -> ExamResult:
        """
        전체 시험을 채점한다.
        
        Args:
            exam_id (int): 시험 ID
            student_id (int): 학생 ID
            student_answers (Dict[int, str]): 문제 ID -> 학생 답안 매핑
            
        Returns:
            ExamResult: 채점 결과
            
        Example:
            >>> result = grade_exam(
            ...     exam_id=1,
            ...     student_id=1,
            ...     student_answers={1: "went", 2: "the", 3: "was"}
            ... )
            >>> print(f"점수: {result.score}, 정답률: {result.accuracy}")
        """
        correct_count = 0
        total_count = len(student_answers)
        
        answer_records = []
        
        # 각 문제 채점
        for question_id, student_answer in student_answers.items():
            is_correct, correct_answer = GradingService.check_answer(student_answer, question_id)
            correct_count += 1 if is_correct else 0
            
            # 답안 기록 생성
            record = AnswerRecord(
                exam_id=exam_id,
                student_id=student_id,
                question_id=question_id,
                student_answer=student_answer,
                correct_answer=correct_answer,
                is_correct=CORRECT if is_correct else WRONG
            )
            answer_records.append(record)
        
        # 결과 계산
        wrong_count = total_count - correct_count
        score = GradingService.calculate_score(correct_count, total_count)
        accuracy = GradingService.calculate_accuracy(correct_count, total_count)
        
        # ExamResult 생성
        result = ExamResult(
            exam_id=exam_id,
            student_id=student_id,
            correct_count=correct_count,
            wrong_count=wrong_count,
            score=score,
            accuracy=accuracy
        )
        
        # 데이터베이스에 저장
        result.result_id = ResultRepository.create(result)
        AnswerRecordRepository.create_batch(answer_records)
        
        print(f"✓ Exam graded: Student {student_id}, Score: {score:.2f}, Accuracy: {accuracy*100:.2f}%")
        return result
    
    @staticmethod
    def calculate_score(correct_count: int, total_questions: int) -> float:
        """
        점수를 계산한다 (0-100 스케일).
        
        Args:
            correct_count (int): 정답 개수
            total_questions (int): 전체 문항 수
            
        Returns:
            float: 점수
            
        Example:
            >>> calculate_score(8, 10)
            80.0
        """
        if total_questions == 0:
            return 0.0
        return (correct_count / total_questions) * TOTAL_SCORE
    
    @staticmethod
    def calculate_accuracy(correct_count: int, total_questions: int) -> float:
        """
        정답률을 계산한다 (0-1.0 스케일).
        
        Args:
            correct_count (int): 정답 개수
            total_questions (int): 전체 문항 수
            
        Returns:
            float: 정답률
            
        Example:
            >>> calculate_accuracy(8, 10)
            0.8
        """
        if total_questions == 0:
            return 0.0
        return correct_count / total_questions
    
    @staticmethod
    def get_exam_statistics(exam_id: int) -> Dict:
        """
        시험의 전체 통계를 반환한다.
        
        Args:
            exam_id (int): 시험 ID
            
        Returns:
            Dict: 통계 정보
                - total_students: 응시 학생 수
                - avg_score: 평균 점수
                - avg_accuracy: 평균 정답률
                - max_score: 최고 점수
                - min_score: 최저 점수
                - results: 학생별 결과 리스트
                
        Example:
            >>> stats = get_exam_statistics(1)
            >>> print(f"평균 점수: {stats['avg_score']:.2f}")
        """
        results = ResultRepository.read_by_exam(exam_id)
        
        if not results:
            return {
                'total_students': 0,
                'avg_score': 0.0,
                'avg_accuracy': 0.0,
                'max_score': 0.0,
                'min_score': 0.0,
                'results': []
            }
        
        scores = [r.score for r in results]
        accuracies = [r.accuracy for r in results]
        
        return {
            'total_students': len(results),
            'avg_score': ResultRepository.get_exam_average_score(exam_id),
            'avg_accuracy': ResultRepository.get_exam_average_accuracy(exam_id),
            'max_score': max(scores),
            'min_score': min(scores),
            'results': results
        }
    
    @staticmethod
    def get_question_statistics(question_id: int) -> Dict:
        """
        문제의 통계를 반환한다.
        
        Args:
            question_id (int): 문제 ID
            
        Returns:
            Dict: 문제 통계
                - accuracy: 정답률
                - total_attempts: 시도 횟수
                - correct_count: 정답 개수
                - wrong_count: 오답 개수
        """
        accuracy = AnswerRecordRepository.get_question_accuracy(question_id)
        records = AnswerRecordRepository.read_by_question(question_id)
        
        correct_count = sum(1 for r in records if r.is_correct == CORRECT)
        wrong_count = len(records) - correct_count
        
        return {
            'accuracy': accuracy,
            'total_attempts': len(records),
            'correct_count': correct_count,
            'wrong_count': wrong_count
        }
