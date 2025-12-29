from datetime import datetime, timedelta
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import MongoClient
import os

from auth import get_current_active_user
from database import get_collection
from models.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioListResponse
from models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionType,
)
from services.portfolio_service import (
    calculate_portfolio_value,
    calculate_profit_loss,
    update_holdings_after_buy,
    update_holdings_after_sell,
    update_portfolio_totals,
)


router = APIRouter(prefix="/virtual-portfolio", tags=["Portfolio Virtuel"])


MONGO_URI = os.getenv("MONGO_URI") or f"mongodb://{os.getenv('MONGO_HOST', '127.0.0.1')}:{os.getenv('MONGO_PORT', '27017')}/"
DB_NAME = "crypto_db"


def get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME]


@router.get("/available-cryptos", tags=["Portfolio Virtuel"])
async def get_available_cryptos(
    current_user: dict = Depends(get_current_active_user),
    prices_collection=Depends(get_collection),
):
    try:
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": "$symbol",
                    "symbol": {"$first": "$symbol"},
                    "name": {"$first": "$name"},
                    "price_usd": {"$first": "$price_usd"},
                    "coin_id": {"$first": "$coin_id"},
                }
            },
            {"$sort": {"symbol": 1}},
            {
                "$project": {
                    "_id": 0,
                    "symbol": 1,
                    "name": 1,
                    "price_usd": 1,
                    "coin_id": 1,
                }
            },
        ]

        cryptos = list(prices_collection.aggregate(pipeline))
        return {"success": True, "cryptos": cryptos, "count": len(cryptos)}
    except Exception as e:
        print(f"[VIRTUAL-PORTFOLIO] Erreur récupération cryptos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des cryptos: {str(e)}",
        )


