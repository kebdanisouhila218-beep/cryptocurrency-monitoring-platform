from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient


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


def calculate_profit_loss(total_value_usd: float, total_invested_usd: float) -> Tuple[float, float]:
    """Calculate Profit/Loss (P&L) in USD and percent.

    Args:
        total_value_usd: Current total value (USD).
        total_invested_usd: Total invested amount (USD).

    Returns:
        (profit_loss_usd, profit_loss_percent)

    Notes:
        - If total_invested_usd <= 0, percent is 0.
        - Values are rounded to 2 decimals.
        - Includes debug prints.
    """

    try:
        total_value = float(total_value_usd)
        invested = float(total_invested_usd)
    except Exception:
        print(f"[portfolio_service] ⚠️ calculate_profit_loss invalid inputs: value={total_value_usd}, invested={total_invested_usd}")
        return 0.0, 0.0

    profit_loss = total_value - invested
    if invested <= 0:
        pl_usd = round(profit_loss, 2)
        print(f"[portfolio_service] calculate_profit_loss value={total_value} invested={invested} => pl={pl_usd} pct=0.0")
        return pl_usd, 0.0

    pct = (profit_loss / invested) * 100.0
    pl_usd = round(profit_loss, 2)
    pl_pct = round(pct, 2)
    print(f"[portfolio_service] calculate_profit_loss value={total_value} invested={invested} => pl={pl_usd} pct={pl_pct}")
    return pl_usd, pl_pct


def calculate_portfolio_value(holdings: Dict[str, float], prices_collection) -> float:
    """Calculate the total USD value of a holdings dict.

    Args:
        holdings: Dict of {crypto_symbol: quantity}
        prices_collection: MongoDB collection containing price documents.

    Returns:
        Total value in USD (rounded to 2 decimals).

    Behavior:
        - Symbols are forced to UPPERCASE.
        - If a price is missing, that crypto contributes 0 and a warning is printed.
        - Prints debug information.
    """

    total = 0.0
    if not holdings:
        print("[portfolio_service] calculate_portfolio_value holdings empty")
        return 0.0

    for symbol, qty in holdings.items():
        sym = str(symbol).upper().strip()
        if not sym:
            continue

        try:
            quantity = float(qty)
        except Exception:
            print(f"[portfolio_service] ⚠️ Invalid quantity for {sym}: {qty}")
            continue

        if quantity <= 0:
            continue

        current_price = get_latest_price(prices_collection, sym)
        if current_price is None:
            print(f"[portfolio_service] ⚠️ Price not found for {sym}. Using 0.")
            current_price = 0.0

        subtotal = quantity * float(current_price)
        total += subtotal
        print(f"[portfolio_service] value {sym}: qty={quantity} price={current_price} subtotal={round(subtotal, 2)}")

    total_rounded = round(total, 2)
    print(f"[portfolio_service] calculate_portfolio_value total={total_rounded}")
    return total_rounded


def update_holdings_after_buy(holdings: Dict[str, float], crypto_symbol: str, quantity: float) -> Dict[str, float]:
    """Update holdings after a BUY operation.

    Args:
        holdings: Current holdings {symbol: quantity}
        crypto_symbol: Symbol to buy (any case)
        quantity: Quantity bought (> 0)

    Returns:
        Updated holdings dict.
    """

    sym = str(crypto_symbol).upper().strip()
    qty = float(quantity)
    if not sym or qty <= 0:
        print(f"[portfolio_service] ⚠️ update_holdings_after_buy invalid inputs sym={crypto_symbol} qty={quantity}")
        return dict(holdings or {})

    new_holdings = dict(holdings or {})
    current = float(new_holdings.get(sym, 0.0) or 0.0)
    new_holdings[sym] = round(current + qty, 8)
    print(f"[portfolio_service] BUY holdings {sym}: {current} + {qty} => {new_holdings[sym]}")
    return new_holdings


