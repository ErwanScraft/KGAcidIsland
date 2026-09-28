from endstone.command import Command, CommandSender
from endstone.plugin import Plugin

from .features.island.handler import IslandHandler
from .features.island.manager import IslandManager
from .features.island.template import IslandTemplate
from .features.toxic_water.handler import ToxicWaterHandler
from .utils.config import ConfigManager
from .utils.messages import MessageManager


class KGAcidIsland(Plugin):
    api_version = "0.11"

    prefix = "KGAcidIsland"

    commands = {
        "island": {
            "description": "Manage your Acid Island.",
            "usages": [
                "/island",
                "/island create",
                "/island home",
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
    }

    def on_enable(self) -> None:
        self.config_manager = ConfigManager(self)
        self.config_manager.load()

        self.messages = MessageManager(
            self.config_manager
        )

        self.island_manager = IslandManager(self)
        self.island_manager.load()

        self.island_template = IslandTemplate(self)

        self.island_handler = IslandHandler(self)
        self.toxic_water_handler = ToxicWaterHandler(self)

        self.register_events(self)

        self.toxic_water_handler.start()

        self.logger.info(
            "KGAcidIsland v0.1.0 enabled."
        )
        self.logger.info(
            "Loaded %d island(s).",
            len(self.island_manager._islands),
        )

    def on_command(
        self,
        sender: CommandSender,
        command: Command,
        args: list[str],
    ) -> bool:
        if command.name == "island":
            return self.island_handler.handle(
                sender,
                command,
                args,
            )

        return False