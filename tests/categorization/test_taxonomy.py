"""
TDD Tests: Category Taxonomy

Story 2.1 AC: Category taxonomy with 150+ pre-mapped Philippine merchants.
RED phase - these tests will fail until taxonomy.py is implemented.
"""

import pytest


class TestCategoryDefinitions:
    """Test category definitions."""

    def test_categories_can_be_imported(self):
        """CATEGORIES constant can be imported."""
        from analyze_fin.categorization.taxonomy import CATEGORIES

        assert CATEGORIES is not None
        assert isinstance(CATEGORIES, dict)

    def test_has_minimum_required_categories(self):
        """Taxonomy has at least 10 categories."""
        from analyze_fin.categorization.taxonomy import CATEGORIES

        assert len(CATEGORIES) >= 10

    def test_has_food_and_dining_category(self):
        """Food & Dining category exists."""
        from analyze_fin.categorization.taxonomy import CATEGORIES

        assert "Food & Dining" in CATEGORIES

    def test_has_shopping_category(self):
        """Shopping category exists."""
        from analyze_fin.categorization.taxonomy import CATEGORIES

        assert "Shopping" in CATEGORIES

    def test_has_transportation_category(self):
        """Transportation category exists."""
        from analyze_fin.categorization.taxonomy import CATEGORIES

        assert "Transportation" in CATEGORIES

    def test_has_bills_and_utilities_category(self):
        """Bills & Utilities category exists."""
        from analyze_fin.categorization.taxonomy import CATEGORIES

        assert "Bills & Utilities" in CATEGORIES

    def test_categories_have_descriptions(self):
        """Each category has a description."""
        from analyze_fin.categorization.taxonomy import CATEGORIES

        for cat_name, cat_info in CATEGORIES.items():
            assert "description" in cat_info, f"{cat_name} missing description"

    def test_categories_have_keywords(self):
        """Each category has keywords for matching."""
        from analyze_fin.categorization.taxonomy import CATEGORIES

        for cat_name, cat_info in CATEGORIES.items():
            assert "keywords" in cat_info, f"{cat_name} missing keywords"
            assert isinstance(cat_info["keywords"], list)


class TestMerchantMapping:
    """Test pre-mapped Philippine merchants."""

    def test_merchant_mapping_can_be_imported(self):
        """MERCHANT_MAPPING can be imported."""
        from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING

        assert MERCHANT_MAPPING is not None
        assert isinstance(MERCHANT_MAPPING, dict)

    def test_has_minimum_merchants(self):
        """Has at least 100 pre-mapped merchants."""
        from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING

        assert len(MERCHANT_MAPPING) >= 100

    def test_jollibee_mapped_to_food(self):
        """JOLLIBEE is mapped to Food & Dining."""
        from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING

        # Merchant names are stored uppercase for matching
        jollibee_mapping = MERCHANT_MAPPING.get("JOLLIBEE")
        assert jollibee_mapping is not None
        assert jollibee_mapping["category"] == "Food & Dining"

    def test_mcdonalds_mapped_to_food(self):
        """MCDONALD'S is mapped to Food & Dining."""
        from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING

        # Try different variations
        found = False
        for key in MERCHANT_MAPPING:
            if "MCDONALD" in key:
                assert MERCHANT_MAPPING[key]["category"] == "Food & Dining"
                found = True
                break
        assert found, "McDonald's not found in merchant mapping"

    def test_grab_mapped_to_transportation(self):
        """GRAB is mapped to Transportation."""
        from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING

        for key in MERCHANT_MAPPING:
            if "GRAB" in key and "FOOD" not in key:
                assert MERCHANT_MAPPING[key]["category"] == "Transportation"
                return
        pytest.fail("GRAB not found in merchant mapping")

    def test_lazada_mapped_to_shopping(self):
        """LAZADA is mapped to Shopping."""
        from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING

        for key in MERCHANT_MAPPING:
            if "LAZADA" in key:
                assert MERCHANT_MAPPING[key]["category"] == "Shopping"
                return
        pytest.fail("LAZADA not found in merchant mapping")

    def test_shopee_mapped_to_shopping(self):
        """SHOPEE is mapped to Shopping."""
        from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING

        for key in MERCHANT_MAPPING:
            if "SHOPEE" in key:
                assert MERCHANT_MAPPING[key]["category"] == "Shopping"
                return
        pytest.fail("SHOPEE not found in merchant mapping")

    def test_meralco_mapped_to_bills(self):
        """MERALCO is mapped to Bills & Utilities."""
        from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING

        for key in MERCHANT_MAPPING:
            if "MERALCO" in key:
                assert MERCHANT_MAPPING[key]["category"] == "Bills & Utilities"
                return
        pytest.fail("MERALCO not found in merchant mapping")

    def test_merchant_mapping_has_normalized_names(self):
        """Merchant mappings include normalized display names."""
        from analyze_fin.categorization.taxonomy import MERCHANT_MAPPING

        for raw_name, mapping in MERCHANT_MAPPING.items():
            assert "normalized" in mapping, f"{raw_name} missing normalized name"
            assert "category" in mapping, f"{raw_name} missing category"


class TestCategoryLookup:
    """Test category lookup functions."""

    def test_get_category_exists(self):
        """get_category function exists."""
        from analyze_fin.categorization.taxonomy import get_category

        assert callable(get_category)

    def test_get_category_returns_food_for_jollibee(self):
        """get_category returns Food & Dining for JOLLIBEE."""
        from analyze_fin.categorization.taxonomy import get_category

        category = get_category("JOLLIBEE")
        assert category == "Food & Dining"

    def test_get_category_case_insensitive(self):
        """get_category is case-insensitive."""
        from analyze_fin.categorization.taxonomy import get_category

        assert get_category("jollibee") == "Food & Dining"
        assert get_category("JOLLIBEE") == "Food & Dining"
        assert get_category("Jollibee") == "Food & Dining"

    def test_get_category_returns_none_for_unknown(self):
        """get_category returns None for unknown merchants."""
        from analyze_fin.categorization.taxonomy import get_category

        result = get_category("UNKNOWN_MERCHANT_XYZ_123")
        assert result is None

    def test_get_normalized_name_exists(self):
        """get_normalized_name function exists."""
        from analyze_fin.categorization.taxonomy import get_normalized_name

        assert callable(get_normalized_name)

    def test_get_normalized_name_returns_proper_case(self):
        """get_normalized_name returns proper case."""
        from analyze_fin.categorization.taxonomy import get_normalized_name

        assert get_normalized_name("JOLLIBEE") == "Jollibee"
        assert get_normalized_name("jollibee") == "Jollibee"
