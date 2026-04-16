# test_dopewars.py
import random
from dopewars import GameState, GOODS, LOCATIONS, generate_prices, buy, sell


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


def test_buy_success():
    state = GameState()
    state.cash = 1000
    err = buy(state, "Ludes", 10, 50)
    assert err is None
    assert state.cash == 500
    assert state.inventory["Ludes"] == 10


def test_buy_not_enough_cash():
    state = GameState()
    state.cash = 100
    err = buy(state, "Cocaine", 1, 20000)
    assert err is not None
    assert state.cash == 100
    assert state.inventory["Cocaine"] == 0


def test_buy_exceeds_capacity():
    state = GameState()
    state.cash = 999999
    state.inventory["Ludes"] = 95
    err = buy(state, "Weed", 10, 1)
    assert err is not None
    assert state.inventory["Weed"] == 0


def test_buy_exactly_fills_capacity():
    state = GameState()
    state.cash = 999999
    state.inventory["Ludes"] = 90
    err = buy(state, "Weed", 10, 1)
    assert err is None
    assert state.inventory["Weed"] == 10


def test_sell_success():
    state = GameState()
    state.cash = 0
    state.inventory["Acid"] = 5
    err = sell(state, "Acid", 3, 2000)
    assert err is None
    assert state.cash == 6000
    assert state.inventory["Acid"] == 2


def test_sell_more_than_owned():
    state = GameState()
    state.inventory["Weed"] = 2
    err = sell(state, "Weed", 5, 500)
    assert err is not None
    assert state.inventory["Weed"] == 2
