from endstone.command import Command, CommandSender
from endstone.plugin import Plugin

from .features.island.handler import IslandHandler
from .features.island.manager import IslandManager
from .features.island.template import IslandTemplate
from .features.toxic_water.handler import ToxicWaterHandler
from .utils.config import ConfigManager
from .utils.messages import MessageManager


class KGAcidIsland(Plugin):
    name = "KGAcidIsland"
    version = "0.1.0"
    authors = ["ErwanScraft"]
    description = "Acid Island gameplay for KG Survival."
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
        self._load_resources()
        self._load_configuration()
        self._load_messages()
        self._initialize_handlers()
    
        self._register_commands()
        self.toxic_water_handler.start()
    
        self.logger.info(
            f"{self.name} v{self.version} enabled."
        )
        self.logger.info(
            "Loaded %d island(s).",
            self.island_manager.count,
        )
    
    
    def _load_resources(self) -> None:
        self.save_resources("config.yml")
        self.save_resources("message.yml")
        self.save_resources("starter.yml")
    
    
    def _load_configuration(self) -> None:
        self.config_manager = ConfigManager(self)
        self.config_manager.load()
    
        self.island_manager = IslandManager(self)
        self.island_manager.load()
    
    
    def _load_messages(self) -> None:
        self.messages = KGAcidIslandMessages(self)
    
    
    def _initialize_handlers(self) -> None:
        self.island_template = IslandTemplate(self)
    
        self.island_handler = IslandHandler(self)
        self.toxic_water_handler = ToxicWaterHandler(self)
    
    
    def _register_commands(self) -> None:
        command = self.get_command("island")
    
        if command is not None:
            command.executor = self.island_handler