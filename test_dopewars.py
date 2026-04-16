# test_dopewars.py
import random
from dopewars import GameState, GOODS, LOCATIONS, generate_prices


def test_gamestate_defaults():
    random.seed(42)
    state = GameState()
    assert state.cash == 2000
    assert state.debt == 5500
    assert state.bank == 0
    assert state.capacity == 100
    assert state.day == 1
    assert state.guns == 0
    assert state.health == 100
    assert state.current_location in LOCATIONS
    assert all(state.inventory[g] == 0 for g in GOODS)


def test_generate_prices_within_ranges():
    random.seed(42)
    prices = generate_prices()
    assert set(prices.keys()) == set(GOODS.keys())
    for good, price in prices.items():
        low, high = GOODS[good]
        assert low <= price <= high, f"{good}: {price} not in [{low}, {high}]"


def test_generate_prices_vary_with_seed():
    random.seed(1)
    prices_a = generate_prices()
    random.seed(2)
    prices_b = generate_prices()
    assert prices_a != prices_b
