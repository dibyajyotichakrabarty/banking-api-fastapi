from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Account, Transaction
from auth import get_current_user

router = APIRouter(tags=["L6 - Banking"])

class TransferRequest(BaseModel):
    to_account: str
    amount: float

class DepositRequest(BaseModel):
    amount: float

class BalanceResponse(BaseModel):
    account_number: str
    balance: float

@router.post("/transfer", status_code=200)
def transfer_money(
    transfer_data: TransferRequest,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if transfer_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if current_user.account_number == transfer_data.to_account:
        raise HTTPException(status_code=400, detail="Cannot transfer to same account")
    if current_user.balance < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    receiver = db.query(Account).filter(Account.account_number == transfer_data.to_account).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver account not found")
    
    current_user.balance -= transfer_data.amount
    receiver.balance += transfer_data.amount
    
    new_transaction = Transaction(
        from_account=current_user.account_number,
        to_account=transfer_data.to_account,
        amount=transfer_data.amount,
        type="transfer"
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Transfer successful",
        "from": current_user.account_number,
        "to": transfer_data.to_account,
        "amount": transfer_data.amount,
        "remaining_balance": current_user.balance
    }

@router.post("/deposit")
def deposit_money(
    deposit_data: DepositRequest,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if deposit_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    current_user.balance += deposit_data.amount
    
    new_transaction = Transaction(
        from_account="BANK",
        to_account=current_user.account_number,
        amount=deposit_data.amount,
        type="deposit"
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Deposit successful", "new_balance": current_user.balance}

@router.get("/balance", response_model=BalanceResponse)
def check_balance(current_user: Account = Depends(get_current_user)):
    return {
        "account_number": current_user.account_number,
        "balance": current_user.balance
    }

def create_bank_routes(app):
    app.include_router(router)