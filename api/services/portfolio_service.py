from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId


def weighted_average_price(
    old_quantity: float,
    old_avg_price: float,
    new_quantity: float,
    new_price: float,
) -> float:
    if old_quantity <= 0:
        return float(new_price)
    if new_quantity <= 0:
        return float(old_avg_price)
    return ((old_quantity * old_avg_price) + (new_quantity * new_price)) / (old_quantity + new_quantity)


def calculate_position_value(quantity: float, current_price: float) -> float:
    return float(quantity) * float(current_price)


def calculate_profit_loss(total_invested: float, current_value: float) -> tuple[float, float]:
    invested = float(total_invested)
    value = float(current_value)
    pl = value - invested
    if invested <= 0:
        return pl, 0.0
    return pl, (pl / invested) * 100.0


def get_latest_price(prices_collection, crypto_symbol: str) -> Optional[float]:
    latest = prices_collection.find_one(
        {"symbol": crypto_symbol.upper()},
        sort=[("timestamp", -1)],
    )
    if not latest:
        return None
    price = latest.get("price_usd")
    if price is None:
        return None
    try:
        return float(price)
    except Exception:
        return None


def get_portfolio_or_404(portfolios_collection, portfolio_id: str) -> dict:
    try:
        obj_id = ObjectId(portfolio_id)
    except InvalidId:
        raise ValueError("INVALID_PORTFOLIO_ID")

    portfolio = portfolios_collection.find_one({"_id": obj_id})
    if not portfolio:
        raise LookupError("PORTFOLIO_NOT_FOUND")
    return portfolio


def ensure_portfolio_owner(portfolio: dict, user_id: str) -> None:
    if portfolio.get("user_id") != user_id:
        raise PermissionError("FORBIDDEN")


def update_positions_prices(
    positions_collection,
    prices_collection,
    portfolio_id: str,
) -> None:
    positions = list(positions_collection.find({"portfolio_id": portfolio_id}))
    now = datetime.utcnow()

    for pos in positions:
        symbol = pos.get("crypto_symbol")
        if not symbol:
            continue

        latest_price = get_latest_price(prices_collection, symbol)
        if latest_price is None:
            latest_price = float(pos.get("current_price", 0.0))

        quantity = float(pos.get("quantity", 0.0))
        avg_buy = float(pos.get("average_buy_price", 0.0))
        total_invested = float(pos.get("total_invested", avg_buy * quantity))

        current_value = calculate_position_value(quantity, latest_price)
        pl, pl_pct = calculate_profit_loss(total_invested, current_value)

        positions_collection.update_one(
            {"_id": pos["_id"]},
            {
                "$set": {
                    "current_price": latest_price,
                    "total_invested": total_invested,
                    "current_value": current_value,
                    "profit_loss": pl,
                    "profit_loss_percent": pl_pct,
                    "updated_at": now,
                }
            },
        )


def calculate_portfolio_total_value(
    portfolio: dict,
    positions_collection,
) -> tuple[float, float, float]:
    cash = float(portfolio.get("current_balance", 0.0))
    positions = list(positions_collection.find({"portfolio_id": str(portfolio["_id"])}, {"current_value": 1}))
    positions_value = 0.0
    for p in positions:
        try:
            positions_value += float(p.get("current_value", 0.0))
        except Exception:
            continue
    return cash + positions_value, cash, positions_value


