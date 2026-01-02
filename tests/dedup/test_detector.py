"""
TDD Tests: Duplicate Transaction Detection

Story 3.1 AC: Detect exact and potential duplicate transactions.
RED phase - these tests will fail until detector.py is implemented.
"""

from datetime import datetime, timedelta
from decimal import Decimal


class TestDuplicateDetectorStructure:
    """Test DuplicateDetector class structure."""

    def test_detector_exists(self):
        """DuplicateDetector can be imported."""
        from analyze_fin.dedup.detector import DuplicateDetector

        assert DuplicateDetector is not None

    def test_detector_can_instantiate(self):
        """DuplicateDetector can be instantiated."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        assert detector is not None

    def test_detector_has_find_duplicates_method(self):
        """DuplicateDetector has find_duplicates method."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        assert callable(detector.find_duplicates)

    def test_detector_has_is_duplicate_method(self):
        """DuplicateDetector has is_duplicate method."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        assert callable(detector.is_duplicate)


class TestDuplicateMatch:
    """Test DuplicateMatch data class."""

    def test_duplicate_match_exists(self):
        """DuplicateMatch can be imported."""
        from analyze_fin.dedup.detector import DuplicateMatch

        assert DuplicateMatch is not None

    def test_duplicate_match_has_required_fields(self):
        """DuplicateMatch has all required fields."""
        from analyze_fin.dedup.detector import DuplicateMatch

        match = DuplicateMatch(
            transaction_a={"id": 1},
            transaction_b={"id": 2},
            confidence=0.95,
            match_type="exact",
            reasons=["Same date", "Same amount", "Same description"],
        )

        assert match.transaction_a == {"id": 1}
        assert match.transaction_b == {"id": 2}
        assert match.confidence == 0.95
        assert match.match_type == "exact"
        assert len(match.reasons) == 3


class TestExactDuplicateDetection:
    """Test exact duplicate detection."""

    def test_detect_exact_duplicate(self):
        """Detect transactions with same date, amount, and description."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15, 10, 30),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15, 10, 30),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
        ]

        duplicates = detector.find_duplicates(transactions)

        assert len(duplicates) == 1
        assert duplicates[0].match_type == "exact"
        assert duplicates[0].confidence >= 0.99

    def test_no_duplicates_different_dates(self):
        """No duplicates when dates differ."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 16),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
        ]

        duplicates = detector.find_duplicates(transactions)

        assert len(duplicates) == 0

    def test_no_duplicates_different_amounts(self):
        """No duplicates when amounts differ significantly."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("200.00"),
                "description": "JOLLIBEE",
            },
        ]

        duplicates = detector.find_duplicates(transactions)

        assert len(duplicates) == 0

    def test_no_duplicates_different_descriptions(self):
        """No exact duplicates when descriptions differ."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "MCDONALDS",
            },
        ]

        duplicates = detector.find_duplicates(transactions)

        assert len(duplicates) == 0


class TestNearDuplicateDetection:
    """Test near-duplicate detection."""

    def test_detect_near_duplicate_same_day(self):
        """Detect near-duplicates: same day, same amount, similar description."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15, 10, 30),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE GREENBELT",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15, 10, 31),  # 1 minute later
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE GREENBELT 3",
            },
        ]

        duplicates = detector.find_duplicates(transactions)

        assert len(duplicates) == 1
        assert duplicates[0].match_type == "near"
        assert 0.8 <= duplicates[0].confidence < 0.99

    def test_detect_near_duplicate_slight_amount_difference(self):
        """Detect near-duplicates with slight amount differences."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.50"),  # 0.5% difference
                "description": "JOLLIBEE",
            },
        ]

        duplicates = detector.find_duplicates(transactions)

        assert len(duplicates) == 1
        assert duplicates[0].match_type == "near"


class TestCrossSourceDuplicates:
    """Test cross-source duplicate detection."""

    def test_detect_cross_source_duplicates(self):
        """Detect duplicates from different sources."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
                "source": "gcash",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
                "source": "bpi",
            },
        ]

        duplicates = detector.find_duplicates(transactions)

        assert len(duplicates) == 1
        # Cross-source duplicates should be flagged
        assert "cross_source" in [r.lower() for r in duplicates[0].reasons] or \
               duplicates[0].match_type == "cross_source"


