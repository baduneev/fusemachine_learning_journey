# database.py
# यो file database connection setup गर्न र raw SQL execute गर्न use हुन्छ


# os module import gareko
# Environment variable read garna use huncha
import os


# dotenv bata load_dotenv import gareko
# .env file vitra ko variables load garna use huncha
from dotenv import load_dotenv


# SQLAlchemy bata create_engine ra text import gareko
# create_engine -> database connection engine create garna
# text          -> raw SQL query lai SQLAlchemy executable SQL object banauna
from sqlalchemy import create_engine, text


# SQLAlchemy ORM bata sessionmaker import gareko
# sessionmaker -> database session create garne factory banauna
from sqlalchemy.orm import sessionmaker


# .env file load gareko
# Example .env:
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
load_dotenv()


# .env file bata DATABASE_URL read gareko
# DATABASE_URL database connection string ho
DATABASE_URL = os.getenv("DATABASE_URL")


# Database engine create gareko
# Engine = Python app ra database bich ko main connection manager
engine = create_engine(DATABASE_URL)


# Database session factory create gareko
# SessionLocal() call garda actual DB session create huncha
SessionLocal = sessionmaker(

    # autocommit=False means query/changes automatically commit hudaina
    # Manual commit garna parcha if insert/update/delete gareko cha
    autocommit=False,

    # autoflush=False means SQLAlchemy le pending changes automatic flush gardaina
    # Manual control ko lagi False rakhincha
    autoflush=False,

    # Yo session kun database engine sanga bind/connect huncha define gareko
    bind=engine
)


# New database session return garne function
# यो function call गर्दा fresh DB session paaincha
def get_db_session():

    # SessionLocal() le actual database session create garcha
    return SessionLocal()


# Raw SQL query execute garne function
# sql: str means input SQL query string huncha
def execute_raw_sql(sql: str):

    # Database session create gareko
    db = get_db_session()

    try:
        # Raw SQL string lai text(sql) le executable SQL object banaucha
        # db.execute() le SQL query database ma run garcha
        result = db.execute(text(sql))

        # Query result bata सबै rows fetch gareko
        # Example: [(1, "Ram"), (2, "Sita")]
        rows = result.fetchall()

        # Result ko column names fetch gareko
        # Example: ["id", "name"]
        columns = result.keys()

        # Rows ra columns lai dictionary format ma convert gareko
        # Example:
        # columns = ["id", "name"]
        # row = (1, "Ram")
        # dict(zip(columns, row)) => {"id": 1, "name": "Ram"}
        data = [dict(zip(columns, row)) for row in rows]

        # Final data list return gareko
        # API/LLM pipeline le use garna easy JSON-like format ma huncha
        return data

    finally:
        # Query complete भए पनि वा error आए पनि session close हुन्छ
        # Connection leak prevent garna important cha
        db.close()