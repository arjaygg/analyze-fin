"""Tests for configuration system (Story 4.2)."""

from pathlib import Path

import pytest
import yaml

from analyze_fin.config import ConfigManager, get_config
from analyze_fin.config.defaults import DEFAULT_CONFIG, DEFAULT_CONFIG_TEMPLATE
from analyze_fin.exceptions import ConfigError


class TestConfigManager:
    """Tests for ConfigManager class."""

    def test_creates_default_config_when_none_exists(self, tmp_path: Path) -> None:
        """AC2: Auto-generate default config file on first run."""
        config_path = tmp_path / "config.yaml"
        manager = ConfigManager(config_path)

        # Config doesn't exist yet
        assert not config_path.exists()

        # Loading triggers creation
        manager.load()

        # Config file should now exist
        assert config_path.exists()

        # Verify content is valid YAML with expected sections
        with open(config_path) as f:
            content = yaml.safe_load(f)
        assert "database" in content
        assert "output" in content
        assert "categorization" in content

    def test_config_file_has_comments(self, tmp_path: Path) -> None:
        """AC2: Config includes comments explaining each setting."""
        config_path = tmp_path / "config.yaml"
        manager = ConfigManager(config_path)
        manager.create_default()

        with open(config_path) as f:
            content = f.read()

        # Verify comments exist
        assert "# analyze-fin configuration" in content
        assert "# Path to SQLite database file" in content
        assert "# Default output format" in content

    def test_loads_user_config(self, tmp_path: Path) -> None:
        """Config file values are loaded correctly."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            """\
database:
  path: /custom/path/db.sqlite
output:
  format: json
"""
        )

        manager = ConfigManager(config_path)
        config = manager.load()

        assert config["database"]["path"] == "/custom/path/db.sqlite"
        assert config["output"]["format"] == "json"

    def test_merges_with_defaults(self, tmp_path: Path) -> None:
        """Partial config merges with defaults."""
        config_path = tmp_path / "config.yaml"
        # Only specify one value
        config_path.write_text("output:\n  format: csv\n")

        manager = ConfigManager(config_path)
        config = manager.load()

        # User value
        assert config["output"]["format"] == "csv"
        # Defaults preserved
        assert config["output"]["color"] is True
        assert config["categorization"]["auto_categorize"] is True

    def test_invalid_yaml_raises_config_error(self, tmp_path: Path) -> None:
        """AC9: Invalid YAML syntax raises ConfigError."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("invalid: yaml: syntax: [")

        manager = ConfigManager(config_path)
        with pytest.raises(ConfigError) as exc_info:
            manager.load()

        assert "Invalid YAML" in str(exc_info.value)

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """AC4: Directory is created if it doesn't exist."""
        config_path = tmp_path / "nested" / "deep" / "config.yaml"
        manager = ConfigManager(config_path)
        manager.create_default()

        assert config_path.exists()
        assert config_path.parent.exists()


class TestConfigGet:
    """Tests for ConfigManager.get() with override precedence."""

    def test_cli_override_has_highest_precedence(self, tmp_path: Path) -> None:
        """AC8: CLI flags take precedence over config file."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("output:\n  format: json\n")

        manager = ConfigManager(config_path)
        value = manager.get("output.format", cli_override="csv")

        assert value == "csv"

    def test_env_var_overrides_config(self, tmp_path: Path, monkeypatch) -> None:
        """AC8: Environment variables override config file."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("output:\n  format: pretty\n")
        monkeypatch.setenv("ANALYZE_FIN_OUTPUT_FORMAT", "json")

        manager = ConfigManager(config_path)
        value = manager.get("output.format")

        assert value == "json"

    def test_config_overrides_defaults(self, tmp_path: Path) -> None:
        """AC8: Config file overrides defaults."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("output:\n  format: csv\n")

        manager = ConfigManager(config_path)
        value = manager.get("output.format")

        assert value == "csv"

    def test_defaults_used_when_not_specified(self, tmp_path: Path) -> None:
        """AC8: Defaults used when nothing else specified."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("")  # Empty config

        manager = ConfigManager(config_path)
        value = manager.get("output.format")

        assert value == DEFAULT_CONFIG["output"]["format"]

    def test_nested_key_access(self, tmp_path: Path) -> None:
        """Dot notation accesses nested values."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("banks:\n  bpi:\n    password_pattern: '^\\d{6}$'\n")

        manager = ConfigManager(config_path)
        value = manager.get("banks.bpi.password_pattern")

        assert value == "^\\d{6}$"

    def test_env_var_type_conversion_bool(self, tmp_path: Path, monkeypatch) -> None:
        """Environment variable strings converted to correct types."""
        config_path = tmp_path / "config.yaml"
        manager = ConfigManager(config_path)
        monkeypatch.setenv("ANALYZE_FIN_OUTPUT_COLOR", "false")

        value = manager.get("output.color")

        assert value is False

    def test_env_var_type_conversion_float(self, tmp_path: Path, monkeypatch) -> None:
        """Environment variable strings converted to float."""
        config_path = tmp_path / "config.yaml"
        manager = ConfigManager(config_path)
        monkeypatch.setenv("ANALYZE_FIN_CATEGORIZATION_CONFIDENCE_THRESHOLD", "0.95")

        value = manager.get("categorization.confidence_threshold")

        assert value == 0.95


class TestConvenienceMethods:
    """Tests for typed convenience methods."""

    def test_get_database_path_expands_tilde(self, tmp_path: Path) -> None:
        """AC4: Path expansion for ~ to home directory."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("database:\n  path: ~/mydata/app.db\n")

        manager = ConfigManager(config_path)
        db_path = manager.get_database_path()

        assert str(db_path).startswith(str(Path.home()))
        assert "mydata/app.db" in str(db_path)

    def test_get_database_path_with_cli_override(self, tmp_path: Path) -> None:
        """CLI override works for database path."""
        config_path = tmp_path / "config.yaml"
        manager = ConfigManager(config_path)

        db_path = manager.get_database_path(cli_override="/custom/override.db")

        assert str(db_path).endswith("override.db")

    def test_get_output_format_validates(self, tmp_path: Path) -> None:
        """AC9: Invalid format raises ConfigError."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("output:\n  format: invalid\n")

        manager = ConfigManager(config_path)
        with pytest.raises(ConfigError) as exc_info:
            manager.get_output_format()

        assert "Invalid output format" in str(exc_info.value)
        assert "pretty, json, csv" in str(exc_info.value)

    def test_get_confidence_threshold_validates_range(self, tmp_path: Path) -> None:
        """AC9: Out of range threshold raises ConfigError."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categorization:\n  confidence_threshold: 1.5\n")

        manager = ConfigManager(config_path)
        with pytest.raises(ConfigError) as exc_info:
            manager.get_confidence_threshold()

        assert "out of range" in str(exc_info.value)
        assert "0.0 to 1.0" in str(exc_info.value)

    def test_is_auto_categorize_enabled(self, tmp_path: Path) -> None:
        """AC6: Auto-categorization config is read correctly."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categorization:\n  auto_categorize: false\n")

        manager = ConfigManager(config_path)
        assert manager.is_auto_categorize_enabled() is False

    def test_is_color_enabled(self, tmp_path: Path) -> None:
        """Color output config is read correctly."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("output:\n  color: false\n")

        manager = ConfigManager(config_path)
        assert manager.is_color_enabled() is False


