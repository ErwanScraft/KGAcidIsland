import json
from pathlib import Path

from .model import Island


class IslandManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config = plugin.config_manager

        self._islands: dict[str, Island] = {}

        self._data_path = (
            Path(plugin.data_folder) / "islands.json"
        )

    def load(self) -> None:
        if not self._data_path.exists():
            return

        with self._data_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        for owner_uuid, island_data in data.items():
            self._islands[owner_uuid] = Island(
                owner_uuid=owner_uuid,
                grid_x=island_data["grid_x"],
                grid_z=island_data["grid_z"],
                origin_x=island_data["origin_x"],
                origin_y=island_data["origin_y"],
                origin_z=island_data["origin_z"],
            )

    def save(self) -> None:
        data = {
            owner_uuid: {
                "grid_x": island.grid_x,
                "grid_z": island.grid_z,
                "origin_x": island.origin_x,
                "origin_y": island.origin_y,
                "origin_z": island.origin_z,
            }
            for owner_uuid, island in self._islands.items()
        }

        with self._data_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def get_island(self, owner_uuid: str) -> Island | None:
        return self._islands.get(owner_uuid)

    def create_island(self, owner_uuid: str) -> Island:
        existing = self.get_island(owner_uuid)

        if existing is not None:
            raise ValueError("Player already owns an island.")

        grid_x, grid_z = self._find_free_slot()

        island_size = int(
            self.config.config["island"]["size"]
        )

        spacing = int(
            self.config.config["island"]["spacing"]
        )

        origin = self.config.config["island"]["origin"]

        grid_size = island_size + spacing

        origin_x = int(origin["x"]) + (grid_x * grid_size)
        origin_z = int(origin["z"]) + (grid_z * grid_size)
        origin_y = int(
            self.config.config["island"]["y"]
        )

        island = Island(
            owner_uuid=owner_uuid,
            grid_x=grid_x,
            grid_z=grid_z,
            origin_x=origin_x,
            origin_y=origin_y,
            origin_z=origin_z,
        )

        self._islands[owner_uuid] = island
        self.save()

        return island

    def _find_free_slot(self) -> tuple[int, int]:
        occupied = {
            (island.grid_x, island.grid_z)
            for island in self._islands.values()
        }

        if (0, 0) not in occupied:
            return 0, 0

        radius = 1

        while True:
            for grid_x in range(-radius, radius + 1):
                for grid_z in range(-radius, radius + 1):
                    if (
                        abs(grid_x) != radius
                        and abs(grid_z) != radius
                    ):
                        continue

                    if (grid_x, grid_z) not in occupied:
                        return grid_x, grid_z

            radius += 1