"""
ATDD Acceptance Tests: Merchant Categorization & Learning

Feature: Automatically categorize transactions and normalize merchant names
Story: FR14-20 - Categorization & Merchant Intelligence

These tests are INTENTIONALLY FAILING (RED phase) to guide implementation.
They define the expected behavior before any code is written.

Acceptance Criteria:
- AC1: Auto-categorize transactions using merchant mapping (>90% accuracy)
- AC2: Normalize merchant names across variations (JOLLIBEE GREENBELT → Jollibee)
- AC3: Handle unknown merchants gracefully (mark as "Uncategorized")
- AC4: Learn from user corrections and update mapping
- AC5: Persist learned mappings to data/merchant_mapping.json
- AC6: Support fuzzy matching for typos and variations
- AC7: Batch categorize multiple transactions efficiently

Test Status: 🔴 RED (Failing - awaiting implementation)
"""

import pytest
from pathlib import Path
from decimal import Decimal
import json

# These imports will fail until implementation exists
# from src.analyze_fin.categorization.categorizer import MerchantCategorizer
# from src.analyze_fin.categorization.normalizer import MerchantNormalizer
# from src.analyze_fin.categorization.learning import LearningEngine

from tests.support.helpers import assert_categorized


# ============================================================================
# AC1: Auto-categorize transactions using merchant mapping (>90% accuracy)
# ============================================================================

@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_categorize_known_merchant_assigns_correct_category(sample_merchant_mapping):
    """
    GIVEN a transaction with known merchant "JOLLIBEE"
    WHEN categorization is performed
    THEN category "Food & Dining" is assigned with high confidence (>0.90)

    Implementation Tasks:
    - [ ] Create MerchantCategorizer in src/analyze_fin/categorization/categorizer.py
    - [ ] Load merchant mapping from JSON file
    - [ ] Implement categorize() method
    - [ ] Return category and confidence score
    - [ ] Run: pytest tests/categorization/test_categorization_atdd.py::test_categorize_known_merchant_assigns_correct_category
    """
    pytest.skip("Implementation pending - awaiting MerchantCategorizer")

    # Expected implementation:
    # categorizer = MerchantCategorizer(sample_merchant_mapping)
    # transaction = {"description": "JOLLIBEE GREENBELT 3"}
    #
    # result = categorizer.categorize(transaction)
    #
    # assert result.category == "Food & Dining"
    # assert result.merchant_normalized == "Jollibee"
    # assert result.confidence >= 0.90


@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_categorize_multiple_merchants_achieves_90_percent_accuracy(sample_transactions):
    """
    GIVEN 100 transactions with known merchants
    WHEN batch categorization is performed
    THEN at least 90 transactions are correctly categorized

    Implementation Tasks:
    - [ ] Implement batch categorization
    - [ ] Measure categorization accuracy
    - [ ] Achieve >90% accuracy on test dataset
    """
    pytest.skip("Implementation pending - awaiting batch categorization")

    # Expected implementation:
    # categorizer = MerchantCategorizer.load_default_mapping()
    #
    # # Categorize all transactions
    # results = [categorizer.categorize(txn) for txn in sample_transactions]
    #
    # # Count correct categorizations (compare to ground truth)
    # correct_count = sum(1 for r in results if r.category == r.expected_category)
    # accuracy = correct_count / len(results)
    #
    # assert accuracy >= 0.90, f"Accuracy {accuracy:.2%} below 90% threshold"


# ============================================================================
# AC2: Normalize merchant names across variations
# ============================================================================

@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.unit
@pytest.mark.parametrize("description,expected_normalized", [
    ("JOLLIBEE GREENBELT 3", "Jollibee"),
    ("JOLLIBEE SM NORTH EDSA", "Jollibee"),
    ("JOLLIBEE - MAKATI BRANCH", "Jollibee"),
    ("7-ELEVEN STORE #1234", "7-Eleven"),
    ("7-11 STORE #5678", "7-Eleven"),
    ("SEVEN ELEVEN BGC", "7-Eleven"),
    ("GRAB - TRIP TO MAKATI", "Grab"),
    ("GRAB FOOD ORDER", "Grab"),
])
def test_normalize_merchant_name_across_variations(description, expected_normalized):
    """
    GIVEN merchant descriptions with location/branch variations
    WHEN normalization is performed
    THEN base merchant name is extracted correctly

    Implementation Tasks:
    - [ ] Create MerchantNormalizer in src/analyze_fin/categorization/normalizer.py
    - [ ] Implement normalize() method
    - [ ] Remove location suffixes (GREENBELT 3, SM NORTH, etc.)
    - [ ] Remove branch indicators (BRANCH, STORE #, etc.)
    - [ ] Standardize name format (Title Case)
    - [ ] Handle special cases (7-11 → 7-Eleven)
    """
    pytest.skip("Implementation pending - awaiting MerchantNormalizer")

    # Expected implementation:
    # normalizer = MerchantNormalizer()
    # normalized = normalizer.normalize(description)
    # assert normalized == expected_normalized


