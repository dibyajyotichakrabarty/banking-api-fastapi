from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    account_number = Column(String(20), unique=True, index=True)
    balance = Column(Float, default=0.0)
    role = Column(String(20), default="user") # L9: admin/user

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    from_account = Column(String(20), index=True)
    to_account = Column(String(20), index=True)
    amount = Column(Float)
    type = Column(String(20), default="transfer")
    timestamp = Column(DateTime, default=datetime.utcnow)