"""
TDD Tests: Merchant Name Normalizer

Story 2.3 AC: Merchant normalization with fuzzy matching.
RED phase - these tests will fail until normalizer.py is implemented.
"""



class TestNormalizerStructure:
    """Test MerchantNormalizer class structure."""

    def test_normalizer_exists(self):
        """MerchantNormalizer can be imported."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        assert MerchantNormalizer is not None

    def test_normalizer_can_instantiate(self):
        """MerchantNormalizer can be instantiated."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        assert normalizer is not None

    def test_normalizer_has_normalize_method(self):
        """MerchantNormalizer has normalize method."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        assert callable(normalizer.normalize)

    def test_normalizer_has_extract_merchant_method(self):
        """MerchantNormalizer has extract_merchant method."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        assert callable(normalizer.extract_merchant)


class TestNormalizationResult:
    """Test NormalizationResult data class."""

    def test_normalization_result_exists(self):
        """NormalizationResult can be imported."""
        from analyze_fin.categorization.normalizer import NormalizationResult

        assert NormalizationResult is not None

    def test_normalization_result_has_required_fields(self):
        """NormalizationResult has all required fields."""
        from analyze_fin.categorization.normalizer import NormalizationResult

        result = NormalizationResult(
            original="JOLLIBEE GREENBELT 3",
            normalized="Jollibee",
            confidence=0.95,
            match_type="exact",
        )

        assert result.original == "JOLLIBEE GREENBELT 3"
        assert result.normalized == "Jollibee"
        assert result.confidence == 0.95
        assert result.match_type == "exact"


class TestExactMatching:
    """Test exact merchant name matching."""

    def test_normalize_jollibee(self):
        """JOLLIBEE normalizes to Jollibee."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("JOLLIBEE")

        assert result.normalized == "Jollibee"
        assert result.confidence >= 0.95

    def test_normalize_is_case_insensitive(self):
        """Normalization is case-insensitive."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()

        assert normalizer.normalize("jollibee").normalized == "Jollibee"
        assert normalizer.normalize("JOLLIBEE").normalized == "Jollibee"
        assert normalizer.normalize("Jollibee").normalized == "Jollibee"

    def test_normalize_handles_whitespace(self):
        """Handles leading/trailing whitespace."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()

        assert normalizer.normalize("  JOLLIBEE  ").normalized == "Jollibee"


class TestVariationMatching:
    """Test matching of merchant name variations."""

    def test_mcdonalds_variations(self):
        """All McDonald's variations normalize correctly."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()

        assert normalizer.normalize("MCDO").normalized == "McDonald's"
        assert normalizer.normalize("MCDONALDS").normalized == "McDonald's"
        assert normalizer.normalize("MCDONALD'S").normalized == "McDonald's"
        assert normalizer.normalize("MC DONALDS").normalized == "McDonald's"

    def test_seveneleven_variations(self):
        """All 7-Eleven variations normalize correctly."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()

        assert normalizer.normalize("7-ELEVEN").normalized == "7-Eleven"
        assert normalizer.normalize("7 ELEVEN").normalized == "7-Eleven"
        assert normalizer.normalize("7ELEVEN").normalized == "7-Eleven"

    def test_grab_variations(self):
        """All Grab variations normalize correctly."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()

        assert normalizer.normalize("GRAB").normalized == "Grab"
        assert normalizer.normalize("GRAB RIDE").normalized == "Grab"
        assert normalizer.normalize("GRABCAR").normalized == "GrabCar"
        assert normalizer.normalize("GRABFOOD").normalized == "GrabFood"


