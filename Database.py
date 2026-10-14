from sqlalchemy.orm import sessionmaker
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Enum, inspect, text
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
    quantity = Column(Float)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=True, index=True)


class User(Base):

    __tablename__ = "Users"

    id  = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=True)


Base.metadata.create_all(bind = engine)


def migrate_auth_columns():
    tables = set(inspect(engine).get_table_names())

    with engine.begin() as connection:
        if "Users" in tables:
            user_columns = {
                column["name"] for column in inspect(connection).get_columns("Users")
            }
            if "username" not in user_columns:
                connection.execute(text('ALTER TABLE "Users" ADD COLUMN username VARCHAR'))
                connection.execute(
                    text('CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON "Users" (username)')
                )
            if "password" not in user_columns:
                connection.execute(text('ALTER TABLE "Users" ADD COLUMN password VARCHAR'))

        if "transaction" in tables:
            transaction_columns = {
                column["name"] for column in inspect(connection).get_columns("transaction")
            }
            if "user_id" not in transaction_columns:
                connection.execute(
                    text(
                        'ALTER TABLE "transaction" ADD COLUMN user_id INTEGER '
                        'REFERENCES "Users"(id)'
                    )
                )
                connection.execute(
                    text(
                        'CREATE INDEX IF NOT EXISTS ix_transaction_user_id '
                        'ON "transaction" (user_id)'
                    )
                )


migrate_auth_columns()