@router.get("/crypto-price/{symbol}", tags=["Portfolio Virtuel"])
async def get_crypto_current_price(
    symbol: str,
    current_user: dict = Depends(get_current_active_user),
    prices_collection=Depends(get_collection),
):
    try:
        latest = prices_collection.find_one(
            {"symbol": symbol.upper()},
            sort=[("timestamp", -1)],
        )

        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crypto {symbol} non trouvée",
            )

        return {
            "success": True,
            "symbol": latest.get("symbol"),
            "name": latest.get("name", "N/A"),
            "price_usd": latest.get("price_usd"),
            "timestamp": latest.get("timestamp"),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[VIRTUAL-PORTFOLIO] Erreur récupération prix {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du prix: {str(e)}",
        )


@router.get("/stats/global", tags=["Portfolio Virtuel - Stats"])
async def get_global_stats(current_user: dict = Depends(get_current_active_user)):
    try:
        db = get_db()
        portfolios_collection = db["virtual_portfolios"]
        transactions_collection = db["virtual_transactions"]

        user_id = str(current_user["_id"])
        portfolios = list(portfolios_collection.find({"user_id": user_id}))

        if not portfolios:
            return {
                "success": True,
                "stats": {
                    "total_portfolios": 0,
                    "total_invested": 0,
                    "total_current_value": 0,
                    "total_profit_loss": 0,
                    "total_profit_loss_percent": 0,
                    "best_portfolio": None,
                    "worst_portfolio": None,
                    "total_transactions": 0,
                },
            }

        total_invested = 0.0
        total_current_value = 0.0
        best_portfolio = None
        worst_portfolio = None
        best_profit_percent = float("-inf")
        worst_profit_percent = 0

        for portfolio in portfolios:
            invested = float(portfolio.get("total_invested_usd", 0) or 0)
            current_value = float(portfolio.get("total_value_usd", 0) or 0)
            profit_loss_percent = float(portfolio.get("profit_loss_percent", 0) or 0)

            total_invested += invested
            total_current_value += current_value

            if profit_loss_percent > best_profit_percent:
                best_profit_percent = profit_loss_percent
                best_portfolio = {
                    "id": portfolio.get("portfolio_id", str(portfolio.get("_id"))),
                    "name": portfolio.get("name", "N/A"),
                    "profit_loss_percent": round(profit_loss_percent, 2),
                }

            if profit_loss_percent < 0 and profit_loss_percent < worst_profit_percent:
                worst_profit_percent = profit_loss_percent
                worst_portfolio = {
                    "id": portfolio.get("portfolio_id", str(portfolio.get("_id"))),
                    "name": portfolio.get("name", "N/A"),
                    "profit_loss_percent": round(profit_loss_percent, 2),
                }

        total_profit_loss = total_current_value - total_invested
        total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0.0
        total_transactions = int(transactions_collection.count_documents({"user_id": user_id}))

        return {
            "success": True,
            "stats": {
                "total_portfolios": len(portfolios),
                "total_invested": round(total_invested, 2),
                "total_current_value": round(total_current_value, 2),
                "total_profit_loss": round(total_profit_loss, 2),
                "total_profit_loss_percent": round(total_profit_loss_percent, 2),
                "best_portfolio": best_portfolio,
                "worst_portfolio": worst_portfolio,
                "total_transactions": total_transactions,
            },
        }
    except Exception as e:
        print(f"[VIRTUAL-PORTFOLIO] Erreur stats globales: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}",
        )


@router.get("/performance/history", tags=["Portfolio Virtuel - Stats"])
async def get_performance_history(days: int = 30, current_user: dict = Depends(get_current_active_user)):
    try:
        safe_days = int(days)
        if safe_days < 1:
            safe_days = 1
        if safe_days > 365:
            safe_days = 365

        db = get_db()
        portfolios_collection = db["virtual_portfolios"]
        user_id = str(current_user["_id"])
        portfolios = list(portfolios_collection.find({"user_id": user_id}))

        if not portfolios:
            return {"success": True, "history": [], "days": safe_days}

        current_total_value = sum(float(p.get("total_value_usd", 0) or 0) for p in portfolios)
        current_total_invested = sum(float(p.get("total_invested_usd", 0) or 0) for p in portfolios)

        history = []
        for i in range(safe_days, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            variation = (safe_days - i) / safe_days if safe_days > 0 else 1
            value = current_total_invested + ((current_total_value - current_total_invested) * variation)
            history.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "value": round(float(value), 2),
                    "invested": round(float(current_total_invested), 2),
                    "profit_loss": round(float(value) - float(current_total_invested), 2),
                }
            )

        return {"success": True, "history": history, "days": safe_days}
    except Exception as e:
        print(f"[VIRTUAL-PORTFOLIO] Erreur historique: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'historique: {str(e)}",
        )


