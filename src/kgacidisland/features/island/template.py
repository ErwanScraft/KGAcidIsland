from endstone import Player

from .model import Island


class IslandTemplate:
    def __init__(self, plugin) -> None:
        super().__init__()
        self.plugin = plugin
        self._selections = {}

    def set_pos1(
        self,
        player: Player,
    ) -> None:
        self._selections.setdefault(
            str(player.unique_id),
            {},
        )["pos1"] = (
            int(player.location.x),
            int(player.location.y),
            int(player.location.z),
        )

    def set_pos2(
        self,
        player: Player,
    ) -> None:
        self._selections.setdefault(
            str(player.unique_id),
            {},
        )["pos2"] = (
            int(player.location.x),
            int(player.location.y),
            int(player.location.z),
        )

    def clear_selection(
        self,
        player: Player,
    ) -> None:
        self._selections.pop(
            str(player.unique_id),
            None,
        )

    def capture(
        self,
        player: Player,
    ) -> int:
        selection = self._selections.get(
            str(player.unique_id)
        )

        if not selection:
            raise RuntimeError(
                "Template positions are not set."
            )

        pos1 = selection.get("pos1")
        pos2 = selection.get("pos2")

        if pos1 is None or pos2 is None:
            raise RuntimeError(
                "Both template positions are required."
            )

        min_x = min(
            pos1[0],
            pos2[0],
        )
        max_x = max(
            pos1[0],
            pos2[0],
        )
        min_y = min(
            pos1[1],
            pos2[1],
        )
        max_y = max(
            pos1[1],
            pos2[1],
        )
        min_z = min(
            pos1[2],
            pos2[2],
        )
        max_z = max(
            pos1[2],
            pos2[2],
        )

        size_x = max_x - min_x + 1
        size_y = max_y - min_y + 1
        size_z = max_z - min_z + 1

        total_blocks = (
            size_x
            * size_y
            * size_z
        )

        max_blocks = self.plugin.config_manager.get_int(
            "island.template.max_blocks",
            32768,
        )

        if total_blocks > max_blocks:
            raise RuntimeError(
                f"Template is too large. "
                f"Maximum is {max_blocks:,} blocks."
            )

        world = player.dimension

        center_x = (
            min_x + max_x
        ) // 2

        center_z = (
            min_z + max_z
        ) // 2

        palette: list[str] = []
        palette_index: dict[str, int] = {}
        blocks: list[list[int]] = []

        for y in range(
            min_y,
            max_y + 1,
        ):
            for x in range(
                min_x,
                max_x + 1,
            ):
                for z in range(
                    min_z,
                    max_z + 1,
                ):
                    block = world.get_block_at(
                        x,
                        y,
                        z,
                    )

                    block_type = block.type

                    if not isinstance(
                        block_type,
                        str,
                    ) or not block_type:
                        continue

                    if block_type == "minecraft:air":
                        continue

                    if block_type not in palette_index:
                        palette_index[
                            block_type
                        ] = len(palette)

                        palette.append(
                            block_type
                        )

                    blocks.append(
                        [
                            x - center_x,
                            y - min_y,
                            z - center_z,
                            palette_index[
                                block_type
                            ],
                        ]
                    )

        template = {
            "version": 1,
            "size": {
                "x": size_x,
                "y": size_y,
                "z": size_z,
            },
            "palette": palette,
            "blocks": blocks,
        }

        self.plugin.config_manager.save_template(
            template
        )

        self._selections.pop(
            str(player.unique_id),
            None,
        )

        return len(blocks)

    def generate(
        self,
        island: Island,
    ) -> None:
        world_name = self.plugin.config_manager.get(
            "island.world",
            "",
        )

        if not isinstance(
            world_name,
            str,
        ) or not world_name:
            raise RuntimeError(
                "Island world is not configured."
            )

        level = self.plugin.server.level

        if level.name != world_name:
            raise RuntimeError(
                f"Configured island world "
                f"'{world_name}' was not found."
            )

        world = level.get_dimension(
            "overworld"
        )

        if world is None:
            raise RuntimeError(
                f"Overworld dimension for "
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

        if "blocks" in template:
            self._generate_snapshot(
                world,
                island,
                template,
            )
            return

        self._generate_legacy(
            world,
            island,
            template,
        )

    def _generate_snapshot(
        self,
        world,
        island: Island,
        template: dict,
    ) -> None:
        palette = template.get(
            "palette",
            [],
        )

        blocks = template.get(
            "blocks",
            [],
        )

        if not isinstance(
            palette,
            list,
        ):
            raise RuntimeError(
                "starter.yml 'palette' must be a list."
            )

        if any(
            not isinstance(
                block_type,
                str,
            ) or not block_type
            for block_type in palette
        ):
            raise RuntimeError(
                "starter.yml 'palette' contains "
                "an invalid block."
            )

        if not isinstance(
            blocks,
            list,
        ):
            raise RuntimeError(
                "starter.yml 'blocks' must be a list."
            )

        for entry in blocks:
            if not isinstance(
                entry,
                list,
            ) or len(entry) != 4:
                continue

            try:
                offset_x = int(entry[0])
                offset_y = int(entry[1])
                offset_z = int(entry[2])
                palette_id = int(entry[3])
            except (
                TypeError,
                ValueError,
            ):
                continue

            if not 0 <= palette_id < len(
                palette
            ):
                continue

            block_type = palette[
                palette_id
            ]

            world.get_block_at(
                island.origin_x + offset_x,
                island.origin_y + offset_y,
                island.origin_z + offset_z,
            ).set_type(
                block_type
            )

    def _generate_legacy(
        self,
        world,
        island: Island,
        template: dict,
    ) -> None:
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

        try:
            radius = max(
                0,
                int(
                    platform.get(
                        "radius",
                        5,
                    )
                ),
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise RuntimeError(
                "starter.yml 'platform.radius' "
                "must be an integer."
            ) from error

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
                    + int(
                        layer.get(
                            "y",
                            0,
                        )
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            block_type = layer.get(
                "block",
                "minecraft:air",
            )

            if not isinstance(
                block_type,
                str,
            ) or not block_type:
                continue

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
        island: Island,
        template: dict,
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
            ).set_type(
                trunk
            )

        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in range(2, 4):
                    if abs(dx) + abs(dz) <= 3:
                        world.get_block_at(
                            x + dx,
                            y + dy,
                            z + dz,
                        ).set_type(
                            leaves
                        )