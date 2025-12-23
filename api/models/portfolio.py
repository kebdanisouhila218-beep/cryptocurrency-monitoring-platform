from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


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