@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.unit
def test_normalize_preserves_merchant_identity():
    """
    GIVEN similar but distinct merchants
    WHEN normalization is performed
    THEN each merchant maintains unique identity

    Implementation Tasks:
    - [ ] Ensure normalization doesn't over-merge distinct merchants
    - [ ] Test edge cases: "SM Supermarket" vs "SM Department Store"
    """
    pytest.skip("Implementation pending - awaiting distinct merchant handling")

    # Expected implementation:
    # normalizer = MerchantNormalizer()
    #
    # assert normalizer.normalize("SM SUPERMARKET MAKATI") == "SM Supermarket"
    # assert normalizer.normalize("SM DEPARTMENT STORE") == "SM Department Store"
    # # These are different merchants - don't merge them!


# ============================================================================
# AC3: Handle unknown merchants gracefully
# ============================================================================

@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_categorize_unknown_merchant_returns_uncategorized():
    """
    GIVEN a transaction with unknown merchant
    WHEN categorization is performed
    THEN category "Uncategorized" is assigned with low confidence (<0.50)

    Implementation Tasks:
    - [ ] Handle missing merchant in mapping
    - [ ] Return "Uncategorized" as default category
    - [ ] Set confidence < 0.50 for unknown merchants
    - [ ] Log unknown merchant for review
    """
    pytest.skip("Implementation pending - awaiting unknown merchant handling")

    # Expected implementation:
    # categorizer = MerchantCategorizer({})  # Empty mapping
    # transaction = {"description": "UNKNOWN MERCHANT XYZ"}
    #
    # result = categorizer.categorize(transaction)
    #
    # assert result.category == "Uncategorized"
    # assert result.confidence < 0.50
    # assert result.merchant_normalized is None


@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_categorize_lists_unknown_merchants_for_user_review():
    """
    GIVEN multiple transactions with unknown merchants
    WHEN categorization is performed
    THEN unknown merchants are collected for user review

    Implementation Tasks:
    - [ ] Track unknown merchants during batch categorization
    - [ ] Return list of unique unknown merchant descriptions
    - [ ] Provide method to get_unknown_merchants()
    """
    pytest.skip("Implementation pending - awaiting unknown merchant tracking")

    # Expected implementation:
    # categorizer = MerchantCategorizer.load_default_mapping()
    # transactions = [
    #     {"description": "UNKNOWN SHOP A"},
    #     {"description": "UNKNOWN SHOP B"},
    #     {"description": "UNKNOWN SHOP A"},  # Duplicate
    # ]
    #
    # for txn in transactions:
    #     categorizer.categorize(txn)
    #
    # unknown = categorizer.get_unknown_merchants()
    #
    # assert len(unknown) == 2  # Unique merchants only
    # assert "UNKNOWN SHOP A" in unknown
    # assert "UNKNOWN SHOP B" in unknown


# ============================================================================
# AC4: Learn from user corrections and update mapping
# ============================================================================

@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_learn_from_user_correction_updates_mapping():
    """
    GIVEN an unknown merchant "NEW COFFEE SHOP"
    WHEN user corrects category to "Food & Dining"
    THEN mapping is updated and future occurrences are auto-categorized

    Implementation Tasks:
    - [ ] Create LearningEngine in src/analyze_fin/categorization/learning.py
    - [ ] Implement learn() method
    - [ ] Update in-memory merchant mapping
    - [ ] Apply learning to future categorizations
    """
    pytest.skip("Implementation pending - awaiting LearningEngine")

    # Expected implementation:
    # categorizer = MerchantCategorizer({})
    #
    # # First time - unknown
    # result1 = categorizer.categorize({"description": "NEW COFFEE SHOP"})
    # assert result1.category == "Uncategorized"
    #
    # # User corrects
    # categorizer.learn("NEW COFFEE SHOP", category="Food & Dining", normalized_name="New Coffee Shop")
    #
    # # Second time - should remember
    # result2 = categorizer.categorize({"description": "NEW COFFEE SHOP BRANCH 2"})
    # assert result2.category == "Food & Dining"
    # assert result2.merchant_normalized == "New Coffee Shop"
    # assert result2.confidence >= 0.80


