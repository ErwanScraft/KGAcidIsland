from pathlib import Path

import yaml


class ConfigManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_path = Path(plugin.data_folder)

        self.config_path = self.data_path / "config.yml"
        self.messages_path = self.data_path / "messages.yml"
        self.template_path = self.data_path / "starter.yml"

        self.config = {}
        self.messages = {}
        self.template = {}

    def load(self) -> None:
        self.plugin.save_resource("config.yml", overwrite=False)
        self.plugin.save_resource("messages.yml", overwrite=False)
        self.plugin.save_resource("starter.yml", overwrite=False)

        self.config = self._load_file(self.config_path)
        self.messages = self._load_file(self.messages_path)
        self.template = self._load_file(self.template_path)

    @staticmethod
    def _load_file(path: Path) -> dict:
        if not path.exists():
            return {}

        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}