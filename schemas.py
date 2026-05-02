from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

class AccountCreate(BaseModel):
    account_number: int
    password: str = Field(min_length=6)
    email: EmailStr

class LoginRequest(BaseModel):
    account_number: int
    password: str

class TransactionRequest(BaseModel):
    account_number: int
    amount: Decimal = Field(gt=0, decimal_places=2)

class TransferRequest(BaseModel):
    from_acc: int
    to_acc: int
    amount: Decimal = Field(gt=0, decimal_places=2)

class Token(BaseModel):
    access_token: str
    token_type: str

class HistoryItem(BaseModel):
    type: str
    amount: Decimal
    related_acc: Optional[int]
    balance_after: Decimal
    timestamp: datetime