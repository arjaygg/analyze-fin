"""
TDD Tests: Rule-based Transaction Categorizer

Story 2.2 AC: Rule-based categorizer using taxonomy and patterns.
RED phase - these tests will fail until categorizer.py is implemented.
"""

from datetime import datetime
from decimal import Decimal


class TestCategorizerStructure:
    """Test Categorizer class structure."""

    def test_categorizer_exists(self):
        """Categorizer can be imported."""
        from analyze_fin.categorization.categorizer import Categorizer

        assert Categorizer is not None

    def test_categorizer_can_instantiate(self):
        """Categorizer can be instantiated."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        assert categorizer is not None

    def test_categorizer_has_categorize_method(self):
        """Categorizer has categorize method."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        assert callable(categorizer.categorize)

    def test_categorizer_has_categorize_batch_method(self):
        """Categorizer has categorize_batch method."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        assert callable(categorizer.categorize_batch)


class TestCategorizationResult:
    """Test CategorizationResult data class."""

    def test_categorization_result_exists(self):
        """CategorizationResult can be imported."""
        from analyze_fin.categorization.categorizer import CategorizationResult

        assert CategorizationResult is not None

    def test_categorization_result_has_required_fields(self):
        """CategorizationResult has category, confidence, and method."""
        from analyze_fin.categorization.categorizer import CategorizationResult

        result = CategorizationResult(
            category="Food & Dining",
            confidence=0.95,
            method="merchant_mapping",
            merchant_normalized="Jollibee",
        )

        assert result.category == "Food & Dining"
        assert result.confidence == 0.95
        assert result.method == "merchant_mapping"
        assert result.merchant_normalized == "Jollibee"


class TestMerchantMappingCategorization:
    """Test categorization via direct merchant mapping."""

    def test_categorize_jollibee_returns_food_and_dining(self):
        """JOLLIBEE categorizes to Food & Dining."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("JOLLIBEE GREENBELT 3")

        assert result.category == "Food & Dining"
        assert result.confidence >= 0.9

    def test_categorize_grab_returns_transportation(self):
        """GRAB RIDE categorizes to Transportation."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("GRAB RIDE-9281728")

        assert result.category == "Transportation"
        assert result.confidence >= 0.9

    def test_categorize_lazada_returns_shopping(self):
        """LAZADA categorizes to Shopping."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("LAZADA ORDER #123456")

        assert result.category == "Shopping"
        assert result.confidence >= 0.9

    def test_categorize_meralco_returns_bills(self):
        """MERALCO categorizes to Bills & Utilities."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("MERALCO PAYMENT REF:12345")

        assert result.category == "Bills & Utilities"
        assert result.confidence >= 0.9

    def test_categorize_mercury_drug_returns_health(self):
        """MERCURY DRUG categorizes to Health & Wellness."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("MERCURY DRUG STORE")

        assert result.category == "Health & Wellness"
        assert result.confidence >= 0.9

    def test_categorize_is_case_insensitive(self):
        """Categorization is case-insensitive."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()

        assert categorizer.categorize("jollibee").category == "Food & Dining"
        assert categorizer.categorize("JOLLIBEE").category == "Food & Dining"
        assert categorizer.categorize("Jollibee").category == "Food & Dining"


class TestMerchantNormalization:
    """Test merchant name normalization in results."""

    def test_categorize_returns_normalized_merchant_name(self):
        """Result includes properly-cased merchant name."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("JOLLIBEE MAKATI")

        assert result.merchant_normalized == "Jollibee"

    def test_categorize_mcdonalds_variations(self):
        """McDonald's variations all normalize correctly."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()

        assert categorizer.categorize("MCDO").merchant_normalized == "McDonald's"
        assert categorizer.categorize("MCDONALDS").merchant_normalized == "McDonald's"
        assert categorizer.categorize("MCDONALD'S").merchant_normalized == "McDonald's"

    def test_unknown_merchant_has_none_normalized(self):
        """Unknown merchants have None for normalized name."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("RANDOM UNKNOWN STORE XYZ")

        assert result.merchant_normalized is None


class TestKeywordCategorization:
    """Test categorization via keyword matching."""

    def test_categorize_food_keyword(self):
        """Transactions with food keywords categorize correctly."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("RESTAURANT ABC MANILA")

        assert result.category == "Food & Dining"
        assert result.method == "keyword"
        assert result.confidence >= 0.7  # Lower confidence for keyword match

    def test_categorize_transport_keyword(self):
        """Transactions with transport keywords categorize correctly."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("TAXI RIDE 12345")

        assert result.category == "Transportation"

    def test_categorize_bill_keyword(self):
        """Transactions with bill keywords categorize correctly."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("ELECTRIC BILL PAYMENT")

        assert result.category == "Bills & Utilities"


class TestUncategorizedTransactions:
    """Test handling of uncategorizable transactions."""

    def test_unknown_transaction_returns_uncategorized(self):
        """Unknown transactions return Uncategorized."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("XYZABC123 RANDOM TEXT")

        assert result.category == "Uncategorized"

    def test_unknown_transaction_has_low_confidence(self):
        """Uncategorized transactions have zero confidence."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("TOTALLY UNKNOWN THING")

        assert result.confidence == 0.0

    def test_unknown_transaction_method_is_none(self):
        """Uncategorized transactions have None method."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("UNKNOWN RANDOM THING")

        assert result.method is None


