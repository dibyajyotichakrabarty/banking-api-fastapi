from database import get_db
import bcrypt
from decimal import Decimal
import mysql.connector

class BankService:
    def hash_password(self, pwd: str) -> str:
        return bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, pwd: str, hashed: str) -> bool:
        return bcrypt.checkpw(pwd.encode('utf-8'), hashed.encode('utf-8'))

    def log_transaction(self, cursor, acc_no, txn_type, amount, related_acc, balance_after):
        cursor.execute(
            """INSERT INTO transactions (acc_number, type, amount, related_acc, balance_after)
               VALUES (%s, %s, %s, %s, %s)""",
            (acc_no, txn_type, amount, related_acc, balance_after)
        )

    def create_account(self, acc_no: int, password: str, email: str):
        conn = get_db()
        cursor = conn.cursor()
        try:
            hashed_pwd = self.hash_password(password)
            cursor.execute(
                "INSERT INTO account (account_number, password_hash, balance, email) VALUES (%s, %s, %s, %s)",
                (acc_no, hashed_pwd, 0, email)
            )
            conn.commit()
            return {"message": "Account created", "account_number": acc_no}
        except mysql.connector.IntegrityError:
            raise ValueError("Account number already exists")
        finally:
            cursor.close()
            conn.close()

    def login(self, acc_no: int, password: str):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT password_hash FROM account WHERE account_number=%s", (acc_no,))
            result = cursor.fetchone()
            if not result or not self.verify_password(password, result['password_hash']):
                raise ValueError("Invalid credentials")
            return True
        finally:
            cursor.close()
            conn.close()

    def get_balance(self, acc_no: int) -> Decimal:
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT balance FROM account WHERE account_number = %s", (acc_no,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Account not found")
            return result[0]
        finally:
            cursor.close()
            conn.close()

    def deposit(self, acc_no: int, amount: Decimal):
        conn = get_db()
        cursor = conn.cursor()
        try:
            amount = Decimal(str(amount))
            cursor.execute("UPDATE account SET balance = balance + %s WHERE account_number = %s", (amount, acc_no))
            cursor.execute("SELECT balance FROM account WHERE account_number = %s", (acc_no,))
            new_balance = cursor.fetchone()[0]
            self.log_transaction(cursor, acc_no, 'DEPOSIT', amount, None, new_balance)
            conn.commit()
            return {"message": "Deposit successful", "new_balance": new_balance}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def withdraw(self, acc_no: int, amount: Decimal):
        conn = get_db()
        cursor = conn.cursor()
        try:
            if conn.in_transaction:
                conn.rollback()
            amount = Decimal(str(amount))
            conn.start_transaction()
            cursor.execute("SELECT balance FROM account WHERE account_number = %s FOR UPDATE", (acc_no,))
            result = cursor.fetchone()
            if not result:
                conn.rollback()
                raise ValueError("Account not found")
            current_balance = result[0]
            if current_balance < amount:
                conn.rollback()
                raise ValueError("Insufficient balance")
            cursor.execute("UPDATE account SET balance = balance - %s WHERE account_number = %s", (amount, acc_no))
            new_balance = current_balance - amount
            self.log_transaction(cursor, acc_no, 'WITHDRAW', amount, None, new_balance)
            conn.commit()
            return {"message": "Withdrawal successful", "new_balance": new_balance}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def transfer(self, from_acc: int, to_acc: int, amount: Decimal):
        conn = get_db()
        cursor = conn.cursor()
        try:
            if conn.in_transaction:
                conn.rollback()
            amount = Decimal(str(amount))
            if from_acc == to_acc:
                raise ValueError("Cannot transfer to same account")
            conn.start_transaction()
            cursor.execute("SELECT balance FROM account WHERE account_number = %s FOR UPDATE", (from_acc,))
            from_result = cursor.fetchone()
            cursor.execute("SELECT account_number FROM account WHERE account_number = %s FOR UPDATE", (to_acc,))
            to_result = cursor.fetchone()
            if not from_result:
                conn.rollback()
                raise ValueError("Sender account not found")
            if not to_result:
                conn.rollback()
                raise ValueError("Receiver account not found")
            from_balance = from_result[0]
            if from_balance < amount:
                conn.rollback()
                raise ValueError("Insufficient balance")
            cursor.execute("UPDATE account SET balance = balance - %s WHERE account_number = %s", (amount, from_acc))
            cursor.execute("UPDATE account SET balance = balance + %s WHERE account_number = %s", (amount, to_acc))
            new_from_balance = from_balance - amount
            cursor.execute("SELECT balance FROM account WHERE account_number = %s", (to_acc,))
            new_to_balance = cursor.fetchone()[0]
            self.log_transaction(cursor, from_acc, 'TRANSFER_OUT', amount, to_acc, new_from_balance)
            self.log_transaction(cursor, to_acc, 'TRANSFER_IN', amount, from_acc, new_to_balance)
            conn.commit()
            return {"message": "Transfer successful", "new_balance": new_from_balance}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def show_history(self, acc_no: int):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""SELECT type, amount, related_acc, balance_after, timestamp
                              FROM transactions WHERE acc_number = %s ORDER BY timestamp DESC LIMIT 10""", (acc_no,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()