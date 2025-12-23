import pytest
from fastapi.testclient import TestClient

from main import app
from auth import users_collection
from database import get_portfolios_collection, get_positions_collection, get_transactions_collection


client = TestClient(app)


def _register_and_login(username: str, email: str, password: str) -> str:
    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    login = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


@pytest.fixture(autouse=True)
def cleanup():
    usernames = ["portfolio_user1", "portfolio_user2"]

    users_collection.delete_many({"username": {"$in": usernames}})
    yield

    user_docs = list(users_collection.find({"username": {"$in": usernames}}))
    user_ids = [str(u["_id"]) for u in user_docs]

    portfolios_collection = get_portfolios_collection()
    positions_collection = get_positions_collection()
    transactions_collection = get_transactions_collection()

    if user_ids:
        portfolio_ids = [str(p["_id"]) for p in portfolios_collection.find({"user_id": {"$in": user_ids}})]
        if portfolio_ids:
            positions_collection.delete_many({"portfolio_id": {"$in": portfolio_ids}})
            transactions_collection.delete_many({"portfolio_id": {"$in": portfolio_ids}})
        portfolios_collection.delete_many({"user_id": {"$in": user_ids}})

    users_collection.delete_many({"username": {"$in": usernames}})


def test_unauthorized_access():
    r = client.get("/portfolio")
    assert r.status_code == 401


def test_create_portfolio_and_get_portfolios():
    token = _register_and_login("portfolio_user1", "portfolio_user1@example.com", "password12345")

    r = client.post(
        "/portfolio",
        json={"name": "Mon Portfolio", "initial_balance": 10000.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Mon Portfolio"
    assert data["initial_balance"] == 10000.0
    assert data["current_balance"] == 10000.0

    r2 = client.get(
        "/portfolio",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    portfolios = r2.json()
    assert len(portfolios) >= 1


def test_buy_sell_positions_transactions_and_ownership():
    token1 = _register_and_login("portfolio_user1", "portfolio_user1@example.com", "password12345")
    token2 = _register_and_login("portfolio_user2", "portfolio_user2@example.com", "password12345")

    create = client.post(
        "/portfolio",
        json={"name": "P1", "initial_balance": 10000.0},
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert create.status_code == 201
    portfolio_id = create.json()["id"]

    buy1 = client.post(
        f"/portfolio/{portfolio_id}/buy",
        json={"crypto_symbol": "BTC", "quantity": 0.1, "price": 50000.0},
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert buy1.status_code == 200

    buy2 = client.post(
        f"/portfolio/{portfolio_id}/buy",
        json={"crypto_symbol": "ETH", "quantity": 1.0, "price": 3000.0},
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert buy2.status_code == 200

    sell = client.post(
        f"/portfolio/{portfolio_id}/sell",
        json={"crypto_symbol": "BTC", "quantity": 0.05, "price": 55000.0},
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert sell.status_code == 200

    positions = client.get(
        f"/portfolio/{portfolio_id}/positions",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert positions.status_code == 200
    pos = positions.json()
    symbols = {p["crypto_symbol"]: p for p in pos}
    assert symbols["BTC"]["quantity"] == pytest.approx(0.05)
    assert symbols["ETH"]["quantity"] == pytest.approx(1.0)

    txs = client.get(
        f"/portfolio/{portfolio_id}/transactions",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert txs.status_code == 200
    assert len(txs.json()) == 3

    forbidden = client.get(
        f"/portfolio/{portfolio_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert forbidden.status_code == 403
