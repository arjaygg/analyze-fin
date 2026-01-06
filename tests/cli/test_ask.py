class TestAskCommand:
    """Test the ask command (natural language queries)."""

    def test_ask_help_shows_options(self, runner, app):
        result = runner.invoke(app, ["ask", "--help"])
        assert result.exit_code == 0
        assert "natural language" in result.stdout.lower() or "question" in result.stdout.lower()

    def test_ask_parses_category_query(self, runner, app, temp_db):
        result = runner.invoke(app, ["ask", "How much did I spend on food?"])
        assert result.exit_code == 0
        assert "Food & Dining" in result.stdout

    def test_ask_parses_total_intent(self, runner, app, temp_db):
        result = runner.invoke(app, ["ask", "How much did I spend?"])
        assert result.exit_code == 0
        assert "total" in result.stdout.lower()

    def test_ask_parses_date_range(self, runner, app, temp_db):
        result = runner.invoke(app, ["ask", "Show transactions last month"])
        assert result.exit_code == 0
        assert "From:" in result.stdout

    def test_ask_requires_question(self, runner, app):
        result = runner.invoke(app, ["ask"])
        assert result.exit_code != 0


