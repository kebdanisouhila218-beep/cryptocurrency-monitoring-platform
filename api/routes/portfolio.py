from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_current_active_user
from database import (
    get_collection,
    get_portfolios_collection,
    get_positions_collection,
    get_transactions_collection,
)
from models.portfolio import (
    AllocationItem,
    PortfolioAllocationResponse,
    PortfolioCreate,
    PortfolioPerformanceResponse,
    PortfolioResponse,
    PortfolioStatsResponse,
    PortfolioUpdate,
    PositionResponse,
    TransactionResponse,
    TradeRequest,
    PerformancePoint,
    TransactionType,
)
from services.portfolio_service import (
    calculate_portfolio_total_value,
    ensure_portfolio_owner,
    execute_buy,
    execute_sell,
    get_portfolio_or_404,
    update_positions_prices,
)


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


def _portfolio_to_response(portfolio: dict) -> PortfolioResponse:
    return PortfolioResponse(
        id=str(portfolio["_id"]),
        user_id=portfolio["user_id"],
        name=portfolio["name"],
        initial_balance=float(portfolio["initial_balance"]),
        current_balance=float(portfolio["current_balance"]),
        created_at=portfolio["created_at"],
        updated_at=portfolio["updated_at"],
        is_default=bool(portfolio.get("is_default", False)),
    )


def _position_to_response(pos: dict) -> PositionResponse:
    return PositionResponse(
        id=str(pos["_id"]),
        portfolio_id=pos["portfolio_id"],
        crypto_symbol=pos["crypto_symbol"],
        quantity=float(pos.get("quantity", 0.0)),
        average_buy_price=float(pos.get("average_buy_price", 0.0)),
        current_price=float(pos.get("current_price", 0.0)),
        total_invested=float(pos.get("total_invested", 0.0)),
        current_value=float(pos.get("current_value", 0.0)),
        profit_loss=float(pos.get("profit_loss", 0.0)),
        profit_loss_percent=float(pos.get("profit_loss_percent", 0.0)),
        updated_at=pos.get("updated_at"),
    )


def _transaction_to_response(tx: dict) -> TransactionResponse:
    return TransactionResponse(
        id=str(tx["_id"]),
        portfolio_id=tx["portfolio_id"],
        transaction_type=TransactionType(tx["transaction_type"]),
        crypto_symbol=tx["crypto_symbol"],
        quantity=float(tx.get("quantity", 0.0)),
        price=float(tx.get("price", 0.0)),
        total_amount=float(tx.get("total_amount", 0.0)),
        fee=float(tx.get("fee", 0.0)),
        timestamp=tx["timestamp"],
        notes=tx.get("notes"),
    )


def _set_default_portfolio_for_user(portfolios_collection, user_id: str, portfolio_id: ObjectId) -> None:
    portfolios_collection.update_many(
        {"user_id": user_id, "_id": {"$ne": portfolio_id}},
        {"$set": {"is_default": False, "updated_at": datetime.utcnow()}},
    )
    portfolios_collection.update_one(
        {"_id": portfolio_id},
        {"$set": {"is_default": True, "updated_at": datetime.utcnow()}},
    )


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    payload: PortfolioCreate,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
):
    user_id = str(current_user["_id"])
    now = datetime.utcnow()

    existing_count = portfolios_collection.count_documents({"user_id": user_id})
    is_default = bool(payload.is_default) or existing_count == 0

    doc = {
        "user_id": user_id,
        "name": payload.name,
        "initial_balance": float(payload.initial_balance),
        "current_balance": float(payload.initial_balance),
        "created_at": now,
        "updated_at": now,
        "is_default": is_default,
    }

    result = portfolios_collection.insert_one(doc)
    doc["_id"] = result.inserted_id

    if is_default:
        _set_default_portfolio_for_user(portfolios_collection, user_id, doc["_id"])
        doc["is_default"] = True

    created = portfolios_collection.find_one({"_id": doc["_id"]})
    return _portfolio_to_response(created)


