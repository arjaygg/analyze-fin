class TestHelpCommand:
    """Test help output."""

    def test_help_flag_exits_successfully(self, runner, app):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_usage(self, runner, app):
        result = runner.invoke(app, ["--help"])
        assert "Usage:" in result.stdout

    def test_help_shows_commands(self, runner, app):
        result = runner.invoke(app, ["--help"])
        # Typer with Rich uses box formatting, so look for "Commands" (not "Commands:")
        assert "Commands" in result.stdout
        assert "query" in result.stdout
        assert "version" in result.stdout

    def test_help_shows_app_description(self, runner, app):
        result = runner.invoke(app, ["--help"])
        assert "Philippine" in result.stdout or "Finance" in result.stdout


class TestNoArgsShowsHelp:
    """Test that running without args shows help."""

    def test_no_args_shows_help(self, runner, app):
        result = runner.invoke(app, [])
        # With no_args_is_help=True, Typer returns exit code 0 or 2 depending on version
        # The important thing is that help is shown
        assert "Usage:" in result.stdout
        assert "Commands" in result.stdout


