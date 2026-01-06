import json


class TestExportCommand:
    """Test the export command."""

    def test_export_help_shows_options(self, runner, app):
        result = runner.invoke(app, ["export", "--help"])
        assert result.exit_code == 0
        assert "--format" in result.stdout

    def test_export_csv_format(self, runner, app, temp_db):
        result = runner.invoke(app, ["export", "--format", "csv"])
        assert result.exit_code == 0
        # Should have CSV header
        assert "date" in result.stdout or "No transactions" in result.stdout

    def test_export_json_format(self, runner, app, temp_db):
        result = runner.invoke(app, ["export", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list), "JSON output should be an array of transactions"


