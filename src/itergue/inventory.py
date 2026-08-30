from collections.abc import Iterator
from dataclasses import dataclass, field

from itergue.combat import Stats
from itergue.items import Equippable, EquipSlot, Item


@dataclass
class Inventory:
    """The player's bag. Holds at most capacity items."""

    capacity: int = 10
    items: list[Item] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[Item]:
        return iter(self.items)

    def __getitem__(self, index: int) -> Item:
        return self.items[index]

    @property
    def is_full(self) -> bool:
        return len(self.items) >= self.capacity

    def add(self, item: Item) -> bool:
        """Add an item to the inventory. Returns True if successful."""
        if self.is_full:
            return False
        self.items.append(item)
        return True

    def take(self, index: int) -> Item:
        return self.items.pop(index)

    def replace(self, index: int, item: Item | None) -> None:
        """Put item in the slot. None empties the slot."""
        if item is None:
            del self.items[index]
        else:
            self.items[index] = item


@dataclass
class Equipment:
    """What the player is currently wearing"""

    worn: dict[EquipSlot, Equippable] = field(default_factory=dict)

    def __getitem__(self, slot: EquipSlot) -> Equippable | None:
        return self.worn.get(slot)

    def __iter__(self) -> Iterator[Equippable]:
        return iter(self.worn.values())

    @property
    def bonus(self) -> Stats:
        """Everything worn, added together."""
        return sum((item.bonus for item in self), Stats())

    def equip(self, item: Equippable) -> Equippable | None:
        """Wear item in its own slot. Returns the item that was displaced, if any."""
        displaced = self.worn.get(item.slot)
        self.worn[item.slot] = item
        return displaced
