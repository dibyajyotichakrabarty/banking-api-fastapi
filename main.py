from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.database import engine, get_db   # ✅ FIXED (added get_db)
from models import Base, Account, Transaction
from auth import get_current_user, get_current_admin_user, SECRET_KEY, ALGORITHM
from bank import create_bank_routes

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Banking API", version="L9")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------- SCHEMAS -------------------
class SignupRequest(BaseModel):
    username: str
    password: str
    account_number: str
    initial_balance: float = 0.0

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    account_number: str
    balance: float
    role: str

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    id: int
    from_account: str
    to_account: str
    amount: float
    type: str
    timestamp: datetime

    class Config:
        from_attributes = True


class AdminUserResponse(BaseModel):
    id: int
    username: str
    account_number: str
    balance: float
    role: str

    class Config:
        from_attributes = True


class AdminStatsResponse(BaseModel):
    total_users: int
    total_transactions: int
    total_money_in_system: float


# ------------------- UTILS -------------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# ------------------- L1: ROOT -------------------
@app.get("/", tags=["L1 - Root"])
def read_root():
    return {"message": "Welcome to Mini Banking API L9"}


# ------------------- L2: SIGNUP -------------------
@app.post("/signup", status_code=201, tags=["L2 - Auth"])
def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    if db.query(Account).filter(Account.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if db.query(Account).filter(Account.account_number == user_data.account_number).first():
        raise HTTPException(status_code=400, detail="Account number already exists")

    hashed_pw = get_password_hash(user_data.password)

    new_user = Account(
        username=user_data.username,
        hashed_password=hashed_pw,
        account_number=user_data.account_number,
        balance=user_data.initial_balance,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "username": new_user.username}


# ------------------- L3: LOGIN -------------------
@app.post("/login", response_model=TokenResponse, tags=["L3 - Auth"])
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Account).filter(Account.username == login_data.username).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


# ------------------- L5: CURRENT USER -------------------
@app.get("/users/me", response_model=UserResponse, tags=["L5 - Auth"])
def read_users_me(current_user: Account = Depends(get_current_user)):
    return current_user


# ------------------- L8: TRANSACTIONS -------------------
@app.get("/transactions", response_model=List[TransactionResponse], tags=["L8 - Transactions"])
def get_user_transactions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).filter(
        (Transaction.from_account == current_user.account_number) |
        (Transaction.to_account == current_user.account_number)
    ).order_by(Transaction.timestamp.desc()).offset(offset).limit(limit).all()

    return transactions


# ------------------- L9: ADMIN PANEL -------------------
@app.get("/admin/users", response_model=List[AdminUserResponse], tags=["L9 - Admin"])
def get_all_users(
    admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    return db.query(Account).all()


@app.get("/admin/transactions", response_model=List[TransactionResponse], tags=["L9 - Admin"])
def get_all_transactions(
    limit: int = Query(50, ge=1, le=200),
    admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    return db.query(Transaction).order_by(Transaction.timestamp.desc()).limit(limit).all()


@app.get("/admin/stats", response_model=AdminStatsResponse, tags=["L9 - Admin"])
def get_system_stats(
    admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    total_users = db.query(Account).count()
    total_transactions = db.query(Transaction).count()
    total_money = db.query(func.sum(Account.balance)).scalar() or 0.0

    return {
        "total_users": total_users,
        "total_transactions": total_transactions,
        "total_money_in_system": total_money
    }


# ------------------- L6: BANKING ROUTES -------------------
create_bank_routes(app)
