"""
TDD Tests: Duplicate Resolution

Story 3.2 AC: Resolve duplicate transactions (mark, ignore, merge).
RED phase - these tests will fail until resolver.py is implemented.
"""

import pytest
import json
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path


class TestDuplicateResolverStructure:
    """Test DuplicateResolver class structure."""

    def test_resolver_exists(self):
        """DuplicateResolver can be imported."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        assert DuplicateResolver is not None

    def test_resolver_can_instantiate(self):
        """DuplicateResolver can be instantiated."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        assert resolver is not None

    def test_resolver_has_mark_duplicate_method(self):
        """DuplicateResolver has mark_duplicate method."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        assert callable(resolver.mark_duplicate)

    def test_resolver_has_mark_unique_method(self):
        """DuplicateResolver has mark_unique method."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        assert callable(resolver.mark_unique)


class TestResolutionResult:
    """Test Resolution data class."""

    def test_resolution_exists(self):
        """Resolution can be imported."""
        from analyze_fin.dedup.resolver import Resolution

        assert Resolution is not None

    def test_resolution_has_required_fields(self):
        """Resolution has all required fields."""
        from analyze_fin.dedup.resolver import Resolution

        resolution = Resolution(
            transaction_ids=[1, 2],
            resolution_type="duplicate",
            keep_id=1,
            reason="User confirmed",
        )

        assert resolution.transaction_ids == [1, 2]
        assert resolution.resolution_type == "duplicate"
        assert resolution.keep_id == 1
        assert resolution.reason == "User confirmed"


class TestMarkDuplicate:
    """Test marking transactions as duplicates."""

    def test_mark_duplicate_stores_resolution(self):
        """mark_duplicate stores the resolution."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_duplicate(
            transaction_ids=[1, 2],
            keep_id=1,
            reason="Same transaction",
        )

        resolutions = resolver.get_resolutions()
        assert len(resolutions) == 1
        assert resolutions[0].resolution_type == "duplicate"

    def test_mark_duplicate_identifies_keeper(self):
        """mark_duplicate identifies which transaction to keep."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_duplicate(
            transaction_ids=[1, 2, 3],
            keep_id=2,
        )

        resolutions = resolver.get_resolutions()
        assert resolutions[0].keep_id == 2

    def test_mark_duplicate_with_multiple_ids(self):
        """mark_duplicate handles groups of 3+ duplicates."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_duplicate(
            transaction_ids=[1, 2, 3, 4],
            keep_id=1,
        )

        resolutions = resolver.get_resolutions()
        assert len(resolutions[0].transaction_ids) == 4


class TestMarkUnique:
    """Test marking transactions as unique (not duplicates)."""

    def test_mark_unique_stores_resolution(self):
        """mark_unique stores the resolution."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_unique(
            transaction_ids=[1, 2],
            reason="Different merchants",
        )

        resolutions = resolver.get_resolutions()
        assert len(resolutions) == 1
        assert resolutions[0].resolution_type == "unique"

    def test_mark_unique_no_keeper(self):
        """mark_unique has no keep_id (all are kept)."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_unique(transaction_ids=[1, 2])

        resolutions = resolver.get_resolutions()
        assert resolutions[0].keep_id is None


class TestGetDuplicateIds:
    """Test getting IDs of duplicate transactions."""

    def test_get_duplicate_ids_returns_non_keepers(self):
        """get_duplicate_ids returns IDs of non-kept duplicates."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_duplicate(
            transaction_ids=[1, 2, 3],
            keep_id=1,
        )

        duplicate_ids = resolver.get_duplicate_ids()
        assert 2 in duplicate_ids
        assert 3 in duplicate_ids
        assert 1 not in duplicate_ids

    def test_get_duplicate_ids_empty_initially(self):
        """get_duplicate_ids returns empty set initially."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        assert resolver.get_duplicate_ids() == set()


class TestCheckResolution:
    """Test checking resolution status."""

    def test_is_resolved_true_for_resolved(self):
        """is_resolved returns True for resolved transactions."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_duplicate(transaction_ids=[1, 2], keep_id=1)

        assert resolver.is_resolved(1)
        assert resolver.is_resolved(2)

    def test_is_resolved_false_for_unresolved(self):
        """is_resolved returns False for unresolved transactions."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()

        assert not resolver.is_resolved(999)

    def test_get_resolution_for_transaction(self):
        """get_resolution_for returns the resolution for a transaction."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_duplicate(
            transaction_ids=[1, 2],
            keep_id=1,
            reason="Test",
        )

        resolution = resolver.get_resolution_for(1)

        assert resolution is not None
        assert resolution.reason == "Test"