@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_learn_applies_to_merchant_variations():
    """
    GIVEN a learned merchant mapping
    WHEN variations of the merchant are encountered
    THEN the learned category is applied

    Implementation Tasks:
    - [ ] Fuzzy match learned merchants to variations
    - [ ] Apply learned category to similar merchant names
    """
    pytest.skip("Implementation pending - awaiting variation matching")

    # Expected implementation:
    # categorizer = MerchantCategorizer({})
    # categorizer.learn("COFFEE PROJECT", category="Food & Dining")
    #
    # # Should match variations
    # result = categorizer.categorize({"description": "COFFEE PROJECT MAKATI"})
    # assert result.category == "Food & Dining"


# ============================================================================
# AC5: Persist learned mappings to data/merchant_mapping.json
# ============================================================================

@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_save_learned_mappings_to_json_file(temp_dir):
    """
    GIVEN new merchant mappings learned from user corrections
    WHEN save_mappings() is called
    THEN mappings are persisted to merchant_mapping.json file

    Implementation Tasks:
    - [ ] Implement save_mappings() method
    - [ ] Write to data/merchant_mapping.json (or temp path for tests)
    - [ ] Use JSON format with proper structure
    - [ ] Preserve existing mappings when adding new ones
    """
    pytest.skip("Implementation pending - awaiting save_mappings()")

    # Expected implementation:
    # mapping_file = temp_dir / "merchant_mapping.json"
    # categorizer = MerchantCategorizer({})
    #
    # # Learn new mappings
    # categorizer.learn("MERCHANT A", category="Shopping")
    # categorizer.learn("MERCHANT B", category="Food & Dining")
    #
    # # Save to file
    # categorizer.save_mappings(mapping_file)
    #
    # assert mapping_file.exists()
    #
    # # Verify file content
    # with open(mapping_file) as f:
    #     data = json.load(f)
    #
    # assert "MERCHANT A" in data
    # assert data["MERCHANT A"]["category"] == "Shopping"


@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_load_mappings_from_json_file(temp_dir):
    """
    GIVEN a merchant_mapping.json file with mappings
    WHEN MerchantCategorizer is initialized
    THEN mappings are loaded and available for categorization

    Implementation Tasks:
    - [ ] Implement load_from_file() class method
    - [ ] Read and parse JSON file
    - [ ] Initialize categorizer with loaded mappings
    """
    pytest.skip("Implementation pending - awaiting load_from_file()")

    # Expected implementation:
    # mapping_file = temp_dir / "merchant_mapping.json"
    # mapping_file.write_text(json.dumps({
    #     "JOLLIBEE": {
    #         "normalized": "Jollibee",
    #         "category": "Food & Dining"
    #     }
    # }))
    #
    # categorizer = MerchantCategorizer.load_from_file(mapping_file)
    # result = categorizer.categorize({"description": "JOLLIBEE GREENBELT"})
    #
    # assert result.category == "Food & Dining"


# ============================================================================
# AC6: Support fuzzy matching for typos and variations
# ============================================================================

@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.unit
@pytest.mark.parametrize("description,expected_match,min_confidence", [
    ("JOLIBEE GREENBELT", "Jollibee", 0.70),  # Typo (missing L)
    ("7ELEVEN STORE", "7-Eleven", 0.80),  # Missing hyphen
    ("GRAB FOOD", "Grab", 0.85),  # Partial match
])
def test_fuzzy_match_handles_typos_and_variations(description, expected_match, min_confidence):
    """
    GIVEN merchant descriptions with typos or variations
    WHEN fuzzy matching is performed
    THEN closest match is found with appropriate confidence score

    Implementation Tasks:
    - [ ] Implement fuzzy matching algorithm (Levenshtein distance or similar)
    - [ ] Set confidence based on similarity score
    - [ ] Return best match above similarity threshold (e.g., 70%)
    """
    pytest.skip("Implementation pending - awaiting fuzzy matching")

    # Expected implementation:
    # categorizer = MerchantCategorizer.load_default_mapping()
    # result = categorizer.categorize({"description": description})
    #
    # assert result.merchant_normalized == expected_match
    # assert result.confidence >= min_confidence


