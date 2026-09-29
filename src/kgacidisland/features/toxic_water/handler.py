from endstone import GameMode, Player


class ToxicWaterHandler:
    def __init__(self, plugin) -> None:
        self.plugin = plugin
        self._task_started = False

    def start(self) -> None:
        if self._task_started:
            return

        if not self.plugin.config_manager.get_bool(
            "acid.enabled",
            True,
        ):
            return

        if not self.plugin.config_manager.get_bool(
            "acid.damage.enabled",
            True,
        ):
            return

        interval = max(
            1,
            self.plugin.config_manager.get_int(
                "acid.damage.interval",
                20,
            ),
        )

        self.plugin.server.scheduler.run_task(
            self.plugin,
            self._tick,
            delay=interval,
            period=interval,
        )

        self._task_started = True

    def _tick(self) -> None:
        config = self.plugin.config_manager

        water_level = config.get_int(
            "acid.water_level",
            50,
        )

        world_only = config.get_bool(
            "acid.world_only",
            True,
        )

        configured_world = config.get(
            "island.world",
            "",
        )

        if (
            world_only
            and isinstance(
                configured_world,
                str,
            )
            and configured_world
            and self.plugin.server.level.name
            != configured_world
        ):
            return

        for player in self.plugin.server.online_players:
            if not isinstance(
                player,
                Player,
            ):
                continue

            if player.game_mode in (
                GameMode.CREATIVE,
                GameMode.SPECTATOR,
            ):
                continue

            location = player.location

            if location.y > water_level:
                continue

            x = int(location.x)
            y = int(location.y)
            z = int(location.z)

            is_in_water = False

            for offset in (0, 1):
                block = player.dimension.get_block_at(
                    x,
                    y + offset,
                    z,
                )

                if block.type == "minecraft:water":
                    is_in_water = True
                    break

            if not is_in_water:
                continue

            self._damage(player)

    def _damage(
        self,
        player: Player,
    ) -> None:
        config = self.plugin.config_manager

        effect = config.get(
            "acid.damage.effect",
            {},
        )

        if not isinstance(
            effect,
            dict,
        ):
            return

        effect_type = effect.get(
            "type",
            "poison",
        )

        if not isinstance(
            effect_type,
            str,
        ) or not effect_type.strip():
            effect_type = "poison"

        duration = max(
            1,
            config.get_int(
                "acid.damage.effect.duration",
                2,
            ),
        )

        amplifier = max(
            0,
            config.get_int(
                "acid.damage.effect.amplifier",
                0,
            ),
        )

        hide_particles = config.get_bool(
            "acid.damage.effect.hide_particles",
            True,
        )

        self.plugin.server.dispatch_command(
            self.plugin.server.console_sender,
            (
                f"effect {player.name} "
                f"{effect_type} "
                f"{duration} "
                f"{amplifier} "
                f"{str(hide_particles).lower()}"
            ),
        )