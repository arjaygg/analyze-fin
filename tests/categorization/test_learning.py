"""
TDD Tests: Interactive Learning for Categorization

Story 2.4 AC: Learn from user corrections and custom mappings.
RED phase - these tests will fail until learning.py is implemented.
"""

import json
import tempfile
from pathlib import Path


class TestCategoryLearnerStructure:
    """Test CategoryLearner class structure."""

    def test_learner_exists(self):
        """CategoryLearner can be imported."""
        from analyze_fin.categorization.learning import CategoryLearner

        assert CategoryLearner is not None

    def test_learner_can_instantiate(self):
        """CategoryLearner can be instantiated."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        assert learner is not None

    def test_learner_has_learn_method(self):
        """CategoryLearner has learn method."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        assert callable(learner.learn)

    def test_learner_has_get_rules_method(self):
        """CategoryLearner has get_rules method."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        assert callable(learner.get_rules)


class TestLearnedRule:
    """Test LearnedRule data class."""

    def test_learned_rule_exists(self):
        """LearnedRule can be imported."""
        from analyze_fin.categorization.learning import LearnedRule

        assert LearnedRule is not None

    def test_learned_rule_has_required_fields(self):
        """LearnedRule has all required fields."""
        from analyze_fin.categorization.learning import LearnedRule

        rule = LearnedRule(
            pattern="SARI SARI STORE",
            category="Shopping",
            merchant_normalized="Local Store",
            source="user",
            confidence=1.0,
        )

        assert rule.pattern == "SARI SARI STORE"
        assert rule.category == "Shopping"
        assert rule.merchant_normalized == "Local Store"
        assert rule.source == "user"
        assert rule.confidence == 1.0


class TestLearning:
    """Test learning from user corrections."""

    def test_learn_new_merchant_category(self):
        """Learn category for new merchant."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn(
            description="SARI SARI STORE MARIA",
            category="Shopping",
            merchant_normalized="Maria's Store",
        )

        rules = learner.get_rules()
        assert len(rules) == 1
        assert rules[0].category == "Shopping"

    def test_learn_overwrites_existing_rule(self):
        """Learning updates existing rule for same pattern."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()

        learner.learn("TEST STORE", category="Shopping")
        learner.learn("TEST STORE", category="Groceries")

        rules = learner.get_rules()
        # Should only have one rule for the pattern
        matching = [r for r in rules if "TEST STORE" in r.pattern]
        assert len(matching) == 1
        assert matching[0].category == "Groceries"

    def test_learn_multiple_merchants(self):
        """Learn multiple distinct merchants."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()

        learner.learn("STORE A", category="Shopping")
        learner.learn("STORE B", category="Groceries")
        learner.learn("STORE C", category="Food & Dining")

        rules = learner.get_rules()
        assert len(rules) == 3


class TestLearnerApply:
    """Test applying learned rules to categorization."""

    def test_apply_returns_learned_category(self):
        """apply() returns learned category for matching description."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("LOCAL SHOP", category="Shopping")

        result = learner.apply("LOCAL SHOP")

        assert result is not None
        assert result.category == "Shopping"

    def test_apply_returns_none_for_unknown(self):
        """apply() returns None for unlearned description."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()

        result = learner.apply("UNKNOWN THING")

        assert result is None

    def test_apply_is_case_insensitive(self):
        """apply() matches case-insensitively."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("LOCAL SHOP", category="Shopping")

        assert learner.apply("local shop") is not None
        assert learner.apply("LOCAL SHOP") is not None
        assert learner.apply("Local Shop") is not None

    def test_apply_partial_match(self):
        """apply() matches partial descriptions."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("SARI SARI", category="Shopping")

        result = learner.apply("SARI SARI STORE MARIA BRANCH 2")

        assert result is not None
        assert result.category == "Shopping"


