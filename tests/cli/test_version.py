class TestVersionCommand:
    """Test the version command."""

    def test_version_command_exits_successfully(self, runner, app):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0

    def test_version_command_shows_app_name(self, runner, app):
        result = runner.invoke(app, ["version"])
        assert "analyze-fin" in result.stdout

    def test_version_command_shows_version_number(self, runner, app):
        result = runner.invoke(app, ["version"])
        assert "0.1.0" in result.stdout


