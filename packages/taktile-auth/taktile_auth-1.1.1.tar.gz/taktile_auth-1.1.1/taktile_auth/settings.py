import os
import pathlib
import typing as t

import pkg_resources


def get_resource_path(package: str, resource: str) -> pathlib.Path:
    return pathlib.Path(pkg_resources.resource_filename(package, resource))


class Settings:
    """
    TODO ITER-1717: Move to pydantic-settings
    """

    def __init__(self, defaults: dict[str, t.Any]):
        """
        Initialize the settings with default values and then update them with
        environment variables, if available.
        """
        self._settings = defaults
        self._load_env_vars()

    def _load_env_vars(self) -> None:
        """Update settings from environment variables."""
        for key in self._settings:
            env_value = os.getenv(key)
            if env_value is not None:
                # Convert path strings to pathlib.Path
                if "PATH" in key:
                    self._settings[key] = pathlib.Path(env_value)
                else:
                    self._settings[key] = type(self._settings[key])(env_value)

    def __getattr__(self, item: str) -> t.Any:
        """Get attributes directly from the settings dictionary."""
        try:
            return self._settings[item]
        except KeyError:
            raise AttributeError(f"Setting '{item}' not found")


# Defaults
defaults = {
    "ENV": "local",
    "RESOURCE_PATH": get_resource_path(
        "taktile_auth", "assets/resources.yaml"
    ),
    "ROLE_PATH": get_resource_path("taktile_auth", "assets/roles.yaml"),
    "CACHE_SPEEDUP_TIME_MINUTES": 60,
    "CACHE_FALLBACK_TIME_MINUTES": 72 * 60,
    "CACHE_PUBLIC_KEY_SPEEDUP_TIME_MINUTES": 4 * 60,
    "CACHE_PUBLIC_KEY_FALLBACK_TIME_MINUTES": 10 * 24 * 60,
    "AUTH_SERVER_TIMEOUT_SECONDS": 4,
}

settings = Settings(defaults)
