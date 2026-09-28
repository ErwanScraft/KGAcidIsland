from endstone import Player
from endstone.command import Command, CommandSender


class IslandHandler:
    def __init__(self, plugin):
        self.plugin = plugin

    def handle(
        self,
        sender: CommandSender,
        command: Command,
        args: list[str],
    ) -> bool:
        if not isinstance(sender, Player):
            self.plugin.logger.warning(
                "Only players can use /island."
            )
            return True

        if not args:
            self._send_help(sender)
            return True

        action = args[0].lower()

        if action == "create":
            self._create(sender)
            return True

        if action == "home":
            self._home(sender)
            return True

        self._send_help(sender)
        return True

    def _create(self, player: Player) -> None:
        owner_uuid = str(player.unique_id)

        existing = self.plugin.island_manager.get_island(
            owner_uuid
        )

        if existing is not None:
            player.send_message(
                self.plugin.messages.get(
                    "island.already_exists"
                )
            )
            return

        try:
            island = self.plugin.island_manager.create_island(
                owner_uuid
            )

            self.plugin.island_template.generate(island)

            self._teleport_home(player, island)

        except Exception:
            self.plugin.logger.exception(
                "Failed to create island for %s.",
                player.name,
            )

            player.send_message(
                self.plugin.messages.get(
                    "island.generation_failed"
                )
            )

    def _home(self, player: Player) -> None:
        island = self.plugin.island_manager.get_island(
            str(player.unique_id)
        )

        if island is None:
            player.send_message(
                self.plugin.messages.get(
                    "island.no_island"
                )
            )
            return

        self._teleport_home(player, island)

    def _teleport_home(self, player, island) -> None:
        spawn = self.plugin.config_manager.config[
            "island"
        ].get("spawn", {})

        x = island.origin_x + int(spawn.get("x", 0))
        y = island.origin_y + int(spawn.get("y", 3))
        z = island.origin_z + int(spawn.get("z", 0))

        location = player.location
        location.x = x + 0.5
        location.y = y
        location.z = z + 0.5

        player.teleport(location)

        player.send_message(
            self.plugin.messages.get(
                "island.teleported"
            )
        )

    @staticmethod
    def _send_help(player: Player) -> None:
        player.send_message(
            "§b§lKGAcidIsland"
            "\n§7/island create §f- Create your island"
            "\n§7/island home §f- Teleport to your island"
        )