@router.get("/performance/by-crypto", tags=["Portfolio Virtuel - Stats"])
async def get_performance_by_crypto(
    current_user: dict = Depends(get_current_active_user),
    prices_collection=Depends(get_collection),
):
    try:
        db = get_db()
        portfolios_collection = db["virtual_portfolios"]
        transactions_collection = db["virtual_transactions"]

        user_id = str(current_user["_id"])
        portfolios = list(portfolios_collection.find({"user_id": user_id}))

        if not portfolios:
            return {"success": True, "cryptos": [], "count": 0}

        total_holdings: dict[str, float] = {}
        for portfolio in portfolios:
            holdings = portfolio.get("holdings", {}) or {}
            for symbol, quantity in holdings.items():
                sym = str(symbol).upper().strip()
                if not sym:
                    continue
                try:
                    qty = float(quantity)
                except Exception:
                    continue
                total_holdings[sym] = total_holdings.get(sym, 0.0) + qty

        cryptos_performance = []
        for symbol, quantity in total_holdings.items():
            if quantity <= 0:
                continue

            latest_price = prices_collection.find_one({"symbol": symbol}, sort=[("timestamp", -1)])
            if not latest_price:
                continue

            current_price = float(latest_price.get("price_usd", 0) or 0)
            current_value = float(quantity) * current_price

            total_bought_cost = 0.0
            total_bought_qty = 0.0
            cursor = transactions_collection.find(
                {"user_id": user_id, "crypto_symbol": symbol, "transaction_type": "BUY"},
                {"quantity": 1, "price_usd": 1},
            )
            for tx in cursor:
                try:
                    qty = float(tx.get("quantity", 0) or 0)
                    price = float(tx.get("price_usd", 0) or 0)
                except Exception:
                    continue
                if qty <= 0 or price <= 0:
                    continue
                total_bought_cost += qty * price
                total_bought_qty += qty

            avg_buy_price = (total_bought_cost / total_bought_qty) if total_bought_qty > 0 else 0.0
            cost_basis = avg_buy_price * float(quantity)
            profit_loss = current_value - cost_basis
            profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0.0

            cryptos_performance.append(
                {
                    "symbol": symbol,
                    "name": latest_price.get("name", "N/A"),
                    "quantity": round(float(quantity), 8),
                    "avg_buy_price": round(float(avg_buy_price), 2),
                    "current_price": round(float(current_price), 2),
                    "current_value": round(float(current_value), 2),
                    "total_cost": round(float(cost_basis), 2),
                    "profit_loss": round(float(profit_loss), 2),
                    "profit_loss_percent": round(float(profit_loss_percent), 2),
                }
            )

        cryptos_performance.sort(key=lambda x: x.get("profit_loss", 0), reverse=True)
        return {"success": True, "cryptos": cryptos_performance, "count": len(cryptos_performance)}
    except Exception as e:
        print(f"[VIRTUAL-PORTFOLIO] Erreur performance par crypto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des performances: {str(e)}",
        )


def convert_utc_to_local(dt: datetime) -> Optional[datetime]:
    if dt is None:
        return None
    return dt + timedelta(hours=1)


def portfolio_to_response(portfolio: dict) -> Portfolio:
    return Portfolio(
        portfolio_id=portfolio.get("portfolio_id", str(portfolio["_id"])),
        user_id=portfolio["user_id"],
        name=portfolio["name"],
        total_value_usd=float(portfolio.get("total_value_usd", 0.0)),
        total_invested_usd=float(portfolio.get("total_invested_usd", 0.0)),
        profit_loss_usd=float(portfolio.get("profit_loss_usd", 0.0)),
        profit_loss_percent=float(portfolio.get("profit_loss_percent", 0.0)),
        holdings=portfolio.get("holdings", {}) or {},
        created_at=convert_utc_to_local(portfolio.get("created_at")),
        updated_at=convert_utc_to_local(portfolio.get("updated_at")),
    )


def transaction_to_response(tx: dict) -> TransactionResponse:
    return TransactionResponse(
        transaction_id=tx.get("transaction_id", str(tx["_id"])),
        portfolio_id=tx["portfolio_id"],
        user_id=tx["user_id"],
        transaction_type=TransactionType(tx["transaction_type"]),
        crypto_symbol=tx["crypto_symbol"],
        quantity=float(tx["quantity"]),
        price_usd=float(tx["price_usd"]),
        total_usd=float(tx.get("total_usd", float(tx["quantity"]) * float(tx["price_usd"]))),
        timestamp=convert_utc_to_local(tx.get("timestamp")),
        notes=tx.get("notes"),
    )


