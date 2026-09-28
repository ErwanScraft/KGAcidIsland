from pathlib import Path

import yaml


class ConfigManager:
    def __init__(self, plugin) -> None:
        self.plugin = plugin

        self.path = Path(
            plugin.data_folder
        ) / "config.yml"

        self.template_path = Path(
            plugin.data_folder
        ) / "starter.yml"

        self.data = {}
        self.template = {}

        self._ensure_config()
        self._ensure_template()

        self._load()
        self._load_template()

    def _ensure_config(self) -> None:
        if self.path.exists():
            return

        try:
            self.plugin.save_resources(
                "config.yml",
            )
        except (
            FileNotFoundError,
            OSError,
        ) as error:
            self.plugin.logger.error(
                f"Failed to create config.yml: {error}"
            )

    def _ensure_template(self) -> None:
        if self.template_path.exists():
            return

        try:
            self.plugin.save_resources(
                "starter.yml",
            )
        except (
            FileNotFoundError,
            OSError,
        ) as error:
            self.plugin.logger.error(
                f"Failed to create starter.yml: {error}"
            )

    def _load(self) -> None:
        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = yaml.safe_load(file) or {}

        except (
            OSError,
            yaml.YAMLError,
        ) as error:
            self.plugin.logger.error(
                f"Failed to load config.yml: {error}"
            )
            self.data = {}
            return

        if not isinstance(data, dict):
            self.plugin.logger.error(
                "config.yml must contain a YAML mapping."
            )
            self.data = {}
            return

        self.data = data

    def _load_template(self) -> None:
        try:
            with self.template_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = yaml.safe_load(file) or {}

        except (
            OSError,
            yaml.YAMLError,
        ) as error:
            self.plugin.logger.error(
                f"Failed to load starter.yml: {error}"
            )
            self.template = {}
            return

        if not isinstance(data, dict):
            self.plugin.logger.error(
                "starter.yml must contain a YAML mapping."
            )
            self.template = {}
            return

        self.template = data

    def get(
        self,
        path: str,
        default=None,
    ):
        value = self.data

        for key in path.split("."):
            if not isinstance(value, dict):
                return default

            if key not in value:
                return default

            value = value[key]

        return value

    def get_int(
        self,
        path: str,
        default: int,
    ) -> int:
        value = self.get(
            path,
            default,
        )

        try:
            return int(value)
        except (
            TypeError,
            ValueError,
        ):
            return default

    def get_float(
        self,
        path: str,
        default: float,
    ) -> float:
        value = self.get(
            path,
            default,
        )

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return default

    def get_bool(
        self,
        path: str,
        default: bool,
    ) -> bool:
        value = self.get(
            path,
            default,
        )

        if isinstance(value, bool):
            return value

        return default