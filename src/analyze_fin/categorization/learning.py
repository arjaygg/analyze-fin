"""
Interactive learning for transaction categorization.

Provides:
- CategoryLearner: Learn from user corrections
- LearnedRule: Representation of a learned rule
- Persistence via JSON files
"""

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class LearnedRule:
    """A learned categorization rule.

    Attributes:
        pattern: The pattern to match (uppercase)
        category: The assigned category
        merchant_normalized: Optional normalized merchant name
        source: Source of the rule ('user', 'import', etc.)
        confidence: Confidence score (0.0 to 1.0)
        created_at: When the rule was created
    """

    pattern: str
    category: str
    merchant_normalized: str | None = None
    source: str = "user"
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "pattern": self.pattern,
            "category": self.category,
            "merchant_normalized": self.merchant_normalized,
            "source": self.source,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LearnedRule":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()

        return cls(
            pattern=data["pattern"],
            category=data["category"],
            merchant_normalized=data.get("merchant_normalized"),
            source=data.get("source", "user"),
            confidence=data.get("confidence", 1.0),
            created_at=created_at,
        )


@dataclass
class ApplyResult:
    """Result of applying learned rules.

    Attributes:
        category: The matched category
        merchant_normalized: Optional normalized merchant name
        confidence: Confidence score
        rule: The matched rule
    """

    category: str
    merchant_normalized: str | None
    confidence: float
    rule: LearnedRule


class CategoryLearner:
    """Learn categorization rules from user corrections.

    Stores learned rules and applies them during categorization.
    Rules can be persisted to/from JSON files.

    Example:
        learner = CategoryLearner()

        # Learn from correction
        learner.learn("LOCAL STORE", category="Shopping")

        # Apply learned rules
        result = learner.apply("LOCAL STORE")
        if result:
            print(f"Learned: {result.category}")

        # Save rules
        learner.save(Path("rules.json"))

        # Load rules
        learner.load(Path("rules.json"))
    """

    def __init__(self) -> None:
        """Initialize an empty learner."""
        self._rules: dict[str, LearnedRule] = {}

    def learn(
        self,
        description: str,
        category: str,
        merchant_normalized: str | None = None,
        source: str = "user",
        confidence: float = 1.0,
    ) -> LearnedRule:
        """Learn a new categorization rule.

        Args:
            description: Transaction description to match
            category: Category to assign
            merchant_normalized: Optional normalized merchant name
            source: Source of the rule
            confidence: Confidence score

        Returns:
            The created LearnedRule
        """
        pattern = description.upper().strip()

        rule = LearnedRule(
            pattern=pattern,
            category=category,
            merchant_normalized=merchant_normalized,
            source=source,
            confidence=confidence,
        )

        self._rules[pattern] = rule
        return rule

    def learn_batch(
        self, corrections: Sequence[dict]
    ) -> int:
        """Learn multiple rules at once.

        Args:
            corrections: List of dicts with 'description', 'category',
                        and optionally 'merchant_normalized'

        Returns:
            Number of rules learned
        """
        count = 0
        for correction in corrections:
            self.learn(
                description=correction["description"],
                category=correction["category"],
                merchant_normalized=correction.get("merchant_normalized"),
            )
            count += 1
        return count

    def apply(self, description: str) -> ApplyResult | None:
        """Apply learned rules to a description.

        Args:
            description: Transaction description

        Returns:
            ApplyResult if a rule matches, None otherwise
        """
        if not description:
            return None

        normalized = description.upper().strip()

        # Try exact match first
        if normalized in self._rules:
            rule = self._rules[normalized]
            return ApplyResult(
                category=rule.category,
                merchant_normalized=rule.merchant_normalized,
                confidence=rule.confidence,
                rule=rule,
            )

        # Try partial match (pattern in description)
        for pattern, rule in self._rules.items():
            if pattern in normalized:
                return ApplyResult(
                    category=rule.category,
                    merchant_normalized=rule.merchant_normalized,
                    confidence=rule.confidence * 0.9,  # Lower confidence for partial
                    rule=rule,
                )

        return None

    def get_rules(self) -> list[LearnedRule]:
        """Get all learned rules.

        Returns:
            List of LearnedRule objects
        """
        return list(self._rules.values())

    def delete_rule(self, pattern: str) -> bool:
        """Delete a rule by pattern.

        Args:
            pattern: The pattern to delete

        Returns:
            True if deleted, False if not found
        """
        key = pattern.upper().strip()
        if key in self._rules:
            del self._rules[key]
            return True
        return False

    def clear(self) -> None:
        """Remove all learned rules."""
        self._rules.clear()

    def count(self) -> int:
        """Get number of learned rules.

        Returns:
            Number of rules
        """
        return len(self._rules)

    def save(self, path: Path) -> None:
        """Save rules to a JSON file.

        Args:
            path: File path to save to
        """
        data = {
            "version": 1,
            "rules": [rule.to_dict() for rule in self._rules.values()],
        }

        path.write_text(json.dumps(data, indent=2))

    def load(self, path: Path) -> int:
        """Load rules from a JSON file.

        Merges with existing rules (loaded rules take precedence
        for same pattern).

        Args:
            path: File path to load from

        Returns:
            Number of rules loaded
        """
        if not path.exists():
            return 0

        data = json.loads(path.read_text())
        rules = data.get("rules", [])

        count = 0
        for rule_data in rules:
            rule = LearnedRule.from_dict(rule_data)
            self._rules[rule.pattern] = rule
            count += 1

        return count