def _find_virtual_portfolio_or_404(portfolios_collection, portfolio_id: str) -> dict:
    try:
        obj_id = ObjectId(portfolio_id)
        doc = portfolios_collection.find_one({"_id": obj_id})
        if doc:
            return doc
    except InvalidId:
        pass

    doc = portfolios_collection.find_one({"portfolio_id": portfolio_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio non trouvé")
    return doc


def _ensure_owner(portfolio: dict, user_id: str) -> None:
    if portfolio.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé à ce portfolio")


@router.post("", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
def create_virtual_portfolio(
    payload: PortfolioCreate,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    portfolios_collection = db["virtual_portfolios"]

    user_id = str(current_user["_id"])
    print(f"[VIRTUAL-PORTFOLIO] Création portfolio pour user: {user_id}")

    now = datetime.utcnow()
    portfolio_model = Portfolio(user_id=user_id, name=payload.name)

    doc = {
        "portfolio_id": portfolio_model.portfolio_id,
        "user_id": user_id,
        "name": portfolio_model.name,
        "total_value_usd": 0.0,
        "total_invested_usd": 0.0,
        "profit_loss_usd": 0.0,
        "profit_loss_percent": 0.0,
        "holdings": {},
        "created_at": now,
        "updated_at": now,
    }

    portfolios_collection.insert_one(doc)
    created = portfolios_collection.find_one({"portfolio_id": doc["portfolio_id"]})
    return portfolio_to_response(created)


@router.get("", response_model=PortfolioListResponse)
def list_virtual_portfolios(current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    portfolios_collection = db["virtual_portfolios"]

    user_id = str(current_user["_id"])
    print(f"[VIRTUAL-PORTFOLIO] Liste portfolios user: {user_id}")

    docs = list(portfolios_collection.find({"user_id": user_id}).sort("created_at", -1))
    items = [portfolio_to_response(p) for p in docs]
    return {"portfolios": items, "count": len(items)}


@router.get("/{portfolio_id}", response_model=Portfolio)
def get_virtual_portfolio(portfolio_id: str, current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    portfolios_collection = db["virtual_portfolios"]

    user_id = str(current_user["_id"])
    portfolio = _find_virtual_portfolio_or_404(portfolios_collection, portfolio_id)
    _ensure_owner(portfolio, user_id)

    return portfolio_to_response(portfolio)


@router.put("/{portfolio_id}", response_model=Portfolio)
def update_virtual_portfolio(
    portfolio_id: str,
    payload: PortfolioUpdate,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    portfolios_collection = db["virtual_portfolios"]

    user_id = str(current_user["_id"])
    portfolio = _find_virtual_portfolio_or_404(portfolios_collection, portfolio_id)
    _ensure_owner(portfolio, user_id)

    update_fields = {"updated_at": datetime.utcnow()}
    if payload.name is not None:
        update_fields["name"] = payload.name.strip()

    portfolios_collection.update_one({"_id": portfolio["_id"]}, {"$set": update_fields})
    updated = portfolios_collection.find_one({"_id": portfolio["_id"]})
    return portfolio_to_response(updated)


@router.delete("/{portfolio_id}")
def delete_virtual_portfolio(portfolio_id: str, current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    portfolios_collection = db["virtual_portfolios"]
    transactions_collection = db["virtual_transactions"]

    user_id = str(current_user["_id"])
    portfolio = _find_virtual_portfolio_or_404(portfolios_collection, portfolio_id)
    _ensure_owner(portfolio, user_id)

    print(f"[VIRTUAL-PORTFOLIO] Suppression portfolio {portfolio.get('portfolio_id')} user={user_id}")

    transactions_collection.delete_many({"portfolio_id": portfolio.get("portfolio_id", str(portfolio["_id"]))})
    portfolios_collection.delete_one({"_id": portfolio["_id"]})

    return {"message": "Portfolio virtuel supprimé avec succès", "deleted": True}


@router.post("/{portfolio_id}/transaction", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_virtual_transaction(
    portfolio_id: str,
    payload: TransactionCreate,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    portfolios_collection = db["virtual_portfolios"]
    transactions_collection = db["virtual_transactions"]

    user_id = str(current_user["_id"])
    portfolio = _find_virtual_portfolio_or_404(portfolios_collection, portfolio_id)
    _ensure_owner(portfolio, user_id)

    sym = payload.crypto_symbol.upper().strip()
    qty = float(payload.quantity)
    price = float(payload.price_usd)
    tx_type = payload.transaction_type

    print(f"[VIRTUAL-PORTFOLIO] Transaction {tx_type} - {sym}: {qty} @ ${price}")

    holdings = portfolio.get("holdings", {}) or {}

    if tx_type == TransactionType.BUY:
        new_holdings = update_holdings_after_buy(holdings, sym, qty)
        portfolios_collection.update_one(
            {"_id": portfolio["_id"]},
            {"$set": {"holdings": new_holdings, "updated_at": datetime.utcnow()}},
        )
    elif tx_type == TransactionType.SELL:
        new_holdings, ok, msg = update_holdings_after_sell(holdings, sym, qty)
        if not ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        portfolios_collection.update_one(
            {"_id": portfolio["_id"]},
            {"$set": {"holdings": new_holdings, "updated_at": datetime.utcnow()}},
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Type de transaction invalide")

    tx_model = Transaction(
        portfolio_id=portfolio.get("portfolio_id", str(portfolio["_id"])),
        user_id=user_id,
        transaction_type=tx_type,
        crypto_symbol=sym,
        quantity=qty,
        price_usd=price,
        notes=payload.notes,
    )

    tx_doc = tx_model.dict()
    tx_doc["timestamp"] = datetime.utcnow()

    transactions_collection.insert_one(tx_doc)

    update_portfolio_totals(
        portfolio_id=portfolio.get("portfolio_id", str(portfolio["_id"])),
        transaction_type=tx_type,
        total_usd=float(tx_doc.get("total_usd", qty * price)),
        portfolios_collection=portfolios_collection,
    )

    saved = transactions_collection.find_one({"transaction_id": tx_doc["transaction_id"]})
    return transaction_to_response(saved)


@router.get("/{portfolio_id}/transactions", response_model=TransactionListResponse)
def list_virtual_transactions(
    portfolio_id: str,
    transaction_type: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
):
    db = get_db()
    portfolios_collection = db["virtual_portfolios"]
    transactions_collection = db["virtual_transactions"]

    user_id = str(current_user["_id"])
    portfolio = _find_virtual_portfolio_or_404(portfolios_collection, portfolio_id)
    _ensure_owner(portfolio, user_id)

    query = {"portfolio_id": portfolio.get("portfolio_id", str(portfolio["_id"]))}
    if transaction_type:
        query["transaction_type"] = str(transaction_type).upper().strip()

    docs = list(transactions_collection.find(query).sort("timestamp", -1))
    txs = [transaction_to_response(d) for d in docs]
    return {"transactions": txs, "count": len(txs)}


@router.get("/{portfolio_id}/performance", response_model=Portfolio)
def get_virtual_performance(portfolio_id: str, current_user: dict = Depends(get_current_active_user)):
    db = get_db()
    portfolios_collection = db["virtual_portfolios"]
    prices_collection = db["prices"]

    user_id = str(current_user["_id"])
    portfolio = _find_virtual_portfolio_or_404(portfolios_collection, portfolio_id)
    _ensure_owner(portfolio, user_id)

    holdings = portfolio.get("holdings", {}) or {}
    total_value = calculate_portfolio_value(holdings, prices_collection)
    invested = float(portfolio.get("total_invested_usd", 0.0) or 0.0)
    pl_usd, pl_pct = calculate_profit_loss(total_value_usd=total_value, total_invested_usd=invested)

    now = datetime.utcnow()
    portfolios_collection.update_one(
        {"_id": portfolio["_id"]},
        {
            "$set": {
                "total_value_usd": round(total_value, 2),
                "profit_loss_usd": round(pl_usd, 2),
                "profit_loss_percent": round(pl_pct, 2),
                "updated_at": now,
            }
        },
    )

    updated = portfolios_collection.find_one({"_id": portfolio["_id"]})
    return portfolio_to_response(updated)
