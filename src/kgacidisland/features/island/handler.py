from endstone import Player
from endstone.command import Command, CommandExecutor, CommandSender
from .model import Island


class IslandHandler(CommandExecutor):
    def __init__(self, plugin) -> None:
        super().__init__()
        self.plugin = plugin

    def on_command(
        self,
        sender: CommandSender,
        command: Command,
        args: list[str],
    ) -> bool:
        if not isinstance(
            sender,
            Player,
        ):
            sender.send_message(
                self.plugin.messages.get(
                    "callback.player_only",
                    "§cThis command can only be used by a player.",
                )
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

    def _create(
        self,
        player: Player,
    ) -> None:
        owner_uuid = str(
            player.unique_id
        )

        if self.plugin.island_manager.get_island(
            owner_uuid
        ) is not None:
            player.send_message(
                self.plugin.messages.prefixed(
                    "island.already_exists"
                )
            )
            return

        island: Island | None = None

        try:
            island = (
                self.plugin.island_manager.create_island(
                    owner_uuid
                )
            )

            self.plugin.island_template.generate(
                island
            )
            
            self.plugin.island_manager.save()
            
            self._teleport_home(
                player,
                island,
            )

            player.send_message(
                self.plugin.messages.prefixed(
                    "island.created"
                )
            )

        except Exception:
            if island is not None:
                self.plugin.island_manager.remove_island(
                    owner_uuid
                )

            self.plugin.logger.error(
                f"Failed to create island "
                f"for {player.name}: "
                f"{type(error).__name__}: {error}"
            )

            player.send_message(
                self.plugin.messages.prefixed(
                    "island.generation_failed"
                )
            )

    def _home(
        self,
        player: Player,
    ) -> None:
        island = (
            self.plugin.island_manager.get_island(
                str(player.unique_id)
            )
        )

        if island is None:
            player.send_message(
                self.plugin.messages.prefixed(
                    "island.no_island"
                )
            )
            return

        self._teleport_home(
            player,
            island,
        )

    def _teleport_home(
        self,
        player: Player,
        island: Island,
    ) -> None:
        spawn = self.plugin.config_manager.get(
            "island.spawn",
            {},
        )

        if not isinstance(
            spawn,
            dict,
        ):
            spawn = {}

        x = island.origin_x + int(
            spawn.get("x", 0)
        )

        y = island.origin_y + int(
            spawn.get("y", 4)
        )

        z = island.origin_z + int(
            spawn.get("z", 0)
        )

        location = player.location

        location.x = x + 0.5
        location.y = y
        location.z = z + 0.5

        player.teleport(
            location
        )

        player.send_message(
            self.plugin.messages.prefixed(
                "island.teleported"
            )
        )

    def _send_help(
        self,
        player: Player,
    ) -> None:
        player.send_message(
            "§b§lKGAcidIsland\n"
            "§7/island create §f- Create your island\n"
            "§7/island home §f- Teleport to your island"
        )