@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.unit
def test_fuzzy_match_confidence_decreases_with_similarity():
    """
    GIVEN varying degrees of typos
    WHEN fuzzy matching is performed
    THEN confidence score reflects match quality

    Implementation Tasks:
    - [ ] Confidence score scales with string similarity
    - [ ] Exact match: confidence = 1.0
    - [ ] Close match (1-2 typos): confidence = 0.80-0.95
    - [ ] Distant match: confidence < 0.70
    """
    pytest.skip("Implementation pending - awaiting confidence scaling")

    # Expected implementation:
    # categorizer = MerchantCategorizer({"JOLLIBEE": {...}})
    #
    # exact = categorizer.categorize({"description": "JOLLIBEE"})
    # assert exact.confidence >= 0.95
    #
    # close = categorizer.categorize({"description": "JOLIBEE"})  # 1 typo
    # assert 0.80 <= close.confidence < 0.95
    #
    # distant = categorizer.categorize({"description": "JOLBE"})  # Multiple typos
    # assert distant.confidence < 0.80


# ============================================================================
# AC7: Batch categorize multiple transactions efficiently
# ============================================================================

@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_batch_categorize_processes_100_transactions_under_1_second(sample_transactions):
    """
    GIVEN 100 transactions to categorize
    WHEN batch categorization is performed
    THEN all transactions are categorized in under 1 second

    Implementation Tasks:
    - [ ] Implement efficient batch processing
    - [ ] Optimize merchant lookup (use dict/hash map)
    - [ ] Avoid redundant normalization
    - [ ] Cache fuzzy match results
    """
    pytest.skip("Implementation pending - awaiting batch optimization")

    # Expected implementation:
    # import time
    #
    # categorizer = MerchantCategorizer.load_default_mapping()
    # transactions = sample_transactions[:100]  # First 100
    #
    # start = time.time()
    # results = categorizer.categorize_batch(transactions)
    # elapsed = time.time() - start
    #
    # assert len(results) == 100
    # assert elapsed < 1.0, f"Batch categorization took {elapsed:.2f}s (threshold: 1.0s)"


@pytest.mark.atdd
@pytest.mark.categorization
@pytest.mark.integration
def test_batch_categorize_returns_summary_statistics():
    """
    GIVEN batch categorization results
    WHEN summary is generated
    THEN statistics include: total, categorized, uncategorized, confidence distribution

    Implementation Tasks:
    - [ ] Implement get_summary() method
    - [ ] Count categorized vs uncategorized transactions
    - [ ] Calculate average confidence score
    - [ ] Group by category with counts
    """
    pytest.skip("Implementation pending - awaiting summary statistics")

    # Expected implementation:
    # categorizer = MerchantCategorizer.load_default_mapping()
    # transactions = generate_transactions(50)
    #
    # results = categorizer.categorize_batch(transactions)
    # summary = categorizer.get_summary(results)
    #
    # assert summary["total"] == 50
    # assert summary["categorized"] + summary["uncategorized"] == 50
    # assert "average_confidence" in summary
    # assert "by_category" in summary  # {"Food & Dining": 15, "Transportation": 8, ...}


# ============================================================================
# IMPLEMENTATION CHECKLIST
# ============================================================================

