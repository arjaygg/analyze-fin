"""
Configuration management for analyze-fin.

Provides ConfigManager class for loading, accessing, and validating configuration.

Override Precedence:
    CLI flags > environment variables > config file > defaults

Environment Variables:
    Use ANALYZE_FIN_ prefix with uppercase, underscores for nested keys.
    Example: ANALYZE_FIN_DATABASE_PATH, ANALYZE_FIN_OUTPUT_FORMAT
"""

from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from analyze_fin.config.defaults import (
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_PATH,
    DEFAULT_CONFIG_TEMPLATE,
)
from analyze_fin.exceptions import ConfigError


class ConfigManager:
    """Manage application configuration with layered override support.

    Configuration is loaded lazily on first access. Supports:
    - Auto-creation of default config file
    - Path expansion (~ and environment variables)
    - Nested key access via dot notation
    - Override precedence: CLI > env > config > defaults

    Example:
        >>> config = ConfigManager()
        >>> db_path = config.get("database.path")
        >>> format = config.get("output.format", cli_override="json")
    """

    _instance: ConfigManager | None = None

    def __init__(self, config_path: Path | str | None = None) -> None:
        """Initialize ConfigManager.

        Args:
            config_path: Custom config file path. Defaults to ~/.analyze-fin/config.yaml
        """
        if config_path is not None:
            self.config_path = Path(config_path)
        else:
            self.config_path = DEFAULT_CONFIG_PATH

        self._config: dict[str, Any] = {}
        self._loaded = False

    @classmethod
    def get_instance(cls, config_path: Path | str | None = None) -> ConfigManager:
        """Get singleton ConfigManager instance.

        Args:
            config_path: Custom config file path (only used on first call).

        Returns:
            Shared ConfigManager instance.
        """
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (useful for testing)."""
        cls._instance = None

    def load(self) -> dict[str, Any]:
        """Load configuration from file, creating default if needed.

        Returns:
            Loaded configuration dict.

        Raises:
            ConfigError: If config file has invalid YAML syntax.
        """
        if self._loaded:
            return self._config

        # Start with defaults
        self._config = deepcopy(DEFAULT_CONFIG)

        # Create default config if it doesn't exist
        if not self.config_path.exists():
            self.create_default()

        # Load and merge user config
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self._merge_config(self._config, user_config)
            except yaml.YAMLError as e:
                raise ConfigError(
                    f"Invalid YAML in config file: {e}",
                    setting=str(self.config_path),
                ) from e

        self._loaded = True
        return self._config

    def create_default(self) -> Path:
        """Create default config file with documented settings.

        Returns:
            Path to created config file.
        """
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write default config with comments
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CONFIG_TEMPLATE)

        return self.config_path

    def get(
        self,
        key: str,
        default: Any = None,
        *,
        cli_override: Any = None,
    ) -> Any:
        """Get configuration value with override precedence.

        Args:
            key: Dot-notation key (e.g., "database.path", "output.format").
            default: Default value if key not found.
            cli_override: CLI flag value (highest precedence).

        Returns:
            Configuration value with precedence: CLI > env > config > default.
        """
        # 1. CLI override has highest precedence
        if cli_override is not None:
            return self._process_value(cli_override, key)

        # 2. Check environment variable
        env_value = self._get_env_value(key)
        if env_value is not None:
            return self._process_value(env_value, key)

        # 3. Get from config file (loads if needed)
        config = self.load()
        value = self._get_nested(config, key)
        if value is not None:
            return self._process_value(value, key)

        # 4. Fall back to provided default
        return default

    def get_database_path(self, cli_override: str | None = None) -> Path:
        """Get database path with path expansion.

        Args:
            cli_override: CLI-provided path override.

        Returns:
            Expanded Path to database file.
        """
        path_str = self.get("database.path", cli_override=cli_override)
        return self._expand_path(path_str)

    def get_output_format(self, cli_override: str | None = None) -> str:
        """Get output format.

        Args:
            cli_override: CLI-provided format override.

        Returns:
            Output format string (pretty, json, csv).
        """
        format_val = self.get("output.format", default="pretty", cli_override=cli_override)
        valid_formats = ("pretty", "json", "csv")
        if format_val not in valid_formats:
            raise ConfigError(
                f"Invalid output format '{format_val}'. Valid: {', '.join(valid_formats)}",
                setting="output.format",
            )
        return format_val

    def get_report_format(self, cli_override: str | None = None) -> str:
        """Get report format.

        Args:
            cli_override: CLI-provided format override.

        Returns:
            Report format string (html, markdown).
        """
        format_val = self.get("output.report_format", default="html", cli_override=cli_override)
        valid_formats = ("html", "markdown")
        if format_val not in valid_formats:
            raise ConfigError(
                f"Invalid report format '{format_val}'. Valid: {', '.join(valid_formats)}",
                setting="output.report_format",
            )
        return format_val

    def is_auto_categorize_enabled(self, cli_override: bool | None = None) -> bool:
        """Check if auto-categorization is enabled.

        Args:
            cli_override: CLI-provided override.

        Returns:
            True if auto-categorization is enabled.
        """
        return bool(self.get("categorization.auto_categorize", default=True, cli_override=cli_override))

    def get_confidence_threshold(self, cli_override: float | None = None) -> float:
        """Get categorization confidence threshold.

        Args:
            cli_override: CLI-provided threshold override.

        Returns:
            Confidence threshold (0.0 to 1.0).

        Raises:
            ConfigError: If threshold is not between 0.0 and 1.0.
        """
        threshold = self.get("categorization.confidence_threshold", default=0.8, cli_override=cli_override)
        try:
            threshold = float(threshold)
        except (TypeError, ValueError) as e:
            raise ConfigError(
                f"Invalid confidence threshold '{threshold}'. Must be a number.",
                setting="categorization.confidence_threshold",
            ) from e

        if not 0.0 <= threshold <= 1.0:
            raise ConfigError(
                f"Confidence threshold {threshold} out of range. Must be 0.0 to 1.0.",
                setting="categorization.confidence_threshold",
            )
        return threshold

    def is_color_enabled(self, cli_override: bool | None = None) -> bool:
        """Check if color output is enabled.

        Args:
            cli_override: CLI-provided override.

        Returns:
            True if color output is enabled.
        """
        return bool(self.get("output.color", default=True, cli_override=cli_override))

    def _get_env_value(self, key: str) -> str | None:
        """Get value from environment variable.

        Args:
            key: Dot-notation config key.

        Returns:
            Environment variable value or None if not set.
        """
        # Convert "database.path" to "ANALYZE_FIN_DATABASE_PATH"
        env_key = f"ANALYZE_FIN_{key.upper().replace('.', '_')}"
        return os.environ.get(env_key)

    def _get_nested(self, config: dict[str, Any], key: str) -> Any:
        """Get nested value using dot notation.

        Args:
            config: Configuration dict.
            key: Dot-notation key (e.g., "database.path").

        Returns:
            Nested value or None if not found.
        """
        parts = key.split(".")
        value = config
        for part in parts:
            if not isinstance(value, dict):
                return None
            value = value.get(part)
            if value is None:
                return None
        return value

    def _merge_config(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        """Recursively merge override config into base config.

        Args:
            base: Base configuration dict (modified in place).
            override: Override values to merge.
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _expand_path(self, path: str | Path) -> Path:
        """Expand path with ~ and environment variables.

        Args:
            path: Path string or Path object.

        Returns:
            Expanded absolute Path.
        """
        path_str = str(path)
        # Expand ~ to home directory
        path_str = os.path.expanduser(path_str)
        # Expand environment variables
        path_str = os.path.expandvars(path_str)
        return Path(path_str).resolve()

    def _process_value(self, value: Any, key: str) -> Any:
        """Process value based on expected type from defaults.

        Args:
            value: Raw value (may be string from env var).
            key: Config key for type lookup.

        Returns:
            Processed value with correct type.
        """
        # Get expected type from defaults
        default_value = self._get_nested(DEFAULT_CONFIG, key)

        if default_value is None:
            return value

        # Convert string to expected type
        if isinstance(value, str):
            if isinstance(default_value, bool):
                return value.lower() in ("true", "1", "yes", "on")
            elif isinstance(default_value, int):
                try:
                    return int(value)
                except ValueError:
                    return value
            elif isinstance(default_value, float):
                try:
                    return float(value)
                except ValueError:
                    return value

        return value


def get_config(config_path: Path | str | None = None) -> ConfigManager:
    """Get ConfigManager instance (convenience function).

    Args:
        config_path: Custom config file path (only used on first call).

    Returns:
        ConfigManager singleton instance.
    """
    return ConfigManager.get_instance(config_path)
