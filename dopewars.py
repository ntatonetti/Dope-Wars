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


def deposit(state: GameState, amount: int) -> str | None:
    if amount > state.cash:
        return "You don't have that much cash!"
    state.cash -= amount
    state.bank += amount
    return None


def withdraw(state: GameState, amount: int) -> str | None:
    if amount > state.bank:
        return "You don't have that much in the bank!"
    state.bank -= amount
    state.cash += amount
    return None


def repay_debt(state: GameState, amount: int) -> str | None:
    if amount > state.cash:
        return "You don't have that much cash!"
    amount = min(amount, state.debt)
    state.cash -= amount
    state.debt -= amount
    return None


def apply_interest(state: GameState) -> None:
    state.debt = int(state.debt * 1.10)


def roll_events(state: GameState, prices: dict[str, int]) -> list[tuple[str, str, int]]:
    events = []

    # Price spike (~15% chance) — cheap goods skyrocket
    if random.random() < 0.15:
        good = random.choice(["Weed", "Speed", "Ludes"])
        multiplier = random.randint(4, 8)
        prices[good] = GOODS[good][1] * multiplier
        events.append(("price_spike", f"Cops made a bust! {good} prices skyrocket!", 0))

    # Price crash (~15% chance) — expensive goods bottom out
    if random.random() < 0.15:
        good = random.choice(["Cocaine", "Heroin", "Acid"])
        divisor = random.randint(4, 8)
        prices[good] = GOODS[good][0] // divisor
        events.append(("price_crash", f"{good} prices have bottomed out!", 0))

    # Find goods (~10% chance)
    if random.random() < 0.10:
        good = random.choice(list(GOODS.keys()))
        amount = random.randint(2, 6)
        carried = sum(state.inventory.values())
        space = state.capacity - carried
        amount = min(amount, space)
        if amount > 0:
            state.inventory[good] += amount
            events.append(("find_goods", f"You find {amount} units of {good} on the ground!", 0))

    # Mugger (~10% chance)
    if random.random() < 0.10 and state.cash > 0:
        lost = random.randint(1, max(1, state.cash // 3))
        state.cash -= lost
        events.append(("mugger", f"A mugger attacks! You lose ${lost:,}!", 0))

    # Cops (~15% chance, scales with day)
    if random.random() < 0.15:
        min_cops = 1 + state.day // 10
        max_cops = max(min_cops, min(3 + state.day // 5, 8))
        num_cops = random.randint(min_cops, max_cops)
        events.append(("cops", f"Officer Hardass and {num_cops} cops are chasing you!", num_cops))

    # Gun offer (~10% chance)
    if random.random() < 0.10:
        events.append(("gun_offer", "Would you like to buy a gun for $400?", 400))

    # Trench coat offer (~10% chance)
    if random.random() < 0.10:
        events.append(("coat_offer", "Would you like to buy a trench coat for $200?", 200))

    return events


def combat_round(state: GameState, num_cops: int, choice: str) -> tuple[int, bool, str]:
    """Process one round of combat. Returns (remaining_cops, escaped, message)."""
    if choice == "run":
        escape_chance = max(0.2, min(0.9, 1.0 - num_cops * 0.1))
        if random.random() < escape_chance:
            return num_cops, True, "You escaped!"
        damage = num_cops * random.randint(3, 7)
        state.health = max(0, state.health - damage)
        return num_cops, False, f"You couldn't escape! They hit you for {damage} damage."

    if choice == "fight":
        if state.guns <= 0:
            return num_cops, False, "You don't have any guns!"
        num_cops -= 1
        if num_cops > 0:
            damage = num_cops * random.randint(3, 7)
            state.health = max(0, state.health - damage)
            return num_cops, False, f"You killed a cop! {num_cops} remaining. They hit you for {damage} damage."
        return num_cops, False, "You killed the last cop!"

    return num_cops, False, ""
