class IslandTemplate:
    def __init__(self, plugin) -> None:
        self.plugin = plugin

    def generate(self, island) -> None:
        world_name = self.plugin.config_manager.get(
            "island.world",
            "",
        )

        if not world_name:
            raise RuntimeError(
                "Island world is not configured."
            )

        world = self.plugin.server.get_world(
            world_name
        )

        if world is None:
            raise RuntimeError(
                f"Configured island world "
                f"'{world_name}' was not found."
            )

        template = (
            self.plugin.config_manager.template
        )

        if not isinstance(
            template,
            dict,
        ):
            raise RuntimeError(
                "Invalid starter.yml configuration."
            )

        island_y = island.origin_y

        platform = template.get(
            "platform",
            {},
        )

        if not isinstance(
            platform,
            dict,
        ):
            platform = {}

        radius = max(
            0,
            int(
                platform.get(
                    "radius",
                    5,
                )
            ),
        )

        layers = template.get(
            "layers",
            [],
        )

        if not isinstance(
            layers,
            list,
        ):
            raise RuntimeError(
                "starter.yml 'layers' must be a list."
            )

        for layer in layers:
            if not isinstance(
                layer,
                dict,
            ):
                continue

            try:
                layer_y = (
                    island_y
                    + int(layer.get("y", 0))
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            blocks = layer.get(
                "blocks",
                {},
            )

            if not isinstance(
                blocks,
                dict,
            ):
                continue

            block_type = next(
                (
                    value
                    for value in blocks.values()
                    if isinstance(value, str)
                    and value
                ),
                "minecraft:air",
            )

            for x in range(
                -radius,
                radius + 1,
            ):
                for z in range(
                    -radius,
                    radius + 1,
                ):
                    world.get_block_at(
                        island.origin_x + x,
                        layer_y,
                        island.origin_z + z,
                    ).set_type(
                        block_type
                    )

        self._generate_tree(
            world,
            island,
            template,
        )

    def _generate_tree(
        self,
        world,
        island,
        template,
    ) -> None:
        tree = template.get(
            "tree",
            {},
        )

        if not isinstance(
            tree,
            dict,
        ):
            return

        if not tree.get(
            "enabled",
            True,
        ):
            return

        trunk = tree.get(
            "trunk",
            "minecraft:oak_log",
        )

        leaves = tree.get(
            "leaves",
            "minecraft:oak_leaves",
        )

        if not isinstance(
            trunk,
            str,
        ) or not trunk:
            return

        if not isinstance(
            leaves,
            str,
        ) or not leaves:
            return

        x = island.origin_x + 2
        z = island.origin_z + 2
        y = island.origin_y + 1

        for offset in range(4):
            world.get_block_at(
                x,
                y + offset,
                z,
            ).set_type(trunk)

        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in range(2, 4):
                    if abs(dx) + abs(dz) <= 3:
                        world.get_block_at(
                            x + dx,
                            y + dy,
                            z + dz,
                        ).set_type(leaves)