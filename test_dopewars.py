# test_dopewars.py
import random
from dopewars import GameState, GOODS, LOCATIONS, generate_prices, buy, sell
from dopewars import deposit, withdraw, repay_debt, apply_interest


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


def test_deposit_success():
    state = GameState()
    state.cash = 1000
    err = deposit(state, 600)
    assert err is None
    assert state.cash == 400
    assert state.bank == 600


def test_deposit_more_than_cash():
    state = GameState()
    state.cash = 100
    err = deposit(state, 200)
    assert err is not None
    assert state.cash == 100
    assert state.bank == 0


def test_withdraw_success():
    state = GameState()
    state.bank = 500
    state.cash = 0
    err = withdraw(state, 300)
    assert err is None
    assert state.bank == 200
    assert state.cash == 300


def test_withdraw_more_than_bank():
    state = GameState()
    state.bank = 100
    err = withdraw(state, 200)
    assert err is not None
    assert state.bank == 100


def test_repay_debt_success():
    state = GameState()
    state.cash = 3000
    state.debt = 5500
    err = repay_debt(state, 2000)
    assert err is None
    assert state.cash == 1000
    assert state.debt == 3500


def test_repay_debt_more_than_owed():
    state = GameState()
    state.cash = 10000
    state.debt = 500
    err = repay_debt(state, 1000)
    assert err is None
    assert state.cash == 9500
    assert state.debt == 0


def test_repay_debt_not_enough_cash():
    state = GameState()
    state.cash = 100
    state.debt = 5500
    err = repay_debt(state, 200)
    assert err is not None
    assert state.cash == 100
    assert state.debt == 5500


def test_apply_interest():
    state = GameState()
    state.debt = 1000
    apply_interest(state)
    assert state.debt == 1100


def test_apply_interest_zero_debt():
    state = GameState()
    state.debt = 0
    apply_interest(state)
    assert state.debt == 0


from dopewars import roll_events


def test_roll_events_price_spike():
    state = GameState()
    prices = generate_prices()
    random.seed(0)
    # Run many times to verify spike behavior when triggered
    found_spike = False
    for seed in range(200):
        random.seed(seed)
        prices = generate_prices()
        events = roll_events(state, prices)
        for etype, msg, _data in events:
            if etype == "price_spike":
                found_spike = True
                # Find which good spiked — check it's above normal max
                for good in ["Weed", "Speed", "Ludes"]:
                    if good in msg:
                        assert prices[good] > GOODS[good][1]
                        break
    assert found_spike, "No price spike found in 200 seeds"


def test_roll_events_price_crash():
    state = GameState()
    found_crash = False
    for seed in range(200):
        random.seed(seed)
        prices = generate_prices()
        events = roll_events(state, prices)
        for etype, msg, _data in events:
            if etype == "price_crash":
                found_crash = True
                for good in ["Cocaine", "Heroin", "Acid"]:
                    if good in msg:
                        assert prices[good] < GOODS[good][0]
                        break
    assert found_crash, "No price crash found in 200 seeds"


def test_roll_events_find_goods():
    found = False
    for seed in range(200):
        random.seed(seed)
        state = GameState()
        prices = generate_prices()
        events = roll_events(state, prices)
        for etype, msg, _data in events:
            if etype == "find_goods":
                found = True
                assert sum(state.inventory.values()) > 0
    assert found, "No find-goods event in 200 seeds"


def test_roll_events_mugger():
    found = False
    for seed in range(200):
        random.seed(seed)
        state = GameState()
        prices = generate_prices()
        events = roll_events(state, prices)
        for etype, msg, _data in events:
            if etype == "mugger":
                found = True
                assert state.cash < 2000
    assert found, "No mugger event in 200 seeds"


def test_roll_events_cops():
    found = False
    for seed in range(200):
        random.seed(seed)
        state = GameState()
        prices = generate_prices()
        events = roll_events(state, prices)
        for etype, msg, data in events:
            if etype == "cops":
                found = True
                assert data >= 1
    assert found, "No cops event in 200 seeds"


def test_roll_events_gun_offer():
    found = False
    for seed in range(200):
        random.seed(seed)
        state = GameState()
        prices = generate_prices()
        events = roll_events(state, prices)
        for etype, msg, _data in events:
            if etype == "gun_offer":
                found = True
    assert found, "No gun offer in 200 seeds"


def test_roll_events_coat_offer():
    found = False
    for seed in range(200):
        random.seed(seed)
        state = GameState()
        prices = generate_prices()
        events = roll_events(state, prices)
        for etype, msg, _data in events:
            if etype == "coat_offer":
                found = True
    assert found, "No coat offer in 200 seeds"