def update_holdings_after_sell(
    holdings: Dict[str, float],
    crypto_symbol: str,
    quantity: float,
) -> Tuple[Dict[str, float], bool, str]:
    """Update holdings after a SELL operation.

    Checks if there is enough quantity to sell. If quantity becomes 0, removes the symbol.

    Returns:
        (new_holdings, success, message)
    """

    sym = str(crypto_symbol).upper().strip()
    qty = float(quantity)
    if not sym or qty <= 0:
        return dict(holdings or {}), False, "Quantité invalide"

    new_holdings = dict(holdings or {})
    current_qty = float(new_holdings.get(sym, 0.0) or 0.0)

    if current_qty < qty:
        msg = f"Quantité insuffisante pour vendre {qty} {sym}. Vous possédez seulement {current_qty}."
        print(f"[portfolio_service] SELL failed: {msg}")
        return new_holdings, False, msg

    remaining = current_qty - qty
    if remaining <= 0:
        new_holdings.pop(sym, None)
    else:
        new_holdings[sym] = round(remaining, 8)

    print(f"[portfolio_service] SELL holdings {sym}: {current_qty} - {qty} => {new_holdings.get(sym, 0.0)}")
    return new_holdings, True, "OK"


def update_portfolio_totals(
    portfolio_id: str,
    transaction_type: Any,
    total_usd: float,
    portfolios_collection,
) -> bool:
    """Update portfolio totals (invested/value/P&L) in MongoDB.

    Args:
        portfolio_id: Portfolio identifier (can be Mongo _id or portfolio_id field).
        transaction_type: TransactionType enum or string (BUY/SELL).
        total_usd: Total amount of the transaction.
        portfolios_collection: MongoDB collection for portfolios.

    Returns:
        True if update succeeded, False otherwise.

    Notes:
        - For BUY: total_invested_usd += total_usd
        - For SELL: total_invested_usd -= total_usd (floored at 0)
        - total_value_usd recalculated from holdings using prices collection.
        - profit_loss fields recalculated.
        - updated_at set to datetime.utcnow().
        - Includes debug prints.
    """

    try:
        amount = float(total_usd)
    except Exception:
        print(f"[portfolio_service] ⚠️ update_portfolio_totals invalid total_usd={total_usd}")
        return False

    tx = getattr(transaction_type, "value", transaction_type)
    tx_str = str(tx).upper().strip()

    query: dict[str, Any]
    try:
        query = {"_id": ObjectId(portfolio_id)}
    except Exception:
        query = {"portfolio_id": portfolio_id}

    portfolio = portfolios_collection.find_one(query)
    if not portfolio:
        print(f"[portfolio_service] ⚠️ update_portfolio_totals portfolio not found for {portfolio_id}")
        return False

    current_invested = float(portfolio.get("total_invested_usd", 0.0) or 0.0)

    if tx_str == "BUY":
        new_invested = current_invested + amount
    elif tx_str == "SELL":
        new_invested = max(0.0, current_invested - amount)
    else:
        print(f"[portfolio_service] ⚠️ update_portfolio_totals unknown transaction_type={transaction_type}")
        return False

    holdings = portfolio.get("holdings") or {}

    # Get prices collection from the same database.
    prices_collection = portfolios_collection.database.get_collection("prices")
    total_value = calculate_portfolio_value(holdings, prices_collection)
    pl_usd, pl_pct = calculate_profit_loss(total_value_usd=total_value, total_invested_usd=new_invested)
    now = datetime.utcnow()

    update_doc = {
        "$set": {
            "total_invested_usd": round(new_invested, 2),
            "total_value_usd": round(total_value, 2),
            "profit_loss_usd": round(pl_usd, 2),
            "profit_loss_percent": round(pl_pct, 2),
            "updated_at": now,
        }
    }

    result = portfolios_collection.update_one({"_id": portfolio["_id"]}, update_doc)
    ok = bool(result.matched_count == 1)
    print(f"[portfolio_service] update_portfolio_totals portfolio={portfolio_id} tx={tx_str} amount={amount} ok={ok}")
    return ok


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
        pl, pl_pct = calculate_profit_loss(total_value_usd=current_value, total_invested_usd=total_invested)

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
        pl, pl_pct = calculate_profit_loss(total_value_usd=current_value, total_invested_usd=new_total_invested)

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
        pl, pl_pct = calculate_profit_loss(total_value_usd=current_value, total_invested_usd=total_invested)

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
        pl, pl_pct = calculate_profit_loss(total_value_usd=current_value, total_invested_usd=new_total_invested)

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
