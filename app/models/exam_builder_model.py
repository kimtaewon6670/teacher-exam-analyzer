from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExamBuildItem:
    """
    One row in the exam builder cart.

    category: question category such as vocabulary, grammar, or reading
    total_count: optional row total. When blank, it is calculated from difficulty_counts.
    difficulty_counts: requested count by difficulty. Blank values are stored as 0.
    """
    category: str
    total_count: int = 0
    difficulty_counts: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExamBuildItem":
        difficulty_counts = cls._extract_difficulty_counts(data)
        total_count = cls._to_count(
            data.get("total_count", data.get("count", data.get("total", "")))
        )

        if total_count == 0:
            total_count = sum(difficulty_counts.values())

        return cls(
            category=str(data.get("category", data.get("type", ""))).strip(),
            total_count=total_count,
            difficulty_counts=difficulty_counts,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "total_count": self.total_count,
            "difficulty_counts": dict(self.difficulty_counts),
        }

    def is_empty(self) -> bool:
        return not self.category or self.total_count <= 0

    def unspecified_count(self) -> int:
        specified_count = sum(self.difficulty_counts.values())
        return max(self.total_count - specified_count, 0)

    @staticmethod
    def _extract_difficulty_counts(data: dict[str, Any]) -> dict[str, int]:
        raw_counts = data.get("difficulty_counts", {})
        if not isinstance(raw_counts, dict):
            raw_counts = {}

        counts = {
            str(difficulty).strip(): ExamBuildItem._to_count(count)
            for difficulty, count in raw_counts.items()
            if str(difficulty).strip()
        }

        difficulty_aliases = {
            "easy_count": "쉬움",
            "medium_count": "중간",
            "hard_count": "어려움",
            "low_count": "쉬움",
            "middle_count": "중간",
            "high_count": "어려움",
        }
        for key, difficulty in difficulty_aliases.items():
            if key in data:
                counts[difficulty] = ExamBuildItem._to_count(data.get(key))

        return counts

    @staticmethod
    def _to_count(value: Any) -> int:
        if value in (None, ""):
            return 0

        try:
            return max(int(value), 0)
        except (TypeError, ValueError):
            return 0
