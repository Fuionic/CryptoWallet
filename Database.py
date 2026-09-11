from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Enum
from enum import Enum as PyEnum

db_url = "postgresql://{credential}@localhost:5432/Wallet"

engine = create_engine(db_url)
session = sessionmaker(autocommit = False, autoflush = False, bind = engine)


Base = declarative_base()

class Transaction_type(str, PyEnum):
    BUY = "buy"
    SELL = "sell"

class Transaction(Base):

    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True) 
    transaction_type = Column(Enum(Transaction_type))
    crypto_name = Column(String)
    price_per_unit = Column(Float)
    quantity = Column(Integer)


class User(Base):

    __tablename__ = "Users"

    id  = Column(Integer, primary_key=True, index=True)
    email = Column(String)


Base.metadata.create_all(bind = engine)


    

