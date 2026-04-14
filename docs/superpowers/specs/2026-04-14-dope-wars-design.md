# Dope Wars — Design Spec

A faithful terminal remake of the classic TI-83 Dope Wars game in Python. Single-file architecture, simple print/input UI, no external dependencies.

## Tech Stack

- Python 3 (stdlib only)
- Single file: `dopewars.py`
- Run with: `python dopewars.py`

## Game State

A dataclass holding all mutable game state:

| Field | Type | Initial Value | Notes |
|-------|------|---------------|-------|
| cash | int | 2,000 | Player's on-hand money |
| debt | int | 5,500 | Loan shark debt, 10% daily interest |
| bank | int | 0 | Safe storage, not subject to mugging |
| inventory | dict[str, int] | all zeros | Good name -> quantity |
| capacity | int | 100 | Max total items carried |
| current_location | str | random | One of 6 locations |
| day | int | 1 | Advances on travel, game ends after 30 |
| guns | int | 0 | Used in cop fights |
| health | int | 100 | 0 = game over |

Final score = cash + bank - debt.

## Locations

6 locations, travel between any of them is free and costs 1 day:

- Bronx
- Ghetto
- Central Park
- Manhattan
- Coney Island
- Brooklyn

## Goods & Price Ranges

6 goods with base price ranges. Each day at each location, prices are randomly generated within these ranges. Random events can push prices outside these ranges.

| Good | Low | High |
|------|-----|------|
| Cocaine | 15,000 | 30,000 |
| Heroin | 5,000 | 14,000 |
| Acid | 1,000 | 4,500 |
| Weed | 300 | 900 |
| Speed | 70 | 250 |
| Ludes | 10 | 60 |

## Random Events

Events trigger randomly when traveling to a new location.

### Price Events (~15% chance each per travel)

- **Price spike:** "Cops made a bust! {good} prices skyrocket!" or "Addicts are buying {good} at outrageous prices!" — a cheap good's price jumps 4-8x its normal range.
- **Price crash:** "{good} prices have bottomed out!" — an expensive good drops to 1/4-1/8 its normal low.

### Encounter Events (~10-15% chance per travel)

- **Cops:** "Officer Hardass and N cops are chasing you!" — triggers combat (see below).
- **Find goods:** "You find some {good} on the ground!" — free goods added to inventory (if capacity allows).
- **Mugger:** "A mugger attacks!" — lose a random portion of on-hand cash.

### Opportunity Events (~10% chance per travel)

- **Gun:** "Would you like to buy a gun for $400?" — guns help in cop fights.
- **Trench coat:** "Would you like to buy a trench coat for $200?" — increases inventory capacity by 10.

Exact probabilities will be tuned during playtesting.

## Combat (Cops)

Triggered by cop encounter events. Number of cops scales loosely with the day (1-3 early game, up to 6-8 late game).

Each round the player chooses:

- **Run:** Chance of escape based on number of remaining cops. Failure means cops shoot (lose health).
- **Fight:** Requires at least 1 gun. Player kills 1 cop per round. Remaining cops shoot back (lose health).

Combat continues until:
- Player escapes (run succeeds)
- All cops are dead (fight wins)
- Player health reaches 0 (game over)

## Game Loop

Each iteration represents the player at a location, with day advancing on travel:

1. Display status bar: day, location, cash, debt, bank, guns, health
2. Display market prices at current location
3. Player menu:
   - **B)uy** — pick a good, pick a quantity
   - **S)ell** — pick a good from inventory, pick a quantity
   - **J)et** — pick a destination, advances day by 1, rolls random events
   - **V)isit loan shark** — repay any amount of debt up to cash on hand
   - **D)eposit/withdraw bank** — move cash to/from bank
4. On travel: advance day, generate new prices, roll for random events
5. After day 30: game ends, display final score (cash + bank - debt), prompt to play again

## Input Handling

- Simple text prompts with letter/number choices
- Invalid input re-prompts without crashing
- Ctrl+C exits cleanly with a goodbye message

## Architecture

Single file `dopewars.py` containing:

- `GameState` dataclass
- Constants: `LOCATIONS`, `GOODS` (with price ranges), `EVENT_PROBABILITIES`
- Functions: `generate_prices()`, `roll_events()`, `combat()`, `buy()`, `sell()`, `visit_bank()`, `visit_loan_shark()`, `display_status()`, `display_market()`
- `main()` function with the game loop
- `if __name__ == "__main__"` entry point
