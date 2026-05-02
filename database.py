from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Tera actual MySQL connection string
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:pritam01@localhost/banking_db"

# Engine - connection pool manager
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # True kar de agar SQL queries terminal me dekhni hain
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# FastAPI Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()