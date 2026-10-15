from sqlalchemy.orm import sessionmaker
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Enum
from enum import Enum as PyEnum

load_dotenv()

database_password = os.environ.get("DATABASE_PASSWORD")
if not database_password:
    raise RuntimeError("DATABASE_PASSWORD must be set in the environment or .env file")

db_url = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password=database_password,
    host="localhost",
    port=5432,
    database="Wallet",
)

engine = create_engine(db_url)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
    quantity = Column(Float)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=True, index=True)


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=True)


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

