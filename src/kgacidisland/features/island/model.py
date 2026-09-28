from dataclasses import dataclass


@dataclass(slots=True)
class Island:
    owner_uuid: str
    grid_x: int
    grid_z: int
    origin_x: int
    origin_y: int
    origin_z: int