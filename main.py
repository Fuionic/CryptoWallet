from fastapi import FastAPI
from model import Transaction 
import pydantic
from Database import session


app = FastAPI()

@app.get("/addtransaction")
def add_transaction(transcation : Transaction):
    
    return "Transaction added successsfully"


@app.get("/all")
def get_portfolio():
    return #db_logc
    #conversion rates with api calling
    
    # return "Transaction not found"


@app.get("/search/{id}")
def get_by_id(id : int):
    #databsse logic
    #conversion rates with api calling
    return "Transaction not found"


@app.put("/update/{id}")
def update(id : int , newtransaction : Transaction):

    #database logic
    return "Updated Successfully"

    # return "failed to add product"

@app.delete("/delete/{id}")
def deleteTransaction(id : int):
    #database logic
    return "Transaction delted"