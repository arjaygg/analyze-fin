class TestCategorizeCommand:
    """Test the categorize command."""

    def test_categorize_help_shows_options(self, runner, app):
        result = runner.invoke(app, ["categorize", "--help"])
        assert result.exit_code == 0

    def test_categorize_with_empty_database(self, runner, app, temp_db):
        result = runner.invoke(app, ["categorize"])
        assert result.exit_code == 0
        assert "No" in result.stdout or "categoriz" in result.stdout.lower()


class TestDeduplicateCommand:
    """Test the deduplicate command."""

    def test_deduplicate_help_shows_options(self, runner, app):
        result = runner.invoke(app, ["deduplicate", "--help"])
        assert result.exit_code == 0

    def test_deduplicate_with_empty_database(self, runner, app, temp_db):
        result = runner.invoke(app, ["deduplicate"])
        assert result.exit_code == 0
        assert "No" in result.stdout or "duplicat" in result.stdout.lower()