@router.get("", response_model=list[PortfolioResponse])
async def list_my_portfolios(
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
):
    user_id = str(current_user["_id"])
    portfolios = list(portfolios_collection.find({"user_id": user_id}).sort("created_at", -1))
    return [_portfolio_to_response(p) for p in portfolios]


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio_details(
    portfolio_id: str,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    return _portfolio_to_response(portfolio)


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: str,
    payload: PortfolioUpdate,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aucune donnée à mettre à jour")

    now = datetime.utcnow()
    update_data["updated_at"] = now

    portfolios_collection.update_one({"_id": portfolio["_id"]}, {"$set": update_data})

    if update_data.get("is_default") is True:
        _set_default_portfolio_for_user(portfolios_collection, user_id, portfolio["_id"])

    updated = portfolios_collection.find_one({"_id": portfolio["_id"]})
    return _portfolio_to_response(updated)


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
    positions_collection=Depends(get_positions_collection),
    transactions_collection=Depends(get_transactions_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    pid = str(portfolio["_id"])

    positions_collection.delete_many({"portfolio_id": pid})
    transactions_collection.delete_many({"portfolio_id": pid})
    portfolios_collection.delete_one({"_id": portfolio["_id"]})

    remaining = list(portfolios_collection.find({"user_id": user_id}).sort("created_at", -1))
    if remaining:
        has_default = portfolios_collection.count_documents({"user_id": user_id, "is_default": True})
        if has_default == 0:
            _set_default_portfolio_for_user(portfolios_collection, user_id, remaining[0]["_id"])

    return {"message": "Portfolio supprimé avec succès", "portfolio_id": portfolio_id, "deleted": True}


@router.get("/{portfolio_id}/positions", response_model=list[PositionResponse])
async def list_positions(
    portfolio_id: str,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
    positions_collection=Depends(get_positions_collection),
    prices_collection=Depends(get_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    update_positions_prices(positions_collection, prices_collection, str(portfolio["_id"]))

    positions = list(positions_collection.find({"portfolio_id": str(portfolio["_id"]) }).sort("current_value", -1))
    return [_position_to_response(p) for p in positions]


@router.get("/{portfolio_id}/positions/{symbol}", response_model=PositionResponse)
async def get_position_details(
    portfolio_id: str,
    symbol: str,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
    positions_collection=Depends(get_positions_collection),
    prices_collection=Depends(get_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    update_positions_prices(positions_collection, prices_collection, str(portfolio["_id"]))

    sym = symbol.upper().strip()
    pos = positions_collection.find_one({"portfolio_id": str(portfolio["_id"]), "crypto_symbol": sym})
    if not pos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position non trouvée")

    return _position_to_response(pos)


@router.post("/{portfolio_id}/buy")
async def buy_crypto(
    portfolio_id: str,
    payload: TradeRequest,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
    positions_collection=Depends(get_positions_collection),
    transactions_collection=Depends(get_transactions_collection),
    prices_collection=Depends(get_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    try:
        result = execute_buy(
            portfolios_collection,
            positions_collection,
            transactions_collection,
            prices_collection,
            portfolio,
            payload.crypto_symbol,
            payload.quantity,
            payload.price,
            payload.fee_percent,
            payload.notes,
        )
        return {"message": "Achat effectué", "result": result}
    except ValueError as e:
        code = str(e)
        if code == "INSUFFICIENT_BALANCE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solde insuffisant")
        if code == "PRICE_NOT_AVAILABLE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prix non disponible")
        if code == "INVALID_QUANTITY":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantité invalide")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Achat impossible")


@router.post("/{portfolio_id}/sell")
async def sell_crypto(
    portfolio_id: str,
    payload: TradeRequest,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
    positions_collection=Depends(get_positions_collection),
    transactions_collection=Depends(get_transactions_collection),
    prices_collection=Depends(get_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    try:
        result = execute_sell(
            portfolios_collection,
            positions_collection,
            transactions_collection,
            prices_collection,
            portfolio,
            payload.crypto_symbol,
            payload.quantity,
            payload.price,
            payload.fee_percent,
            payload.notes,
        )
        return {"message": "Vente effectuée", "result": result}
    except ValueError as e:
        code = str(e)
        if code == "INSUFFICIENT_QUANTITY":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantité insuffisante")
        if code == "POSITION_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position non trouvée")
        if code == "PRICE_NOT_AVAILABLE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prix non disponible")
        if code == "INVALID_QUANTITY":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantité invalide")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vente impossible")


@router.get("/{portfolio_id}/transactions", response_model=list[TransactionResponse])
async def list_transactions(
    portfolio_id: str,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
    transactions_collection=Depends(get_transactions_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    txs = list(transactions_collection.find({"portfolio_id": str(portfolio["_id"]) }).sort("timestamp", -1))
    return [_transaction_to_response(tx) for tx in txs]


@router.get("/{portfolio_id}/stats", response_model=PortfolioStatsResponse)
async def get_portfolio_stats(
    portfolio_id: str,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
    positions_collection=Depends(get_positions_collection),
    transactions_collection=Depends(get_transactions_collection),
    prices_collection=Depends(get_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    pid = str(portfolio["_id"])
    update_positions_prices(positions_collection, prices_collection, pid)

    total_value, cash_balance, positions_value = calculate_portfolio_total_value(portfolio, positions_collection)

    positions = list(positions_collection.find({"portfolio_id": pid}, {"total_invested": 1}))
    total_invested = 0.0
    for p in positions:
        try:
            total_invested += float(p.get("total_invested", 0.0))
        except Exception:
            continue

    initial_balance = float(portfolio.get("initial_balance", 0.0))
    profit_loss = total_value - initial_balance
    profit_loss_percent = (profit_loss / initial_balance) * 100.0 if initial_balance > 0 else 0.0

    positions_count = positions_collection.count_documents({"portfolio_id": pid})
    transactions_count = transactions_collection.count_documents({"portfolio_id": pid})

    return PortfolioStatsResponse(
        total_value=total_value,
        cash_balance=cash_balance,
        positions_value=positions_value,
        total_invested=total_invested,
        profit_loss=profit_loss,
        profit_loss_percent=profit_loss_percent,
        roi_percent=profit_loss_percent,
        positions_count=positions_count,
        transactions_count=transactions_count,
    )


@router.get("/{portfolio_id}/allocation", response_model=PortfolioAllocationResponse)
async def get_portfolio_allocation(
    portfolio_id: str,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
    positions_collection=Depends(get_positions_collection),
    prices_collection=Depends(get_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    pid = str(portfolio["_id"])
    update_positions_prices(positions_collection, prices_collection, pid)

    positions = list(positions_collection.find({"portfolio_id": pid}, {"crypto_symbol": 1, "current_value": 1}))

    total_value, _, _ = calculate_portfolio_total_value(portfolio, positions_collection)
    total_value = float(total_value)

    allocation: list[AllocationItem] = []
    for p in positions:
        value = float(p.get("current_value", 0.0))
        pct = (value / total_value) * 100.0 if total_value > 0 else 0.0
        allocation.append(
            AllocationItem(
                crypto_symbol=p.get("crypto_symbol"),
                current_value=value,
                percent=pct,
            )
        )

    allocation.sort(key=lambda x: x.current_value, reverse=True)

    return PortfolioAllocationResponse(total_value=total_value, allocation=allocation)


@router.get("/{portfolio_id}/performance", response_model=PortfolioPerformanceResponse)
async def get_portfolio_performance(
    portfolio_id: str,
    current_user: dict = Depends(get_current_active_user),
    portfolios_collection=Depends(get_portfolios_collection),
    transactions_collection=Depends(get_transactions_collection),
):
    user_id = str(current_user["_id"])

    try:
        portfolio = get_portfolio_or_404(portfolios_collection, portfolio_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de portfolio invalide")
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")

    try:
        ensure_portfolio_owner(portfolio, user_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    pid = str(portfolio["_id"])
    txs = list(transactions_collection.find({"portfolio_id": pid}).sort("timestamp", 1))

    cash = float(portfolio.get("initial_balance", 0.0))
    holdings: dict[str, float] = {}
    last_price: dict[str, float] = {}

    points: list[PerformancePoint] = [
        PerformancePoint(
            timestamp=portfolio["created_at"],
            total_value=cash,
            cash_balance=cash,
            positions_value=0.0,
        )
    ]

    for tx in txs:
        symbol = str(tx.get("crypto_symbol", "")).upper().strip()
        tx_type = tx.get("transaction_type")
        qty = float(tx.get("quantity", 0.0))
        price = float(tx.get("price", 0.0))
        total_amount = float(tx.get("total_amount", qty * price))
        fee = float(tx.get("fee", 0.0))

        if symbol:
            last_price[symbol] = price

        if tx_type == "BUY":
            cash -= total_amount + fee
            holdings[symbol] = float(holdings.get(symbol, 0.0)) + qty
        elif tx_type == "SELL":
            cash += total_amount - fee
            holdings[symbol] = float(holdings.get(symbol, 0.0)) - qty
            if holdings[symbol] <= 0:
                holdings.pop(symbol, None)

        positions_value = 0.0
        for s, q in holdings.items():
            positions_value += float(q) * float(last_price.get(s, 0.0))

        points.append(
            PerformancePoint(
                timestamp=tx["timestamp"],
                total_value=float(cash + positions_value),
                cash_balance=float(cash),
                positions_value=float(positions_value),
            )
        )

    return PortfolioPerformanceResponse(points=points, count=len(points))
