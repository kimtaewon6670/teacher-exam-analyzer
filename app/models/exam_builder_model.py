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
    sub_category: str = ""
    tag: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExamBuildItem":
        difficulty_counts = cls._extract_difficulty_counts(data)
        total_count = cls._to_count(
            data.get("total_count", data.get("count", data.get("total", "")))
        )

        if total_count == 0:
            total_count = sum(difficulty_counts.values())

        return cls(
            category=cls._normalize_category(data.get("category", data.get("type", ""))),
            total_count=total_count,
            difficulty_counts=difficulty_counts,
            sub_category=cls._normalize_all_option(
                data.get("sub_category", data.get("subcategory", "")),
                {"전체 분류", "전체분류", "all", "all categories"},
            ),
            tag=cls._normalize_all_option(
                data.get("tag", data.get("tags", "")),
                {"전체 태그", "전체태그", "all", "all tags"},
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "total_count": self.total_count,
            "difficulty_counts": dict(self.difficulty_counts),
            "sub_category": self.sub_category,
            "tag": self.tag,
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
            ExamBuildItem._normalize_difficulty(difficulty): ExamBuildItem._to_count(count)
            for difficulty, count in raw_counts.items()
            if ExamBuildItem._normalize_difficulty(difficulty)
        }

        difficulty_aliases = {
            "easy_count": "쉬움",
            "medium_count": "보통",
            "normal_count": "보통",
            "hard_count": "어려움",
            "low_count": "쉬움",
            "middle_count": "보통",
            "high_count": "어려움",
        }
        for key, difficulty in difficulty_aliases.items():
            if key in data:
                counts[difficulty] = ExamBuildItem._to_count(data.get(key))

        single_difficulty = ExamBuildItem._normalize_difficulty(
            data.get("difficulty", data.get("level", ""))
        )
        single_count = ExamBuildItem._to_count(
            data.get("total_count", data.get("count", data.get("total", 0)))
        )
        if single_difficulty and single_count and not counts:
            counts[single_difficulty] = single_count

        return counts

    @staticmethod
    def _normalize_category(value: Any) -> str:
        value = str(value or "").strip()
        aliases = {
            "vocabulary": "어휘",
            "vocab": "어휘",
            "word": "어휘",
            "grammar": "문법",
            "reading": "독해",
        }
        return aliases.get(value.lower(), value)

    @staticmethod
    def _normalize_difficulty(value: Any) -> str:
        value = str(value or "").strip()
        aliases = {
            "easy": "쉬움",
            "low": "쉬움",
            "normal": "보통",
            "medium": "보통",
            "middle": "보통",
            "hard": "어려움",
            "high": "어려움",
        }
        return aliases.get(value.lower(), value)

    @staticmethod
    def _normalize_all_option(value: Any, all_labels: set[str]) -> str:
        value = str(value or "").strip()
        return "" if value.lower() in {label.lower() for label in all_labels} else value

    @staticmethod
    def _to_count(value: Any) -> int:
        if value in (None, ""):
            return 0

        try:
            return max(int(value), 0)
        except (TypeError, ValueError):
            return 0