class TestPersistence:
    """Test saving and loading learned rules."""

    def test_save_rules_to_file(self):
        """save() writes rules to JSON file."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("TEST", category="Shopping")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            learner.save(temp_path)
            assert temp_path.exists()

            content = json.loads(temp_path.read_text())
            assert "rules" in content
            assert len(content["rules"]) == 1
        finally:
            temp_path.unlink()

    def test_load_rules_from_file(self):
        """load() reads rules from JSON file."""
        from analyze_fin.categorization.learning import CategoryLearner

        # Create a learner and save
        learner1 = CategoryLearner()
        learner1.learn("SAVED MERCHANT", category="Shopping")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            learner1.save(temp_path)

            # Load into new learner
            learner2 = CategoryLearner()
            learner2.load(temp_path)

            result = learner2.apply("SAVED MERCHANT")
            assert result is not None
            assert result.category == "Shopping"
        finally:
            temp_path.unlink()

    def test_load_merges_with_existing(self):
        """load() merges with existing rules."""
        from analyze_fin.categorization.learning import CategoryLearner

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Save initial rules
            learner1 = CategoryLearner()
            learner1.learn("MERCHANT A", category="Shopping")
            learner1.save(temp_path)

            # Create learner with different rule, then load
            learner2 = CategoryLearner()
            learner2.learn("MERCHANT B", category="Groceries")
            learner2.load(temp_path)

            # Should have both rules
            rules = learner2.get_rules()
            patterns = [r.pattern for r in rules]
            assert "MERCHANT A" in patterns
            assert "MERCHANT B" in patterns
        finally:
            temp_path.unlink()


class TestIntegrationWithCategorizer:
    """Test integration with Categorizer."""

    def test_create_categorizer_with_learner(self):
        """Categorizer can be initialized with a learner."""
        from analyze_fin.categorization.categorizer import Categorizer
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        categorizer = Categorizer(learner=learner)

        assert categorizer is not None

    def test_categorizer_uses_learned_rules(self):
        """Categorizer applies learned rules before defaults."""
        from analyze_fin.categorization.categorizer import Categorizer
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        # Override default categorization
        learner.learn("GRAB", category="Food & Dining", merchant_normalized="Grab Meals")

        categorizer = Categorizer(learner=learner)
        result = categorizer.categorize("GRAB")

        # Should use learned rule instead of default (Transportation)
        assert result.category == "Food & Dining"
        assert result.merchant_normalized == "Grab Meals"

    def test_categorizer_falls_back_to_defaults(self):
        """Categorizer uses defaults when no learned rule matches."""
        from analyze_fin.categorization.categorizer import Categorizer
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("CUSTOM STORE", category="Shopping")

        categorizer = Categorizer(learner=learner)
        result = categorizer.categorize("JOLLIBEE")

        # Should use default mapping
        assert result.category == "Food & Dining"


class TestRuleMetadata:
    """Test rule metadata tracking."""

    def test_rule_has_created_timestamp(self):
        """Rules track when they were created."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("TEST", category="Shopping")

        rules = learner.get_rules()
        assert rules[0].created_at is not None

    def test_rule_has_source(self):
        """Rules track their source."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("TEST", category="Shopping", source="manual")

        rules = learner.get_rules()
        assert rules[0].source == "manual"

    def test_default_source_is_user(self):
        """Default source is 'user'."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("TEST", category="Shopping")

        rules = learner.get_rules()
        assert rules[0].source == "user"


class TestBulkLearning:
    """Test bulk learning operations."""

    def test_learn_batch(self):
        """learn_batch() learns multiple rules at once."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()

        corrections = [
            {"description": "STORE A", "category": "Shopping"},
            {"description": "STORE B", "category": "Groceries"},
            {"description": "STORE C", "category": "Food & Dining"},
        ]

        learner.learn_batch(corrections)

        rules = learner.get_rules()
        assert len(rules) == 3

    def test_learn_batch_returns_count(self):
        """learn_batch() returns count of rules learned."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()

        corrections = [
            {"description": "A", "category": "Shopping"},
            {"description": "B", "category": "Shopping"},
        ]

        count = learner.learn_batch(corrections)

        assert count == 2


class TestRuleManagement:
    """Test rule management operations."""

    def test_delete_rule(self):
        """delete_rule() removes a learned rule."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("TO DELETE", category="Shopping")
        learner.learn("TO KEEP", category="Groceries")

        learner.delete_rule("TO DELETE")

        rules = learner.get_rules()
        patterns = [r.pattern for r in rules]
        assert "TO DELETE" not in patterns
        assert "TO KEEP" in patterns

    def test_clear_all_rules(self):
        """clear() removes all learned rules."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        learner.learn("A", category="Shopping")
        learner.learn("B", category="Groceries")
        learner.learn("C", category="Food & Dining")

        learner.clear()

        rules = learner.get_rules()
        assert len(rules) == 0

    def test_count_rules(self):
        """count() returns number of rules."""
        from analyze_fin.categorization.learning import CategoryLearner

        learner = CategoryLearner()
        assert learner.count() == 0

        learner.learn("A", category="Shopping")
        assert learner.count() == 1

        learner.learn("B", category="Shopping")
        assert learner.count() == 2
