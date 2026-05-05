from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SignupRequest(BaseModel):
    username: str
    password: str = Field(min_length=6)
    account_number: str
    initial_balance: float = 0.0


class LoginRequest(BaseModel):
    username: str
    password: str


class TransferRequest(BaseModel):
    to_account: str
    amount: float = Field(gt=0)


class DepositRequest(BaseModel):
    amount: float = Field(gt=0)


class Token(BaseModel):
    access_token: str
    token_type: str


class BalanceResponse(BaseModel):
    account_number: str
    balance: float


class HistoryItem(BaseModel):
    type: str
    amount: float
    related_acc: Optional[str]
    timestamp: datetime
