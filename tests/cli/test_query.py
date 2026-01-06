import json


class TestQueryCommand:
    """Test the query command."""

    def test_query_command_exits_successfully(self, runner, app, temp_db):
        result = runner.invoke(app, ["query"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_help_shows_options(self, runner, app):
        result = runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0
        assert "--category" in result.stdout
        assert "--merchant" in result.stdout
        assert "--date-range" in result.stdout

    def test_query_with_category_flag(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "--category", "Food & Dining"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_short_category_flag(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "-c", "Shopping"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_merchant_flag(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "--merchant", "Jollibee"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_short_merchant_flag(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "-m", "Grab"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_date_range_flag(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "--date-range", "November 2024"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_amount_min_flag(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "--amount-min", "500"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_amount_max_flag(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "--amount-max", "1000"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_format_flag_json(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "--format", "json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert "count" in output
        assert "transactions" in output
        assert output["count"] == 0

    def test_query_with_multiple_filters(self, runner, app, temp_db):
        result = runner.invoke(
            app,
            [
                "query",
                "--category",
                "Food & Dining",
                "--merchant",
                "Jollibee",
                "--amount-min",
                "100",
            ],
        )
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout


class TestCommandValidation:
    """Test command argument validation."""

    def test_invalid_command_shows_error(self, runner, app):
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0

    def test_query_rejects_invalid_format(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "--format", "invalid"])
        assert result.exit_code == 2
        assert "Invalid format" in result.stdout

    def test_query_rejects_invalid_amount_min(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "--amount-min", "abc"])
        assert result.exit_code == 2
        assert "Invalid amount-min" in result.stdout

    def test_query_rejects_invalid_date_range(self, runner, app, temp_db):
        result = runner.invoke(app, ["query", "--date-range", "invalid-date"])
        assert result.exit_code == 2
        assert "Unrecognized date range" in result.stdout


