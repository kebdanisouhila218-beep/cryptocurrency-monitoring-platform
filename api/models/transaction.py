from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Transaction(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid4()))
    portfolio_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    transaction_type: TransactionType
    crypto_symbol: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    price_usd: float = Field(..., gt=0)
    total_usd: float = Field(0.0, ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

    @field_validator("portfolio_id", "user_id")
    @classmethod
    def strip_id(cls, v: str) -> str:
        vv = v.strip()
        if not vv:
            raise ValueError("id must not be empty")
        return vv

    @field_validator("crypto_symbol")
    @classmethod
    def crypto_symbol_upper(cls, v: str) -> str:
        vv = v.strip().upper()
        if not vv:
            raise ValueError("crypto_symbol must not be empty")
        return vv

    @field_validator("notes")
    @classmethod
    def notes_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        vv = v.strip()
        return vv if vv else None

    @model_validator(mode="before")
    @classmethod
    def compute_total_usd(cls, values: Any) -> Any:
        if isinstance(values, dict):
            qty = values.get("quantity")
            price = values.get("price_usd")
            total = values.get("total_usd")

            if total in (None, 0, 0.0) and qty is not None and price is not None:
                try:
                    values["total_usd"] = float(qty) * float(price)
                except Exception:
                    pass
        return values


class TransactionCreate(BaseModel):
    portfolio_id: Optional[str] = None
    transaction_type: TransactionType
    crypto_symbol: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    price_usd: float = Field(..., gt=0)
    notes: Optional[str] = None

    @field_validator("portfolio_id")
    @classmethod
    def strip_portfolio_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        vv = v.strip()
        return vv if vv else None

    @field_validator("crypto_symbol")
    @classmethod
    def crypto_symbol_uppercase(cls, v: str) -> str:
        vv = v.strip().upper()
        if not vv:
            raise ValueError("crypto_symbol must not be empty")
        return vv

    @field_validator("notes")
    @classmethod
    def notes_strip_create(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        vv = v.strip()
        return vv if vv else None


class TransactionResponse(Transaction):
    pass


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    count: int
