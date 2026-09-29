from endstone.plugin import Plugin

from .features.island.handler import IslandHandler
from .features.island.manager import IslandManager
from .features.island.template import IslandTemplate
from .features.toxic_water.handler import ToxicWaterHandler
from .utils.config import ConfigManager
from .utils.messages import KGAcidIslandMessages


class KGAcidIsland(Plugin):
    api_version = "0.11"

    name = "KGAcidIsland"
    version = "0.1.5"
    authors = ["ErwanScraft"]
    description = "Acid Island gameplay for KG Survival."
    prefix = "KGAcidIsland"

    commands = {
        "island": {
            "description": "Manage your Acid Island.",
            "usages": [
                "/island",
                "/island <action: str> [subcommand: str]",
            ],
            "permissions": [
                "kgacidisland.command.island",
            ],
        },
    }

    permissions = {
        "kgacidisland.command.island": {
            "description": "Allows the player to use /island.",
            "default": True,
        },
        "kgacidisland.command.template": {
            "description": "Allows the player to manage island templates.",
            "default": "op",
        },
    }

    def on_enable(self) -> None:
        self.config_manager = ConfigManager(self)
        self.messages = KGAcidIslandMessages(self)

        self.island_manager = IslandManager(self)
        self.island_manager.load()

        self.island_template = IslandTemplate(self)
        self.island_handler = IslandHandler(self)
        self.toxic_water_handler = ToxicWaterHandler(self)

        command = self.get_command("island")

        if command is not None:
            command.executor = self.island_handler

        self.toxic_water_handler.start()

        self.logger.info(
            f"{self.name} v{self.version} enabled."
        )
        self.logger.info(
            f"Loaded {self.island_manager.count} island(s)."
        )

    def on_disable(self) -> None:
        if not hasattr(self, "island_manager"):
            return

        try:
            self.island_manager.save()
        except RuntimeError as error:
            self.logger.error(str(error))