"""
## Red-Green-Refactor Implementation Guide

### RED Phase (Complete) ✅
- ✅ All tests written and failing
- ✅ Acceptance criteria mapped to tests
- ✅ Expected behavior defined

### GREEN Phase (DEV Team - Start Here) 🟢

#### Step 1: Create Base Structure
- [ ] Create src/analyze_fin/categorization/ directory
- [ ] Create src/analyze_fin/categorization/__init__.py
- [ ] Create data/merchant_mapping.json with initial Philippine merchants
- [ ] Add 150+ merchant mappings (Jollibee, 7-Eleven, SM, Mercury Drug, etc.)

#### Step 2: Implement MerchantCategorizer (Minimal)
- [ ] Create src/analyze_fin/categorization/categorizer.py
- [ ] Implement MerchantCategorizer class
- [ ] Implement categorize() method (exact match only, no fuzzy yet)
- [ ] Run test: test_categorize_known_merchant_assigns_correct_category
- [ ] ✅ Make test pass (green)

#### Step 3: Implement Merchant Normalization
- [ ] Create src/analyze_fin/categorization/normalizer.py
- [ ] Implement MerchantNormalizer class
- [ ] Implement normalize() method
- [ ] Handle location/branch removal
- [ ] Run tests: test_normalize_merchant_name_across_variations
- [ ] ✅ Make tests pass

#### Step 4: Handle Unknown Merchants
- [ ] Add "Uncategorized" default category
- [ ] Track unknown merchants in categorizer
- [ ] Implement get_unknown_merchants() method
- [ ] Run tests: test_categorize_unknown_merchant_*
- [ ] ✅ Make tests pass

#### Step 5: Implement Learning Engine
- [ ] Create src/analyze_fin/categorization/learning.py
- [ ] Implement LearningEngine class
- [ ] Implement learn() method
- [ ] Update in-memory mapping when user corrects
- [ ] Run tests: test_learn_from_user_correction_*
- [ ] ✅ Make tests pass

#### Step 6: Add Persistence
- [ ] Implement save_mappings() method
- [ ] Implement load_from_file() class method
- [ ] Use JSON format for storage
- [ ] Run tests: test_save_learned_mappings_*, test_load_mappings_*
- [ ] ✅ Make tests pass

#### Step 7: Add Fuzzy Matching
- [ ] Install fuzzywuzzy or similar library (pip install fuzzywuzzy python-Levenshtein)
- [ ] Implement fuzzy matching in categorize()
- [ ] Calculate confidence based on similarity
- [ ] Run tests: test_fuzzy_match_*
- [ ] ✅ Make tests pass

#### Step 8: Optimize Batch Processing
- [ ] Implement categorize_batch() method
- [ ] Optimize lookup performance (use dict)
- [ ] Cache fuzzy match results
- [ ] Run tests: test_batch_categorize_*
- [ ] ✅ Make tests pass

#### Step 9: Add Summary Statistics
- [ ] Implement get_summary() method
- [ ] Calculate categorization statistics
- [ ] Group by category with counts
- [ ] Run test: test_batch_categorize_returns_summary_statistics
- [ ] ✅ Make test pass

#### Step 10: Achieve 90% Accuracy
- [ ] Test categorizer with real Philippine merchant data
- [ ] Expand merchant_mapping.json if accuracy < 90%
- [ ] Tune fuzzy matching thresholds
- [ ] Run test: test_categorize_multiple_merchants_achieves_90_percent_accuracy
- [ ] ✅ Make test pass

### REFACTOR Phase (After All Tests Pass) ♻️
- [ ] Extract duplicate code
- [ ] Optimize string matching performance
- [ ] Add type hints
- [ ] Add docstrings
- [ ] Consider caching for frequently accessed merchants
- [ ] Run full test suite to ensure refactoring doesn't break tests

## Running Tests

```bash
# Run all categorization ATDD tests
pytest tests/categorization/test_categorization_atdd.py -v

# Run specific test
pytest tests/categorization/test_categorization_atdd.py::test_categorize_known_merchant_assigns_correct_category -v

# Run with markers
pytest -m "atdd and categorization" -v

# Skip slow tests during development
pytest tests/categorization/test_categorization_atdd.py -m "not slow" -v
```

## Expected Timeline

- Step 1-2: ~2 hours (base structure + categorizer)
- Step 3-4: ~2 hours (normalization + unknown handling)
- Steps 5-6: ~2 hours (learning + persistence)
- Steps 7-8: ~3 hours (fuzzy matching + batch optimization)
- Steps 9-10: ~2 hours (statistics + accuracy tuning)
- Refactor: ~1 hour

**Total: ~12 hours of focused development**

## Success Criteria

When all tests pass (green):
- ✅ Auto-categorizes transactions with >90% accuracy
- ✅ Normalizes merchant names across variations
- ✅ Handles unknown merchants gracefully
- ✅ Learns from user corrections
- ✅ Persists mappings to JSON file
- ✅ Supports fuzzy matching for typos
- ✅ Batch processes efficiently (<1s for 100 transactions)

## Initial Philippine Merchant Mapping

Create data/merchant_mapping.json with:

```json
{
  "JOLLIBEE": {"normalized": "Jollibee", "category": "Food & Dining"},
  "7-ELEVEN": {"normalized": "7-Eleven", "category": "Convenience Store"},
  "7-11": {"normalized": "7-Eleven", "category": "Convenience Store"},
  "SM SUPERMARKET": {"normalized": "SM Supermarket", "category": "Groceries"},
  "MERCURY DRUG": {"normalized": "Mercury Drug", "category": "Healthcare"},
  "GRAB": {"normalized": "Grab", "category": "Transportation"},
  "MCDONALDS": {"normalized": "McDonald's", "category": "Food & Dining"},
  "MINISTOP": {"normalized": "Ministop", "category": "Convenience Store"},
  "PUREGOLD": {"normalized": "Puregold", "category": "Groceries"},
  "SHOPEE": {"normalized": "Shopee", "category": "Online Shopping"},
  "LAZADA": {"normalized": "Lazada", "category": "Online Shopping"},
  "STARBUCKS": {"normalized": "Starbucks", "category": "Food & Dining"},
  "NATIONAL BOOKSTORE": {"normalized": "National Bookstore", "category": "Shopping"}
}
```

Add 140+ more merchants to reach 150+ total.
"""