class TestIsDuplicateMethod:
    """Test is_duplicate comparison method."""

    def test_is_duplicate_returns_match_for_duplicates(self):
        """is_duplicate returns DuplicateMatch for duplicates."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        tx_a = {
            "date": datetime(2024, 1, 15),
            "amount": Decimal("100.00"),
            "description": "JOLLIBEE",
        }
        tx_b = {
            "date": datetime(2024, 1, 15),
            "amount": Decimal("100.00"),
            "description": "JOLLIBEE",
        }

        result = detector.is_duplicate(tx_a, tx_b)

        assert result is not None
        assert result.confidence >= 0.95

    def test_is_duplicate_returns_none_for_non_duplicates(self):
        """is_duplicate returns None for non-duplicates."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        tx_a = {
            "date": datetime(2024, 1, 15),
            "amount": Decimal("100.00"),
            "description": "JOLLIBEE",
        }
        tx_b = {
            "date": datetime(2024, 1, 16),
            "amount": Decimal("200.00"),
            "description": "MCDONALDS",
        }

        result = detector.is_duplicate(tx_a, tx_b)

        assert result is None


class TestDuplicateReasons:
    """Test duplicate detection reasons."""

    def test_exact_duplicate_reasons(self):
        """Exact duplicates include all matching reasons."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()
        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
        ]

        duplicates = detector.find_duplicates(transactions)

        assert len(duplicates) == 1
        reasons_lower = [r.lower() for r in duplicates[0].reasons]
        assert any("date" in r for r in reasons_lower)
        assert any("amount" in r for r in reasons_lower)
        assert any("description" in r for r in reasons_lower)


class TestDetectorConfiguration:
    """Test detector configuration options."""

    def test_configurable_time_threshold(self):
        """Time threshold can be configured."""
        from analyze_fin.dedup.detector import DuplicateDetector

        # Default: same day
        detector_default = DuplicateDetector()

        # Custom: within 1 hour
        detector_strict = DuplicateDetector(time_threshold_hours=1)

        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15, 10, 0),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15, 14, 0),  # 4 hours later
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
        ]

        # Default should catch (same day)
        assert len(detector_default.find_duplicates(transactions)) >= 1

        # Strict should not catch (4 hours apart)
        assert len(detector_strict.find_duplicates(transactions)) == 0

    def test_configurable_amount_threshold(self):
        """Amount threshold can be configured."""
        from analyze_fin.dedup.detector import DuplicateDetector

        # Strict: exact amount only
        detector_strict = DuplicateDetector(amount_threshold_percent=0)

        # Lenient: up to 5% difference
        detector_lenient = DuplicateDetector(amount_threshold_percent=5)

        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("103.00"),  # 3% difference
                "description": "JOLLIBEE",
            },
        ]

        # Strict should not catch
        assert len(detector_strict.find_duplicates(transactions)) == 0

        # Lenient should catch
        assert len(detector_lenient.find_duplicates(transactions)) >= 1


class TestBatchProcessing:
    """Test batch duplicate detection."""

    def test_find_duplicates_in_large_batch(self):
        """Efficiently process large batches."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()

        # Generate 100 unique transactions + 5 duplicates
        transactions = []
        base_date = datetime(2024, 1, 1)

        for i in range(100):
            transactions.append({
                "id": i,
                "date": base_date + timedelta(days=i),
                "amount": Decimal(str(100 + i)),
                "description": f"UNIQUE MERCHANT {i}",
            })

        # Add 5 exact duplicates
        for i in range(5):
            transactions.append({
                "id": 100 + i,
                "date": transactions[i]["date"],
                "amount": transactions[i]["amount"],
                "description": transactions[i]["description"],
            })

        duplicates = detector.find_duplicates(transactions)

        assert len(duplicates) == 5

    def test_returns_all_duplicate_pairs(self):
        """Returns all pairs of duplicates."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()

        # 3 identical transactions = 3 pairs
        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 3,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
        ]

        duplicates = detector.find_duplicates(transactions)

        # Should find pairs: (1,2), (1,3), (2,3)
        assert len(duplicates) == 3


class TestDuplicateGroups:
    """Test grouping of duplicates."""

    def test_group_duplicates(self):
        """group_duplicates clusters related transactions."""
        from analyze_fin.dedup.detector import DuplicateDetector

        detector = DuplicateDetector()

        transactions = [
            {
                "id": 1,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 2,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 3,
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "description": "JOLLIBEE",
            },
            {
                "id": 4,
                "date": datetime(2024, 1, 20),
                "amount": Decimal("200.00"),
                "description": "MCDONALDS",
            },
        ]

        groups = detector.group_duplicates(transactions)

        # Should have 1 group of 3 duplicates, transaction 4 not in any group
        assert len(groups) == 1
        assert len(groups[0]) == 3
