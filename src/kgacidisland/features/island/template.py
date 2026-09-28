class IslandTemplate:
    def __init__(self, plugin):
        self.plugin = plugin

    def generate(self, island) -> None:
        world = self.plugin.server.get_world(
            self.plugin.config_manager.config["island"]["world"]
        )

        if world is None:
            raise RuntimeError("Configured island world was not found.")

        template = self.plugin.config_manager.template
        island_y = island.origin_y

        platform = template.get("platform", {})
        radius = int(platform.get("radius", 5))

        layers = template.get("layers", [])

        for layer in layers:
            layer_y = island_y + int(layer["y"])
            blocks = layer.get("blocks", {})

            block_type = next(
                iter(blocks.values()),
                "minecraft:air",
            )

            for x in range(-radius, radius + 1):
                for z in range(-radius, radius + 1):
                    world.get_block_at(
                        island.origin_x + x,
                        layer_y,
                        island.origin_z + z,
                    ).set_type(block_type)

        self._generate_tree(world, island, template)

    def _generate_tree(self, world, island, template) -> None:
        tree = template.get("tree", {})

        if not tree.get("enabled", True):
            return

        trunk = tree.get(
            "trunk",
            "minecraft:oak_log",
        )

        leaves = tree.get(
            "leaves",
            "minecraft:oak_leaves",
        )

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