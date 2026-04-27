# Banking API - FastAPI + MySQL

Full-stack banking system with JWT authentication + ACID transactions + Docker.

### **Features**
- **JWT Authentication**: Secure login/register with bcrypt password hashing
- **ACID Transactions**: MySQL `SELECT ... FOR UPDATE` prevents double-spend
- **Concurrency Safe**: Handles 100+ simultaneous transfers without race conditions  
- **RESTful API**: 8+ endpoints for accounts, transfers, transaction history
- **Docker Ready**: Fully containerized

### **Tech Stack**
Python, FastAPI, SQLAlchemy, JWT, MySQL, Docker

### **Key Technical Fix**
Solved race conditions using MySQL row-level locking to ensure data integrity under high load.

### **Run Locally**
```bash
git clone https://github.com/dibyajyotichakrabarty/banking-api-fastapi.git
cd banking-api-fastapi
pip install -r requirements.txt
uvicorn main:app --reload