class TestBatchCategorization:
    """Test batch categorization of multiple transactions."""

    def test_categorize_batch_returns_list(self):
        """categorize_batch returns list of results."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        descriptions = ["JOLLIBEE", "GRAB RIDE", "LAZADA"]

        results = categorizer.categorize_batch(descriptions)

        assert isinstance(results, list)
        assert len(results) == 3

    def test_categorize_batch_preserves_order(self):
        """Results maintain same order as input."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        descriptions = ["JOLLIBEE", "GRAB RIDE", "LAZADA"]

        results = categorizer.categorize_batch(descriptions)

        assert results[0].category == "Food & Dining"
        assert results[1].category == "Transportation"
        assert results[2].category == "Shopping"

    def test_categorize_batch_empty_list_returns_empty(self):
        """Empty input returns empty list."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        results = categorizer.categorize_batch([])

        assert results == []


class TestCategorizationMethod:
    """Test categorization method reporting."""

    def test_merchant_mapping_method(self):
        """Direct merchant match reports merchant_mapping method."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("JOLLIBEE")

        assert result.method == "merchant_mapping"

    def test_keyword_method(self):
        """Keyword match reports keyword method."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("RESTAURANT ABC")

        assert result.method == "keyword"


class TestCategorizationConfidence:
    """Test confidence scoring."""

    def test_exact_merchant_match_high_confidence(self):
        """Exact merchant match has highest confidence."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("JOLLIBEE")

        assert result.confidence >= 0.95

    def test_partial_merchant_match_medium_confidence(self):
        """Partial merchant match has medium confidence."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("JOLLIBEE GREENBELT BRANCH 123")

        assert 0.85 <= result.confidence <= 0.95

    def test_keyword_match_lower_confidence(self):
        """Keyword match has lower confidence."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("RESTAURANT XYZ")

        assert result.confidence >= 0.7
        assert result.confidence < 0.9


class TestSpecialCases:
    """Test special categorization cases."""

    def test_atm_withdrawal_categorizes_to_cash(self):
        """ATM WITHDRAWAL categorizes to Cash."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("ATM WITHDRAWAL 7-ELEVEN")

        assert result.category == "Cash"

    def test_cash_in_categorizes_to_cash(self):
        """CASH IN categorizes to Cash."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("CASH IN - SM MALL")

        assert result.category == "Cash"

    def test_transfer_categorizes_to_transfers(self):
        """TRANSFER categorizes to Transfers."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("TRANSFER TO JOHN DOE")

        assert result.category == "Transfers"

    def test_grabfood_categorizes_to_food_not_transport(self):
        """GRABFOOD categorizes to Food & Dining, not Transportation."""
        from analyze_fin.categorization.categorizer import Categorizer

        categorizer = Categorizer()
        result = categorizer.categorize("GRABFOOD - JOLLIBEE")

        assert result.category == "Food & Dining"
        assert result.merchant_normalized == "GrabFood"


class TestRawTransactionCategorization:
    """Test categorization of RawTransaction objects."""

    def test_categorize_raw_transaction(self):
        """Can categorize a RawTransaction object."""
        from analyze_fin.categorization.categorizer import Categorizer
        from analyze_fin.parsers.base import RawTransaction

        categorizer = Categorizer()
        transaction = RawTransaction(
            date=datetime.now(),
            description="JOLLIBEE GREENBELT",
            amount=Decimal("285.50"),
        )

        result = categorizer.categorize_transaction(transaction)

        assert result.category == "Food & Dining"
        assert result.merchant_normalized == "Jollibee"

    def test_categorize_raw_transactions_batch(self):
        """Can categorize a list of RawTransaction objects."""
        from analyze_fin.categorization.categorizer import Categorizer
        from analyze_fin.parsers.base import RawTransaction

        categorizer = Categorizer()
        transactions = [
            RawTransaction(
                date=datetime.now(),
                description="JOLLIBEE",
                amount=Decimal("285.50"),
            ),
            RawTransaction(
                date=datetime.now(),
                description="GRAB RIDE",
                amount=Decimal("150.00"),
            ),
        ]

        results = categorizer.categorize_transactions(transactions)

        assert len(results) == 2
        assert results[0].category == "Food & Dining"
        assert results[1].category == "Transportation"
