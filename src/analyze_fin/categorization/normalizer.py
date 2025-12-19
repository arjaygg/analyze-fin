"""
Merchant name normalizer with fuzzy matching.

Provides:
- MerchantNormalizer: Service for normalizing merchant names
- NormalizationResult: Result of normalization attempt
- Exact, partial, and fuzzy matching support
"""

from dataclasses import dataclass
from typing import Sequence

from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING


@dataclass
class NormalizationResult:
    """Result of normalizing a merchant name.

    Attributes:
        original: Original input string
        normalized: Properly-cased merchant name or None
        confidence: Confidence score (0.0 to 1.0)
        match_type: Type of match ('exact', 'partial', or None)
    """

    original: str
    normalized: str | None
    confidence: float
    match_type: str | None


# Additional variations not in main mapping
MERCHANT_VARIATIONS: dict[str, str] = {
    # McDonald's variations
    "MC DONALDS": "MCDONALDS",
    "MC DONALD'S": "MCDONALDS",
    "MC DO": "MCDO",
    # 7-Eleven variations
    "7ELEVEN": "7-ELEVEN",
    "7 ELEVEN": "7-ELEVEN",
    "SEVEN ELEVEN": "7-ELEVEN",
    # Grab variations (GRAB RIDE maps to GRAB)
    "GRAB RIDE": "GRAB",
    # Other common variations
    "SHAKEYS": "SHAKEY'S",
    "MAXS": "MAX'S",
    "RUSTANS": "RUSTAN'S",
    "WENDYS": "WENDY'S",
    "SNR": "S&R",
}


class MerchantNormalizer:
    """Service for normalizing merchant names.

    Normalizes raw transaction descriptions to canonical merchant names
    using exact matching, variation matching, and partial matching.

    Example:
        normalizer = MerchantNormalizer()

        # Simple normalization
        result = normalizer.normalize("JOLLIBEE MAKATI")
        print(f"{result.normalized} ({result.confidence:.0%})")

        # Extract merchant from complex description
        result = normalizer.extract_merchant("GRAB RIDE-12345")
        print(result.normalized)  # "Grab"

        # Add custom mapping
        normalizer.add_mapping("LOCAL STORE", "Maria's Sari-Sari")
    """

    def __init__(self) -> None:
        """Initialize normalizer with merchant mappings."""
        self._merchant_mapping = MERCHANT_MAPPING.copy()
        self._variations = MERCHANT_VARIATIONS.copy()
        self._custom_mappings: dict[str, str] = {}

    def normalize(self, merchant_name: str) -> NormalizationResult:
        """Normalize a merchant name.

        Args:
            merchant_name: Raw merchant name

        Returns:
            NormalizationResult with normalized name and confidence
        """
        if not merchant_name:
            return NormalizationResult(
                original=merchant_name,
                normalized=None,
                confidence=0.0,
                match_type=None,
            )

        original = merchant_name
        normalized_key = merchant_name.upper().strip()

        # Step 1: Check custom mappings first
        if normalized_key in self._custom_mappings:
            return NormalizationResult(
                original=original,
                normalized=self._custom_mappings[normalized_key],
                confidence=0.98,
                match_type="exact",
            )

        # Step 2: Apply variations to normalize key
        resolved_key = self._apply_variations(normalized_key)

        # Step 3: Try exact match
        if resolved_key in self._merchant_mapping:
            return NormalizationResult(
                original=original,
                normalized=self._merchant_mapping[resolved_key]["normalized"],
                confidence=0.98,
                match_type="exact",
            )

        # Step 4: Try partial match (merchant key in description)
        result = self._try_partial_match(original, normalized_key)
        if result:
            return result

        # Step 5: No match found
        return NormalizationResult(
            original=original,
            normalized=None,
            confidence=0.0,
            match_type=None,
        )

    def _apply_variations(self, key: str) -> str:
        """Apply known variations to normalize key.

        Args:
            key: Uppercase merchant key

        Returns:
            Resolved key after applying variations
        """
        if key in self._variations:
            return self._variations[key]
        return key

    def _try_partial_match(
        self, original: str, normalized_key: str
    ) -> NormalizationResult | None:
        """Try to find a partial match.

        Args:
            original: Original input
            normalized_key: Uppercase normalized key

        Returns:
            NormalizationResult if match found, None otherwise
        """
        # Find best partial match
        best_match: tuple[str, dict] | None = None
        best_position = len(normalized_key)  # Start of string preferred
        best_length = 0

        for merchant_key, mapping in self._merchant_mapping.items():
            if merchant_key in normalized_key:
                position = normalized_key.index(merchant_key)
                # Prefer matches at start and longer matches
                if position < best_position or (
                    position == best_position and len(merchant_key) > best_length
                ):
                    best_match = (merchant_key, mapping)
                    best_position = position
                    best_length = len(merchant_key)

        if best_match:
            merchant_key, mapping = best_match
            # Calculate confidence based on match quality
            match_ratio = len(merchant_key) / max(len(normalized_key), 1)
            # Penalize for non-start matches
            position_penalty = 0.05 if best_position > 0 else 0
            confidence = max(0.7, min(0.95, 0.85 + (match_ratio * 0.1) - position_penalty))

            return NormalizationResult(
                original=original,
                normalized=mapping["normalized"],
                confidence=confidence,
                match_type="partial",
            )

        return None

    def extract_merchant(self, description: str) -> NormalizationResult:
        """Extract and normalize merchant from a transaction description.

        More aggressive extraction that handles order numbers,
        branch names, and other suffixes.

        Args:
            description: Full transaction description

        Returns:
            NormalizationResult with extracted merchant
        """
        # First try direct normalization
        result = self.normalize(description)
        if result.normalized is not None:
            return result

        # Try extracting just the first few words
        words = description.upper().strip().split()
        for num_words in range(min(4, len(words)), 0, -1):
            partial = " ".join(words[:num_words])
            result = self.normalize(partial)
            if result.normalized is not None:
                return NormalizationResult(
                    original=description,
                    normalized=result.normalized,
                    confidence=result.confidence * 0.95,  # Slight penalty
                    match_type="partial",
                )

        # No match found
        return NormalizationResult(
            original=description,
            normalized=None,
            confidence=0.0,
            match_type=None,
        )

    def normalize_batch(
        self, merchant_names: Sequence[str]
    ) -> list[NormalizationResult]:
        """Normalize multiple merchant names.

        Args:
            merchant_names: List of merchant names

        Returns:
            List of NormalizationResult in same order
        """
        return [self.normalize(name) for name in merchant_names]

    def add_mapping(self, raw_name: str, normalized_name: str) -> None:
        """Add a custom merchant mapping.

        Args:
            raw_name: Raw merchant name to match
            normalized_name: Normalized name to return
        """
        key = raw_name.upper().strip()
        self._custom_mappings[key] = normalized_name