class TestMerchantExtraction:
    """Test extracting merchant names from descriptions."""

    def test_extract_from_description_with_branch(self):
        """Extract merchant from description with branch name."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.extract_merchant("JOLLIBEE GREENBELT 3")

        assert result.normalized == "Jollibee"

    def test_extract_from_description_with_order_number(self):
        """Extract merchant from description with order number."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.extract_merchant("LAZADA ORDER #12345678")

        assert result.normalized == "Lazada"

    def test_extract_from_description_with_reference(self):
        """Extract merchant from description with reference."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.extract_merchant("GRAB RIDE-12345")

        assert result.normalized == "Grab"

    def test_extract_from_description_with_location(self):
        """Extract merchant from description with location."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.extract_merchant("STARBUCKS BGC UPTOWN")

        assert result.normalized == "Starbucks"

    def test_extract_handles_all_caps(self):
        """Extract from ALL CAPS descriptions."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.extract_merchant("MERCURY DRUG STORE SM MALL OF ASIA")

        assert result.normalized == "Mercury Drug"


class TestPartialMatching:
    """Test partial/fuzzy merchant matching."""

    def test_partial_match_jollibee_with_suffix(self):
        """Partial match Jollibee with suffix."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("JOLLIBEE MAKATI AYALA")

        assert result.normalized == "Jollibee"
        assert result.match_type == "partial"

    def test_partial_match_lower_confidence(self):
        """Partial matches have lower confidence than exact."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()

        exact = normalizer.normalize("JOLLIBEE")
        partial = normalizer.normalize("JOLLIBEE BRANCH 123 MAKATI")

        assert exact.confidence > partial.confidence

    def test_no_match_returns_none(self):
        """Unknown merchants return None normalized."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("UNKNOWN RANDOM STORE XYZ123")

        assert result.normalized is None
        assert result.confidence == 0.0


class TestBatchNormalization:
    """Test batch normalization."""

    def test_normalize_batch_returns_list(self):
        """normalize_batch returns list of results."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        descriptions = ["JOLLIBEE", "GRAB RIDE", "LAZADA"]

        results = normalizer.normalize_batch(descriptions)

        assert isinstance(results, list)
        assert len(results) == 3

    def test_normalize_batch_preserves_order(self):
        """Results maintain same order as input."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        descriptions = ["JOLLIBEE", "GRAB RIDE", "LAZADA"]

        results = normalizer.normalize_batch(descriptions)

        assert results[0].normalized == "Jollibee"
        assert results[1].normalized == "Grab"
        assert results[2].normalized == "Lazada"

    def test_normalize_batch_empty_list(self):
        """Empty input returns empty list."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        results = normalizer.normalize_batch([])

        assert results == []


class TestCustomMappings:
    """Test adding custom merchant mappings."""

    def test_add_custom_mapping(self):
        """Can add custom merchant mapping."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        normalizer.add_mapping("SARI SARI STORE MARIA", "Maria's Store")

        result = normalizer.normalize("SARI SARI STORE MARIA")

        assert result.normalized == "Maria's Store"

    def test_custom_mapping_persists(self):
        """Custom mapping persists across calls."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        normalizer.add_mapping("LOCAL STORE 123", "Local Store")

        result1 = normalizer.normalize("LOCAL STORE 123")
        result2 = normalizer.normalize("LOCAL STORE 123")

        assert result1.normalized == "Local Store"
        assert result2.normalized == "Local Store"


class TestMatchTypes:
    """Test different match type reporting."""

    def test_exact_match_type(self):
        """Exact matches report 'exact' type."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("JOLLIBEE")

        assert result.match_type == "exact"

    def test_partial_match_type(self):
        """Partial matches report 'partial' type."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("JOLLIBEE MAKATI BRANCH 5")

        assert result.match_type == "partial"

    def test_no_match_type(self):
        """No matches report None type."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("RANDOM UNKNOWN XYZ")

        assert result.match_type is None


class TestSpecialCharacters:
    """Test handling of special characters."""

    def test_handles_ampersand(self):
        """Handles & in merchant names."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("S&R")

        assert result.normalized == "S&R"

    def test_handles_apostrophe(self):
        """Handles apostrophe in merchant names."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("SHAKEY'S")

        assert result.normalized == "Shakey's"

    def test_handles_hyphen(self):
        """Handles hyphen in merchant names."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("7-ELEVEN")

        assert result.normalized == "7-Eleven"

    def test_handles_period(self):
        """Handles period in merchant names."""
        from analyze_fin.categorization.normalizer import MerchantNormalizer

        normalizer = MerchantNormalizer()
        result = normalizer.normalize("COINS.PH")

        assert result.normalized == "Coins.ph"
