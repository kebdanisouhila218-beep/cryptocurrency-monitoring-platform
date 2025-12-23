import pytest
from unittest.mock import Mock

from services.portfolio_service import (
    calculate_portfolio_total_value,
    calculate_position_value,
    execute_buy,
    execute_sell,
    weighted_average_price,
)


def test_weighted_average_price():
    old_quantity = 1.0
    old_avg_price = 100.0
    new_quantity = 1.0
    new_price = 200.0
    assert weighted_average_price(old_quantity, old_avg_price, new_quantity, new_price) == 150.0


def test_calculate_portfolio_value():
    portfolio = {"_id": "p1", "current_balance": 100.0}

    positions_collection = Mock()
    positions_collection.find.return_value = [{"current_value": 50.0}, {"current_value": 25.0}]

    total_value, cash, positions_value = calculate_portfolio_total_value(portfolio, positions_collection)

    assert total_value == 175.0
    assert cash == 100.0
    assert positions_value == 75.0


def test_execute_buy_success():
    portfolios_collection = Mock()
    positions_collection = Mock()
    transactions_collection = Mock()
    prices_collection = Mock()

    portfolio = {"_id": "p1", "current_balance": 1000.0}

    positions_collection.find_one.return_value = None
    prices_collection.find_one.return_value = None

    result = execute_buy(
        portfolios_collection,
        positions_collection,
        transactions_collection,
        prices_collection,
        portfolio,
        "BTC",
        1.0,
        100.0,
        0.0,
        None,
    )

    assert result["price"] == 100.0
    assert result["fee"] == 0.0
    assert result["total_amount"] == 100.0
    assert result["current_balance"] == 900.0

    assert positions_collection.insert_one.called
    assert portfolios_collection.update_one.called
    assert transactions_collection.insert_one.called


def test_execute_buy_insufficient_balance():
    portfolios_collection = Mock()
    positions_collection = Mock()
    transactions_collection = Mock()
    prices_collection = Mock()

    portfolio = {"_id": "p1", "current_balance": 10.0}

    with pytest.raises(ValueError) as e:
        execute_buy(
            portfolios_collection,
            positions_collection,
            transactions_collection,
            prices_collection,
            portfolio,
            "BTC",
            1.0,
            100.0,
            0.0,
            None,
        )

    assert str(e.value) == "INSUFFICIENT_BALANCE"


def test_execute_sell_success():
    portfolios_collection = Mock()
    positions_collection = Mock()
    transactions_collection = Mock()
    prices_collection = Mock()

    portfolio = {"_id": "p1", "current_balance": 0.0}

    positions_collection.find_one.return_value = {
        "_id": "pos1",
        "portfolio_id": "p1",
        "crypto_symbol": "BTC",
        "quantity": 2.0,
        "average_buy_price": 50.0,
        "total_invested": 100.0,
    }

    result = execute_sell(
        portfolios_collection,
        positions_collection,
        transactions_collection,
        prices_collection,
        portfolio,
        "BTC",
        1.0,
        100.0,
        0.0,
        None,
    )

    assert result["price"] == 100.0
    assert result["fee"] == 0.0
    assert result["total_amount"] == 100.0
    assert result["current_balance"] == 100.0
    assert result["remaining_quantity"] == 1.0

    assert positions_collection.update_one.called
    assert portfolios_collection.update_one.called
    assert transactions_collection.insert_one.called


def test_execute_sell_insufficient_quantity():
    portfolios_collection = Mock()
    positions_collection = Mock()
    transactions_collection = Mock()
    prices_collection = Mock()

    portfolio = {"_id": "p1", "current_balance": 0.0}

    positions_collection.find_one.return_value = {
        "_id": "pos1",
        "portfolio_id": "p1",
        "crypto_symbol": "BTC",
        "quantity": 0.5,
        "average_buy_price": 50.0,
        "total_invested": 25.0,
    }

    with pytest.raises(ValueError) as e:
        execute_sell(
            portfolios_collection,
            positions_collection,
            transactions_collection,
            prices_collection,
            portfolio,
            "BTC",
            1.0,
            100.0,
            0.0,
            None,
        )

    assert str(e.value) == "INSUFFICIENT_QUANTITY"
