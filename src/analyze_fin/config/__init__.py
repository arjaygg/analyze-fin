"""Configuration management and settings.

Usage:
    from analyze_fin.config import get_config, ConfigManager

    # Get singleton instance
    config = get_config()

    # Access values with override precedence
    db_path = config.get("database.path")
    format = config.get("output.format", cli_override="json")

    # Use convenience methods
    db_path = config.get_database_path()
    is_auto = config.is_auto_categorize_enabled()
"""

from analyze_fin.config.defaults import (
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_DIR,
    DEFAULT_CONFIG_PATH,
)
from analyze_fin.config.settings import ConfigManager, get_config

__all__ = [
    "ConfigManager",
    "DEFAULT_CONFIG",
    "DEFAULT_CONFIG_DIR",
    "DEFAULT_CONFIG_PATH",
    "get_config",
]
