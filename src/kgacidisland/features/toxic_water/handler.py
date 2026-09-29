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
        water_level = (
            self.plugin.config_manager.get_int(
                "acid.water_level",
                50,
            )
        )

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

            block = player.dimension.get_block_at(
                int(location.x),
                int(location.y),
                int(location.z),
            )
            
            if block.type != "minecraft:water":
                block = player.dimension.get_block_at(
                    int(location.x),
                    int(location.y + 1),
                    int(location.z),
                )
            
            if block.type != "minecraft:water":
                continue
            
            self._damage(player)

    def _damage(
        self,
        player: Player,
    ) -> None:
        amount = self.plugin.config_manager.get_float(
            "acid.damage.amount",
            1.0,
        )
    
        if amount <= 0:
            return
    
        player.health = max(
            0.0,
            player.health - amount,
        )