class TestPersistence:
    """Test saving and loading resolutions."""

    def test_save_resolutions(self):
        """save() writes resolutions to JSON file."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_duplicate(transaction_ids=[1, 2], keep_id=1)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            resolver.save(temp_path)
            assert temp_path.exists()

            content = json.loads(temp_path.read_text())
            assert "resolutions" in content
            assert len(content["resolutions"]) == 1
        finally:
            temp_path.unlink()

    def test_load_resolutions(self):
        """load() reads resolutions from JSON file."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver1 = DuplicateResolver()
        resolver1.mark_duplicate(transaction_ids=[1, 2], keep_id=1)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            resolver1.save(temp_path)

            resolver2 = DuplicateResolver()
            resolver2.load(temp_path)

            assert resolver2.is_resolved(1)
            assert resolver2.is_resolved(2)
        finally:
            temp_path.unlink()


class TestFilterDuplicates:
    """Test filtering out duplicate transactions."""

    def test_filter_removes_duplicates(self):
        """filter_transactions removes marked duplicates."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_duplicate(transaction_ids=[1, 2], keep_id=1)

        transactions = [
            {"id": 1, "amount": 100},
            {"id": 2, "amount": 100},
            {"id": 3, "amount": 200},
        ]

        filtered = resolver.filter_transactions(transactions)

        ids = [t["id"] for t in filtered]
        assert 1 in ids  # Kept
        assert 2 not in ids  # Removed (duplicate)
        assert 3 in ids  # Not involved in resolution

    def test_filter_keeps_all_if_marked_unique(self):
        """filter_transactions keeps all if marked unique."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_unique(transaction_ids=[1, 2])

        transactions = [
            {"id": 1, "amount": 100},
            {"id": 2, "amount": 100},
        ]

        filtered = resolver.filter_transactions(transactions)

        assert len(filtered) == 2


class TestAutoResolve:
    """Test automatic resolution of duplicates."""

    def test_auto_resolve_exact_duplicates(self):
        """auto_resolve automatically resolves exact duplicates."""
        from analyze_fin.dedup.resolver import DuplicateResolver
        from analyze_fin.dedup.detector import DuplicateDetector, DuplicateMatch

        resolver = DuplicateResolver()
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
        resolved = resolver.auto_resolve(duplicates, keep_first=True)

        assert resolved == 1  # 1 group auto-resolved
        assert resolver.is_resolved(1)
        assert resolver.is_resolved(2)

    def test_auto_resolve_keeps_first_by_default(self):
        """auto_resolve keeps first transaction by default."""
        from analyze_fin.dedup.resolver import DuplicateResolver
        from analyze_fin.dedup.detector import DuplicateMatch

        resolver = DuplicateResolver()

        # Create mock matches
        matches = [
            DuplicateMatch(
                transaction_a={"id": 10},
                transaction_b={"id": 20},
                confidence=0.99,
                match_type="exact",
                reasons=["Same"],
            )
        ]

        resolver.auto_resolve(matches, keep_first=True)

        # Should keep transaction 10 (first)
        duplicate_ids = resolver.get_duplicate_ids()
        assert 20 in duplicate_ids
        assert 10 not in duplicate_ids

    def test_auto_resolve_respects_threshold(self):
        """auto_resolve only resolves above confidence threshold."""
        from analyze_fin.dedup.resolver import DuplicateResolver
        from analyze_fin.dedup.detector import DuplicateMatch

        resolver = DuplicateResolver()

        matches = [
            DuplicateMatch(
                transaction_a={"id": 1},
                transaction_b={"id": 2},
                confidence=0.7,  # Below threshold
                match_type="near",
                reasons=["Similar"],
            )
        ]

        resolved = resolver.auto_resolve(matches, min_confidence=0.9)

        assert resolved == 0  # Not auto-resolved due to low confidence


class TestResolutionStats:
    """Test resolution statistics."""

    def test_get_stats(self):
        """get_stats returns resolution statistics."""
        from analyze_fin.dedup.resolver import DuplicateResolver

        resolver = DuplicateResolver()
        resolver.mark_duplicate(transaction_ids=[1, 2], keep_id=1)
        resolver.mark_duplicate(transaction_ids=[3, 4, 5], keep_id=3)
        resolver.mark_unique(transaction_ids=[6, 7])

        stats = resolver.get_stats()

        assert stats["total_resolutions"] == 3
        assert stats["duplicate_groups"] == 2
        assert stats["unique_groups"] == 1
        assert stats["total_duplicates_removed"] == 3  # 1 + 2