def execute_buy(
    portfolios_collection,
    positions_collection,
    transactions_collection,
    prices_collection,
    portfolio: dict,
    crypto_symbol: str,
    quantity: float,
    price: Optional[float],
    fee_percent: float,
    notes: Optional[str],
) -> dict:
    symbol = crypto_symbol.upper().strip()
    qty = float(quantity)
    if qty <= 0:
        raise ValueError("INVALID_QUANTITY")

    px = float(price) if price is not None else None
    if px is None:
        px = get_latest_price(prices_collection, symbol)
    if px is None or px <= 0:
        raise ValueError("PRICE_NOT_AVAILABLE")

    fee_pct = float(fee_percent)
    if fee_pct < 0:
        raise ValueError("INVALID_FEE")

    total_amount = qty * px
    fee = total_amount * (fee_pct / 100.0)
    total_cost = total_amount + fee

    current_balance = float(portfolio.get("current_balance", 0.0))
    if current_balance < total_cost:
        raise ValueError("INSUFFICIENT_BALANCE")

    portfolio_id = str(portfolio["_id"])

    pos = positions_collection.find_one({"portfolio_id": portfolio_id, "crypto_symbol": symbol})

    now = datetime.utcnow()

    if pos:
        old_qty = float(pos.get("quantity", 0.0))
        old_avg = float(pos.get("average_buy_price", 0.0))
        new_qty_total = old_qty + qty
        new_avg = weighted_average_price(old_qty, old_avg, qty, px)
        new_total_invested = float(pos.get("total_invested", old_avg * old_qty)) + total_amount

        current_price = get_latest_price(prices_collection, symbol)
        if current_price is None:
            current_price = px
        current_value = calculate_position_value(new_qty_total, current_price)
        pl, pl_pct = calculate_profit_loss(new_total_invested, current_value)

        positions_collection.update_one(
            {"_id": pos["_id"]},
            {
                "$set": {
                    "quantity": new_qty_total,
                    "average_buy_price": new_avg,
                    "current_price": current_price,
                    "total_invested": new_total_invested,
                    "current_value": current_value,
                    "profit_loss": pl,
                    "profit_loss_percent": pl_pct,
                    "updated_at": now,
                }
            },
        )
    else:
        current_price = get_latest_price(prices_collection, symbol)
        if current_price is None:
            current_price = px
        current_value = calculate_position_value(qty, current_price)
        total_invested = total_amount
        pl, pl_pct = calculate_profit_loss(total_invested, current_value)

        positions_collection.insert_one(
            {
                "portfolio_id": portfolio_id,
                "crypto_symbol": symbol,
                "quantity": qty,
                "average_buy_price": px,
                "current_price": current_price,
                "total_invested": total_invested,
                "current_value": current_value,
                "profit_loss": pl,
                "profit_loss_percent": pl_pct,
                "updated_at": now,
            }
        )

    new_balance = current_balance - total_cost
    portfolios_collection.update_one(
        {"_id": portfolio["_id"]},
        {"$set": {"current_balance": new_balance, "updated_at": now}},
    )

    tx_doc: dict[str, Any] = {
        "portfolio_id": portfolio_id,
        "transaction_type": "BUY",
        "crypto_symbol": symbol,
        "quantity": qty,
        "price": px,
        "total_amount": total_amount,
        "fee": fee,
        "timestamp": now,
        "notes": notes,
    }
    transactions_collection.insert_one(tx_doc)

    return {"price": px, "fee": fee, "total_amount": total_amount, "current_balance": new_balance}


def execute_sell(
    portfolios_collection,
    positions_collection,
    transactions_collection,
    prices_collection,
    portfolio: dict,
    crypto_symbol: str,
    quantity: float,
    price: Optional[float],
    fee_percent: float,
    notes: Optional[str],
) -> dict:
    symbol = crypto_symbol.upper().strip()
    qty = float(quantity)
    if qty <= 0:
        raise ValueError("INVALID_QUANTITY")

    px = float(price) if price is not None else None
    if px is None:
        px = get_latest_price(prices_collection, symbol)
    if px is None or px <= 0:
        raise ValueError("PRICE_NOT_AVAILABLE")

    fee_pct = float(fee_percent)
    if fee_pct < 0:
        raise ValueError("INVALID_FEE")

    total_amount = qty * px
    fee = total_amount * (fee_pct / 100.0)
    proceeds = total_amount - fee

    portfolio_id = str(portfolio["_id"])
    pos = positions_collection.find_one({"portfolio_id": portfolio_id, "crypto_symbol": symbol})
    if not pos:
        raise ValueError("POSITION_NOT_FOUND")

    old_qty = float(pos.get("quantity", 0.0))
    if old_qty < qty:
        raise ValueError("INSUFFICIENT_QUANTITY")

    now = datetime.utcnow()

    avg_buy = float(pos.get("average_buy_price", 0.0))
    remaining_qty = old_qty - qty

    old_total_invested = float(pos.get("total_invested", avg_buy * old_qty))
    invested_reduction = avg_buy * qty
    new_total_invested = max(0.0, old_total_invested - invested_reduction)

    if remaining_qty <= 0:
        positions_collection.delete_one({"_id": pos["_id"]})
    else:
        current_price = get_latest_price(prices_collection, symbol)
        if current_price is None:
            current_price = px
        current_value = calculate_position_value(remaining_qty, current_price)
        pl, pl_pct = calculate_profit_loss(new_total_invested, current_value)

        positions_collection.update_one(
            {"_id": pos["_id"]},
            {
                "$set": {
                    "quantity": remaining_qty,
                    "current_price": current_price,
                    "total_invested": new_total_invested,
                    "current_value": current_value,
                    "profit_loss": pl,
                    "profit_loss_percent": pl_pct,
                    "updated_at": now,
                }
            },
        )

    current_balance = float(portfolio.get("current_balance", 0.0))
    new_balance = current_balance + proceeds
    portfolios_collection.update_one(
        {"_id": portfolio["_id"]},
        {"$set": {"current_balance": new_balance, "updated_at": now}},
    )

    tx_doc: dict[str, Any] = {
        "portfolio_id": portfolio_id,
        "transaction_type": "SELL",
        "crypto_symbol": symbol,
        "quantity": qty,
        "price": px,
        "total_amount": total_amount,
        "fee": fee,
        "timestamp": now,
        "notes": notes,
    }
    transactions_collection.insert_one(tx_doc)

    realized_profit = (px - avg_buy) * qty - fee

    return {
        "price": px,
        "fee": fee,
        "total_amount": total_amount,
        "current_balance": new_balance,
        "realized_profit": realized_profit,
        "remaining_quantity": remaining_qty,
    }
