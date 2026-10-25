import csv
from enum import Enum

from person import Gender


class Room:
    def __init__(self, id, name, capacity):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.beds: list[BedStyle] = []
        
class BedStyle(Enum):
    TOP = 1
    BOTTOM = 2

def read_rooms_csv(file_path: str) -> list[Room]:
    """Read rooms and expand top/bottom bunk counts into individual beds."""
    rooms = []
    seen_ids = set()
    with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        required = {
            "id", "name", "capacity", "total_top_bunkers", "total_bottom_bunkers"
        }
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(
                "Room CSV requires id, name, capacity, total_top_bunkers, "
                "total_bottom_bunkers columns."
            )
        for line, row in enumerate(reader, start=2):
            try:
                room = Room(int(row["id"]), row["name"].strip(), int(row["capacity"]))
                top_bunks = int(row["total_top_bunkers"])
                bottom_bunks = int(row["total_bottom_bunkers"])
                if top_bunks < 0 or bottom_bunks < 0:
                    raise ValueError("Bunk counts must be nonnegative integers.")
                # Keep the bed list used by the room assignment model.
                room.beds = (
                    [BedStyle.TOP] * top_bunks
                    + [BedStyle.BOTTOM] * bottom_bunks
                )
                if room.id in seen_ids or not room.name:
                    raise ValueError("Room IDs must be unique and names must be nonempty.")
                if room.capacity < 1 or room.capacity != len(room.beds):
                    raise ValueError("Capacity must be positive and match the number of beds.")
            except (ValueError, KeyError, AttributeError, TypeError) as error:
                raise ValueError(f"Invalid room CSV row {line}: {error}") from error
            seen_ids.add(room.id)
            rooms.append(room)
    if not rooms:
        raise ValueError("Room CSV must contain at least one room.")
    return rooms
