from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Portfolio(BaseModel):
    portfolio_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    total_value_usd: float = Field(0.0, ge=0)
    total_invested_usd: float = Field(0.0, ge=0)
    profit_loss_usd: float = 0.0
    profit_loss_percent: float = 0.0
    holdings: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("name")
    def validate_portfolio_name(cls, v: str) -> str:
        vv = v.strip()
        if not vv:
            raise ValueError("name must not be empty")
        return vv

    @validator("holdings")
    def validate_holdings(cls, v: Dict[str, float]) -> Dict[str, float]:
        cleaned: Dict[str, float] = {}
        for k, qty in (v or {}).items():
            if k is None:
                continue
            symbol = str(k).upper().strip()
            if not symbol:
                continue
            q = float(qty)
            if q < 0:
                raise ValueError("holdings quantities must be >= 0")
            cleaned[symbol] = q
        return cleaned


class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1)
    initial_balance: float = Field(10000.0, gt=0)
    is_default: bool = False

    @validator("name")
    def validate_name(cls, v: str) -> str:
        return v.strip()


class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    is_default: Optional[bool] = None

    @validator("name")
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip()


class PortfolioResponse(BaseModel):
    id: str
    user_id: str
    name: str
    initial_balance: float
    current_balance: float
    created_at: datetime
    updated_at: datetime
    is_default: bool


class PositionResponse(BaseModel):
    id: str
    portfolio_id: str
    crypto_symbol: str
    quantity: float
    average_buy_price: float
    current_price: float
    total_invested: float
    current_value: float
    profit_loss: float
    profit_loss_percent: float
    updated_at: datetime


class TransactionResponse(BaseModel):
    id: str
    portfolio_id: str
    transaction_type: TransactionType
    crypto_symbol: str
    quantity: float
    price: float
    total_amount: float
    fee: float
    timestamp: datetime
    notes: Optional[str] = None


class TradeRequest(BaseModel):
    crypto_symbol: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)
    fee_percent: float = Field(0.0, ge=0)
    notes: Optional[str] = None

    @validator("crypto_symbol")
    def crypto_symbol_uppercase(cls, v: str) -> str:
        return v.upper().strip()

    @validator("notes")
    def notes_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        vv = v.strip()
        return vv if vv else None


class PortfolioStatsResponse(BaseModel):
    total_value: float
    cash_balance: float
    positions_value: float
    total_invested: float
    profit_loss: float
    profit_loss_percent: float
    roi_percent: float
    positions_count: int
    transactions_count: int


class AllocationItem(BaseModel):
    crypto_symbol: str
    current_value: float
    percent: float


class PortfolioAllocationResponse(BaseModel):
    total_value: float
    allocation: list[AllocationItem]


class PerformancePoint(BaseModel):
    timestamp: datetime
    total_value: float
    cash_balance: float
    positions_value: float


class PortfolioPerformanceResponse(BaseModel):
    points: list[PerformancePoint]
    count: int