class TestSingleton:
    """Tests for singleton pattern."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        ConfigManager.reset_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        ConfigManager.reset_instance()

    def test_get_instance_returns_same_object(self, tmp_path: Path) -> None:
        """Singleton returns same instance."""
        config_path = tmp_path / "config.yaml"

        instance1 = ConfigManager.get_instance(config_path)
        instance2 = ConfigManager.get_instance()

        assert instance1 is instance2

    def test_reset_instance_creates_new(self, tmp_path: Path) -> None:
        """Reset allows new instance creation."""
        config_path1 = tmp_path / "config1.yaml"
        config_path2 = tmp_path / "config2.yaml"

        instance1 = ConfigManager.get_instance(config_path1)
        ConfigManager.reset_instance()
        instance2 = ConfigManager.get_instance(config_path2)

        assert instance1 is not instance2

    def test_get_config_function(self, tmp_path: Path) -> None:
        """get_config() convenience function works."""
        config_path = tmp_path / "config.yaml"
        config = get_config(config_path)

        assert isinstance(config, ConfigManager)


class TestDefaultConfigTemplate:
    """Tests for default config template."""

    def test_template_is_valid_yaml(self) -> None:
        """AC10: Config file is plain YAML."""
        parsed = yaml.safe_load(DEFAULT_CONFIG_TEMPLATE)

        assert "database" in parsed
        assert "output" in parsed
        assert "categorization" in parsed
        assert "banks" in parsed

    def test_template_has_all_default_keys(self) -> None:
        """Template has same structure as defaults."""
        parsed = yaml.safe_load(DEFAULT_CONFIG_TEMPLATE)

        # Check all default keys exist in template
        assert parsed["database"]["path"] is not None
        assert parsed["output"]["format"] is not None
        assert parsed["output"]["color"] is not None
        assert parsed["categorization"]["auto_categorize"] is not None
        assert parsed["categorization"]["confidence_threshold"] is not None
