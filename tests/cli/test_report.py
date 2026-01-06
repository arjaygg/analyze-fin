class TestReportCommand:
    """Test the report command."""

    def test_report_help_shows_options(self, runner, app):
        result = runner.invoke(app, ["report", "--help"])
        assert result.exit_code == 0
        assert "--format" in result.stdout or "--output" in result.stdout

    def test_report_with_empty_database(self, runner, app, temp_db):
        result = runner.invoke(app, ["report"])
        # Should succeed but note no transactions
        assert result.exit_code == 0
        assert "No transactions" in result.stdout or "report" in result.stdout.lower()


