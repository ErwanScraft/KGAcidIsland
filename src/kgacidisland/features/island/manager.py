import json
from pathlib import Path

from .model import Island


class IslandManager:
    def __init__(self, plugin) -> None:
        self.plugin = plugin
        self.config = plugin.config_manager

        self._islands: dict[str, Island] = {}

        self._data_path = (
            Path(plugin.data_folder) / "islands.json"
        )

    @property
    def count(self) -> int:
        return len(self._islands)

    def load(self) -> None:
        if not self._data_path.exists():
            return

        try:
            with self._data_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)
        except (
            OSError,
            json.JSONDecodeError,
        ) as error:
            self.plugin.logger.error(
                f"Failed to load islands.json: {error}"
            )
            return

        if not isinstance(data, dict):
            self.plugin.logger.error(
                "Invalid islands.json format."
            )
            return

        self._islands.clear()

        for owner_uuid, island_data in data.items():
            if not isinstance(island_data, dict):
                continue

            try:
                self._islands[owner_uuid] = Island(
                    owner_uuid=owner_uuid,
                    grid_x=int(island_data["grid_x"]),
                    grid_z=int(island_data["grid_z"]),
                    origin_x=int(island_data["origin_x"]),
                    origin_y=int(island_data["origin_y"]),
                    origin_z=int(island_data["origin_z"]),
                )
            except (
                KeyError,
                TypeError,
                ValueError,
            ) as error:
                self.plugin.logger.warning(
                    f"Skipped invalid island data for "
                    f"{owner_uuid}: {error}"
                )

    def save(self) -> None:
        self._data_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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

        try:
            with self._data_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=2,
                )
        except OSError as error:
            self.plugin.logger.error(
                f"Failed to save islands.json: {error}"
            )

    def get_island(
        self,
        owner_uuid: str,
    ) -> Island | None:
        return self._islands.get(owner_uuid)

    def create_island(
        self,
        owner_uuid: str,
    ) -> Island:
        if self.get_island(owner_uuid) is not None:
            raise ValueError(
                "Player already owns an island."
            )

        grid_x, grid_z = self._find_free_slot()

        island_size = self.config.get_int(
            "island.size",
            128,
        )

        spacing = self.config.get_int(
            "island.spacing",
            8,
        )

        origin_x = self.config.get_int(
            "island.origin.x",
            500,
        )

        origin_z = self.config.get_int(
            "island.origin.z",
            500,
        )

        origin_y = self.config.get_int(
            "island.y",
            100,
        )

        grid_size = island_size + spacing

        island = Island(
            owner_uuid=owner_uuid,
            grid_x=grid_x,
            grid_z=grid_z,
            origin_x=origin_x + (grid_x * grid_size),
            origin_y=origin_y,
            origin_z=origin_z + (grid_z * grid_size),
        )

        self._islands[owner_uuid] = island
        self.save()

        return island

    def remove_island(
        self,
        owner_uuid: str,
    ) -> bool:
        if owner_uuid not in self._islands:
            return False

        del self._islands[owner_uuid]
        self.save()

        return True

    def _find_free_slot(self) -> tuple[int, int]:
        occupied = {
            (
                island.grid_x,
                island.grid_z,
            )
            for island in self._islands.values()
        }

        if (0, 0) not in occupied:
            return 0, 0

        radius = 1

        while True:
            for grid_x in range(
                -radius,
                radius + 1,
            ):
                for grid_z in range(
                    -radius,
                    radius + 1,
                ):
                    if (
                        abs(grid_x) != radius
                        and abs(grid_z) != radius
                    ):
                        continue

                    if (
                        grid_x,
                        grid_z,
                    ) not in occupied:
                        return grid_x, grid_z

            radius += 1