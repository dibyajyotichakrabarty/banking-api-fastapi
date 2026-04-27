from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from models import AccountCreate, TransactionRequest, TransferRequest, Token, HistoryItem
from bank import BankService
from auth import create_access_token, get_current_user
from typing import List

app = FastAPI(title="Bank API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_bank_service():
    return BankService()

@app.post("/create-account", status_code=201)
def create_account(data: AccountCreate, bank: BankService = Depends(get_bank_service)):
    try:
        return bank.create_account(data.account_number, data.password, data.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), bank: BankService = Depends(get_bank_service)):
    try:
        bank.login(int(form_data.username), form_data.password)
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/deposit")
def deposit(data: TransactionRequest, current_user: int = Depends(get_current_user), bank: BankService = Depends(get_bank_service)):
    if current_user!= data.account_number:
        raise HTTPException(status_code=403, detail="Not authorized for this account")
    try:
        return bank.deposit(data.account_number, data.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/withdraw")
def withdraw(data: TransactionRequest, current_user: int = Depends(get_current_user), bank: BankService = Depends(get_bank_service)):
    if current_user!= data.account_number:
        raise HTTPException(status_code=403, detail="Not authorized for this account")
    try:
        return bank.withdraw(data.account_number, data.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transfer")
def transfer(data: TransferRequest, current_user: int = Depends(get_current_user), bank: BankService = Depends(get_bank_service)):
    if current_user!= data.from_acc:
        raise HTTPException(status_code=403, detail="Not authorized for this account")
    try:
        return bank.transfer(data.from_acc, data.to_acc, data.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/balance/{acc_no}")
def balance(acc_no: int, current_user: int = Depends(get_current_user), bank: BankService = Depends(get_bank_service)):
    if current_user!= acc_no:
        raise HTTPException(status_code=403, detail="Not authorized for this account")
    try:
        bal = bank.get_balance(acc_no)
        return {"account_number": acc_no, "balance": bal}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/history/{acc_no}", response_model=List[HistoryItem])
def history(acc_no: int, current_user: int = Depends(get_current_user), bank: BankService = Depends(get_bank_service)):
    if current_user!= acc_no:
        raise HTTPException(status_code=403, detail="Not authorized for this account")
    return bank.show_history(acc_no)