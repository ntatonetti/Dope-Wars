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


def display_status(state: GameState) -> None:
    print(f"\n{'=' * 50}")
    print(f" Day: {state.day}/30  |  {state.current_location}")
    print(f" Cash: ${state.cash:,}  |  Debt: ${state.debt:,}  |  Bank: ${state.bank:,}")
    print(f" Guns: {state.guns}  |  Health: {state.health}  |  Space: {state.capacity - sum(state.inventory.values())}")
    print(f"{'=' * 50}")


def display_market(prices: dict[str, int], inventory: dict[str, int]) -> None:
    print(f"\n{'Goods':<12} {'Price':>10} {'You Have':>10}")
    print("-" * 34)
    for i, (good, price) in enumerate(prices.items(), 1):
        owned = inventory[good]
        print(f" {i}. {good:<8} ${price:>8,} {owned:>10}")


def get_choice(prompt: str, valid: list[str]) -> str:
    while True:
        raw = input(prompt).strip().upper()
        if raw in valid:
            return raw
        print("Invalid choice. Try again.")


def get_amount(prompt: str, max_val: int) -> int | None:
    raw = input(prompt).strip()
    if not raw:
        return None
    try:
        val = int(raw)
    except ValueError:
        print("Enter a number.")
        return None
    if val <= 0:
        print("Must be a positive number.")
        return None
    if val > max_val:
        print(f"Maximum is {max_val}.")
        return None
    return val


def run_combat(state: GameState, num_cops: int) -> None:
    print(f"\nOfficer Hardass and {num_cops} cops are chasing you!")
    while num_cops > 0 and state.health > 0:
        print(f"\n Cops: {num_cops}  |  Health: {state.health}")
        options = ["R"]
        prompt_parts = ["(R)un"]
        if state.guns > 0:
            options.append("F")
            prompt_parts.append("(F)ight")
        choice_str = get_choice(" " + " or ".join(prompt_parts) + "? ", options)
        choice = "run" if choice_str == "R" else "fight"
        num_cops, escaped, msg = combat_round(state, num_cops, choice)
        print(f" {msg}")
        if escaped:
            return
    if state.health <= 0:
        print(" You're dead!")


def process_events(state: GameState, events: list[tuple[str, str, int]]) -> None:
    for etype, msg, data in events:
        if etype == "cops":
            run_combat(state, data)
            if state.health <= 0:
                return
        elif etype == "gun_offer":
            print(f"\n {msg}")
            if state.cash >= 400:
                choice = get_choice(" (Y)es or (N)o? ", ["Y", "N"])
                if choice == "Y":
                    state.cash -= 400
                    state.guns += 1
                    print(" You bought a gun!")
            else:
                print(" You can't afford it.")
        elif etype == "coat_offer":
            print(f"\n {msg}")
            if state.cash >= 200:
                choice = get_choice(" (Y)es or (N)o? ", ["Y", "N"])
                if choice == "Y":
                    state.cash -= 200
                    state.capacity += 10
                    print(" You bought a trench coat! Carrying capacity increased.")
            else:
                print(" You can't afford it.")
        else:
            print(f"\n {msg}")


def main() -> None:
    print("\n" + "=" * 50)
    print("  DOPE WARS")
    print("  Buy low. Sell high. Don't get killed.")
    print("=" * 50)

    while True:
        state = GameState()
        prices = generate_prices()

        while state.day <= 30 and state.health > 0:
            display_status(state)
            display_market(prices, state.inventory)

            action = get_choice(
                "\n (B)uy, (S)ell, (J)et, (V)isit loan shark, (D)eposit/withdraw? ",
                ["B", "S", "J", "V", "D"],
            )

            if action == "B":
                display_market(prices, state.inventory)
                good_idx = get_amount("Which good? (number) ", len(GOODS))
                if good_idx is None:
                    continue
                good = list(GOODS.keys())[good_idx - 1]
                price = prices[good]
                max_afford = state.cash // price if price > 0 else 0
                max_carry = state.capacity - sum(state.inventory.values())
                max_qty = min(max_afford, max_carry)
                if max_qty <= 0:
                    print("You can't buy any of that.")
                    continue
                qty = get_amount(f"How many {good}? (max {max_qty}) ", max_qty)
                if qty is None:
                    continue
                err = buy(state, good, qty, price)
                if err:
                    print(err)
                else:
                    print(f"You bought {qty} {good}.")

            elif action == "S":
                owned = {g: q for g, q in state.inventory.items() if q > 0}
                if not owned:
                    print("You don't have anything to sell!")
                    continue
                display_market(prices, state.inventory)
                good_idx = get_amount("Which good? (number) ", len(GOODS))
                if good_idx is None:
                    continue
                good = list(GOODS.keys())[good_idx - 1]
                if state.inventory[good] <= 0:
                    print(f"You don't have any {good}.")
                    continue
                qty = get_amount(f"How many {good}? (max {state.inventory[good]}) ", state.inventory[good])
                if qty is None:
                    continue
                err = sell(state, good, qty, prices[good])
                if err:
                    print(err)
                else:
                    print(f"You sold {qty} {good} for ${prices[good] * qty:,}.")

            elif action == "J":
                destinations = [loc for loc in LOCATIONS if loc != state.current_location]
                print("\nWhere to?")
                for i, loc in enumerate(destinations, 1):
                    print(f" {i}. {loc}")
                dest_idx = get_amount("? ", len(destinations))
                if dest_idx is None:
                    continue
                state.current_location = destinations[dest_idx - 1]
                state.day += 1
                apply_interest(state)
                prices = generate_prices()
                events = roll_events(state, prices)
                process_events(state, events)

            elif action == "V":
                print(f"\nDebt: ${state.debt:,}")
                if state.debt == 0:
                    print("You don't owe anything!")
                    continue
                amt = get_amount(f"How much to repay? (max ${min(state.cash, state.debt):,}) ", min(state.cash, state.debt))
                if amt is None:
                    continue
                err = repay_debt(state, amt)
                if err:
                    print(err)
                else:
                    print(f"You repaid ${amt:,}. Remaining debt: ${state.debt:,}")

            elif action == "D":
                choice = get_choice(" (D)eposit or (W)ithdraw? ", ["D", "W"])
                if choice == "D":
                    if state.cash <= 0:
                        print("You have no cash to deposit.")
                        continue
                    amt = get_amount(f"Deposit how much? (max ${state.cash:,}) ", state.cash)
                    if amt is None:
                        continue
                    err = deposit(state, amt)
                    if err:
                        print(err)
                    else:
                        print(f"Deposited ${amt:,}.")
                else:
                    if state.bank <= 0:
                        print("Your bank account is empty.")
                        continue
                    amt = get_amount(f"Withdraw how much? (max ${state.bank:,}) ", state.bank)
                    if amt is None:
                        continue
                    err = withdraw(state, amt)
                    if err:
                        print(err)
                    else:
                        print(f"Withdrew ${amt:,}.")

        # Game over
        score = state.cash + state.bank - state.debt
        print(f"\n{'=' * 50}")
        if state.health <= 0:
            print("  YOU'RE DEAD!")
        else:
            print("  GAME OVER — 30 days are up!")
        print(f"\n  Cash:  ${state.cash:,}")
        print(f"  Bank:  ${state.bank:,}")
        print(f"  Debt: -${state.debt:,}")
        print(f"  {'─' * 20}")
        print(f"  Score: ${score:,}")
        print(f"{'=' * 50}")

        again = get_choice("\nPlay again? (Y/N) ", ["Y", "N"])
        if again == "N":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nThanks for playing!")
