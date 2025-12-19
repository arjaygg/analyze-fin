"""
Rule-based transaction categorizer.

Provides:
- Categorizer: Main categorization service
- CategorizationResult: Result of categorizing a transaction
- Methods: merchant_mapping, keyword matching, pattern matching
"""

from dataclasses import dataclass
from typing import Sequence, TYPE_CHECKING

from analyze_fin.categorization.taxonomy import (
    CATEGORIES,
    MERCHANT_MAPPING,
    get_category,
    get_normalized_name,
)
from analyze_fin.parsers.base import RawTransaction

if TYPE_CHECKING:
    from analyze_fin.categorization.learning import CategoryLearner


@dataclass
class CategorizationResult:
    """Result of categorizing a transaction.

    Attributes:
        category: The assigned category name
        confidence: Confidence score (0.0 to 1.0)
        method: Method used for categorization (merchant_mapping, keyword, None)
        merchant_normalized: Properly-cased merchant name if matched
    """

    category: str
    confidence: float
    method: str | None
    merchant_normalized: str | None = None


class Categorizer:
    """Rule-based transaction categorizer.

    Uses a hierarchy of methods to categorize transactions:
    1. Direct merchant mapping (highest confidence)
    2. Keyword matching (medium confidence)
    3. Uncategorized fallback (zero confidence)

    Example:
        categorizer = Categorizer()

        # Single transaction
        result = categorizer.categorize("JOLLIBEE GREENBELT")
        print(f"{result.category} ({result.confidence:.0%})")

        # Batch categorization
        results = categorizer.categorize_batch([
            "JOLLIBEE", "GRAB RIDE", "UNKNOWN STORE"
        ])
    """

    def __init__(self, learner: "CategoryLearner | None" = None) -> None:
        """Initialize categorizer with taxonomy.

        Args:
            learner: Optional CategoryLearner for user-learned rules
        """
        self._merchant_mapping = MERCHANT_MAPPING
        self._categories = CATEGORIES
        self._learner = learner
        # Build keyword lookup for faster matching
        self._keyword_to_category: dict[str, str] = {}
        for cat_name, cat_info in CATEGORIES.items():
            for keyword in cat_info.get("keywords", []):
                self._keyword_to_category[keyword.lower()] = cat_name

    def categorize(self, description: str) -> CategorizationResult:
        """Categorize a transaction description.

        Args:
            description: Transaction description text

        Returns:
            CategorizationResult with category, confidence, and method
        """
        if not description:
            return CategorizationResult(
                category="Uncategorized",
                confidence=0.0,
                method=None,
                merchant_normalized=None,
            )

        description_upper = description.upper().strip()

        # Step 0: Try learned rules first (highest priority)
        if self._learner is not None:
            learned = self._learner.apply(description)
            if learned is not None:
                return CategorizationResult(
                    category=learned.category,
                    confidence=learned.confidence,
                    method="learned",
                    merchant_normalized=learned.merchant_normalized,
                )

        # Step 1: Try direct merchant mapping
        result = self._try_merchant_mapping(description_upper)
        if result:
            return result

        # Step 2: Try keyword matching
        result = self._try_keyword_matching(description_upper)
        if result:
            return result

        # Step 3: Uncategorized fallback
        return CategorizationResult(
            category="Uncategorized",
            confidence=0.0,
            method=None,
            merchant_normalized=None,
        )

    def _try_merchant_mapping(
        self, description_upper: str
    ) -> CategorizationResult | None:
        """Try to categorize via merchant mapping.

        Args:
            description_upper: Uppercase transaction description

        Returns:
            CategorizationResult if matched, None otherwise
        """
        # Exact match first
        if description_upper in self._merchant_mapping:
            mapping = self._merchant_mapping[description_upper]
            return CategorizationResult(
                category=mapping["category"],
                confidence=0.98,
                method="merchant_mapping",
                merchant_normalized=mapping["normalized"],
            )

        # Check each known merchant for partial match
        # Score: (position_score, length) - prioritize start of string and longer matches
        best_match: tuple[str, dict] | None = None
        best_score: tuple[int, int] = (-1, 0)  # (negative position, length)

        for merchant_key, mapping in self._merchant_mapping.items():
            # Check if known merchant is in description
            if merchant_key in description_upper:
                position = description_upper.index(merchant_key)
                # Score: earlier position is better (negative position), longer is better
                score = (-position, len(merchant_key))
                if score > best_score:
                    best_match = (merchant_key, mapping)
                    best_score = score
            elif description_upper in merchant_key:
                # Description is subset of merchant key - lower priority
                score = (-100, len(description_upper))  # Low position priority
                if score > best_score:
                    best_match = (merchant_key, mapping)
                    best_score = score

        if best_match:
            merchant_key, mapping = best_match
            # Confidence based on match quality
            # Higher base confidence for merchant matches
            match_ratio = len(merchant_key) / max(len(description_upper), 1)
            confidence = min(0.95, 0.90 + (match_ratio * 0.05))

            return CategorizationResult(
                category=mapping["category"],
                confidence=confidence,
                method="merchant_mapping",
                merchant_normalized=mapping["normalized"],
            )

        return None

    def _try_keyword_matching(
        self, description_upper: str
    ) -> CategorizationResult | None:
        """Try to categorize via keyword matching.

        Args:
            description_upper: Uppercase transaction description

        Returns:
            CategorizationResult if matched, None otherwise
        """
        description_lower = description_upper.lower()
        words = description_lower.split()

        # Check each word against keywords
        for word in words:
            if word in self._keyword_to_category:
                category = self._keyword_to_category[word]
                return CategorizationResult(
                    category=category,
                    confidence=0.75,
                    method="keyword",
                    merchant_normalized=None,
                )

        # Check for keyword substrings
        for keyword, category in self._keyword_to_category.items():
            if keyword in description_lower:
                return CategorizationResult(
                    category=category,
                    confidence=0.7,
                    method="keyword",
                    merchant_normalized=None,
                )

        return None

    def categorize_batch(
        self, descriptions: Sequence[str]
    ) -> list[CategorizationResult]:
        """Categorize multiple transaction descriptions.

        Args:
            descriptions: List of transaction descriptions

        Returns:
            List of CategorizationResult in same order as input
        """
        return [self.categorize(desc) for desc in descriptions]

    def categorize_transaction(
        self, transaction: RawTransaction
    ) -> CategorizationResult:
        """Categorize a RawTransaction object.

        Args:
            transaction: RawTransaction to categorize

        Returns:
            CategorizationResult
        """
        return self.categorize(transaction.description)

    def categorize_transactions(
        self, transactions: Sequence[RawTransaction]
    ) -> list[CategorizationResult]:
        """Categorize multiple RawTransaction objects.

        Args:
            transactions: List of RawTransaction objects

        Returns:
            List of CategorizationResult in same order as input
        """
        return [self.categorize_transaction(tx) for tx in transactions]
