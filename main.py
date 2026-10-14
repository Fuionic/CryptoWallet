from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import Database
import auth
from model import Transaction 
from Database import session
from sqlalchemy.orm import Session
import httpx
import os

app = FastAPI()
app.include_router(auth.router)
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


@app.post("/addtransaction")
def add_transaction(
    transaction: Transaction,
    db: Session = Depends(get_db),
    current_user: Database.User = Depends(auth.get_current_user),
):
    db.add(Database.Transaction(**transaction.model_dump(), user_id=current_user.id))
    db.commit()
    return {"message": "Transaction added successfully"}


@app.get("/all")
def get_portfolio(
    db: Session = Depends(get_db),
    current_user: Database.User = Depends(auth.get_current_user),
):
    transactions = db.query(Database.Transaction).filter(
        Database.Transaction.user_id == current_user.id
    ).all()
    return transactions


@app.get("/search/{crypto_name}")
def get_by_name(
    crypto_name: str,
    db: Session = Depends(get_db),
    current_user: Database.User = Depends(auth.get_current_user),
):
    transactions = db.query(Database.Transaction).filter(
        Database.Transaction.user_id == current_user.id,
        Database.Transaction.crypto_name.ilike(f"%{crypto_name}%")
    ).all()

    return [
        {
            "id": tx.id,
            "transaction_type": tx.transaction_type,
            "crypto_name": tx.crypto_name,
            "price_per_unit": tx.price_per_unit,
            "quantity": tx.quantity,
        }
        for tx in transactions
    ]


@app.put("/update/{crypto_name}")
def update(
    crypto_name: str,
    newtransaction: Transaction,
    db: Session = Depends(get_db),
    current_user: Database.User = Depends(auth.get_current_user),
):
    transaction = db.query(Database.Transaction).filter(
        Database.Transaction.crypto_name == crypto_name,
        Database.Transaction.user_id == current_user.id,
    ).first()
    if transaction:
        transaction.transaction_type = newtransaction.transaction_type
        transaction.crypto_name = newtransaction.crypto_name
        transaction.price_per_unit = newtransaction.price_per_unit
        transaction.quantity = newtransaction.quantity
        db.commit()
        return {"message": "Transaction updated successfully"}
    else:
        return {"message": "Transaction not found"}


@app.delete("/delete/{id}")
def deleteTransaction(
    id: int,
    db: Session = Depends(get_db),
    current_user: Database.User = Depends(auth.get_current_user),
):
    transaction = db.query(Database.Transaction).filter(
        Database.Transaction.id == id,
        Database.Transaction.user_id == current_user.id,
    ).first()
    if transaction:
        db.delete(transaction)
        db.commit()
        return {"message": "Transaction deleted successfully"}
    else:
        return {"message": "Transaction not found"}


@app.get("/portfolio/live")
async def get_portfolio(
    db: Session = Depends(get_db),
    current_user: Database.User = Depends(auth.get_current_user),
):
    transactions = db.query(Database.Transaction).filter(
        Database.Transaction.user_id == current_user.id
    ).all()

    if not transactions:
        return {
            "total_portfolio_value": 0.0,
            "portfolio_change_percent": 0.0,
            "daily_profit_loss": 0.0,
            "net_flow": 0.0,
            "transactions": []
        }

    coin_ids = ",".join({tx.crypto_name.lower().strip() for tx in transactions if tx.crypto_name})

    cg_url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_ids, "vs_currencies": "usd"}
    headers = {"x-cg-demo-api-key": COINGECKO_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(cg_url, params=params, headers=headers, timeout=20.0)
        live_response = response.json() if response.status_code == 200 else {}

    total_value = 0.0
    detailed_list = []

    for tx in transactions:
        coin_name = tx.crypto_name.lower().strip()
        live_price = live_response.get(coin_name, {}).get("usd", tx.price_per_unit)
        current_value = tx.quantity * live_price

        if tx.transaction_type in ("buy", Database.Transaction_type.BUY):
            total_value += current_value
        elif tx.transaction_type in ("sell", Database.Transaction_type.SELL):
            total_value -= current_value

        detailed_list.append({
            "id": tx.id,
            "transaction_type": tx.transaction_type,
            "crypto_name": tx.crypto_name,
            "quantity": tx.quantity,
            "purchased_price_per_unit": tx.price_per_unit,
            "real_time_price_per_unit": live_price,
            "current_item_value": round(current_value, 2),
        })

    return {
        "total_portfolio_value": round(total_value, 2),
        "portfolio_change_percent": 0.0,
        "daily_profit_loss": 0.0,
        "net_flow": round(total_value, 2),
        "transactions": detailed_list,
    }