from endstone import Player


class ToxicWaterHandler:
    def __init__(self, plugin):
        self.plugin = plugin

    def start(self) -> None:
        acid = self.plugin.config_manager.config.get(
            "acid",
            {},
        )

        if not acid.get("enabled", True):
            return

        damage = acid.get("damage", {})

        if not damage.get("enabled", True):
            return

        interval = max(
            1,
            int(damage.get("interval", 20)),
        )

        self.plugin.server.scheduler.run_task(
            self.plugin,
            self._tick,
            delay=interval,
            period=interval,
        )

    def _tick(self) -> None:
        acid = self.plugin.config_manager.config.get(
            "acid",
            {},
        )

        water_level = int(
            acid.get("water_level", 50)
        )

        for player in self.plugin.server.online_players:
            if not isinstance(player, Player):
                continue

            location = player.location

            if location.y > water_level:
                continue

            block = player.dimension.get_block_at(
                int(location.x),
                int(location.y),
                int(location.z),
            )

            if block.type.identifier != "minecraft:water":
                continue

            self._damage(player)

    def _damage(self, player: Player) -> None:
        amount = float(
            self.plugin.config_manager.config[
                "acid"
            ]["damage"]["amount"]
        )

        self.plugin.server.dispatch_command(
            self.plugin.server.command_sender,
            f"damage {player.name} {amount} poison",
        )