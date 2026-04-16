# dopewars.py
from dataclasses import dataclass, field
import random

LOCATIONS = ["Bronx", "Ghetto", "Central Park", "Manhattan", "Coney Island", "Brooklyn"]

GOODS = {
    "Cocaine": (15000, 30000),
    "Heroin": (5000, 14000),
    "Acid": (1000, 4500),
    "Weed": (300, 900),
    "Speed": (70, 250),
    "Ludes": (10, 60),
}


@dataclass
class GameState:
    cash: int = 2000
    debt: int = 5500
    bank: int = 0
    inventory: dict[str, int] = field(default_factory=lambda: {g: 0 for g in GOODS})
    capacity: int = 100
    current_location: str = field(default_factory=lambda: random.choice(LOCATIONS))
    day: int = 1
    guns: int = 0
    health: int = 100


def generate_prices() -> dict[str, int]:
    return {good: random.randint(low, high) for good, (low, high) in GOODS.items()}


def buy(state: GameState, good: str, quantity: int, price: int) -> str | None:
    cost = price * quantity
    if cost > state.cash:
        return "You can't afford that!"
    carried = sum(state.inventory.values())
    if carried + quantity > state.capacity:
        return "You can't carry that much!"
    state.cash -= cost
    state.inventory[good] += quantity
    return None


def sell(state: GameState, good: str, quantity: int, price: int) -> str | None:
    if state.inventory[good] < quantity:
        return "You don't have that many!"
    state.cash += price * quantity
    state.inventory[good] -= quantity
    return None
