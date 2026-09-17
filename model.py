from pydantic import BaseModel
from enum import Enum

class Transaction_type(str, Enum):
    BUY = "buy"
    SELL = "sell"

class Transaction(BaseModel):
    transaction_type : Transaction_type
    crypto_name : str
    price_per_unit : float
    quantity : float


class User(BaseModel):
    id : int
    email : str





    

