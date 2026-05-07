# os module import gareko
# Yo environment variables access garna use huncha
import os

# dotenv package bata load_dotenv function import gareko
# Yo .env file vitra ko variables Python project ma load garna use huncha
from dotenv import load_dotenv

# SQLAlchemy bata create_engine import gareko
# Yo database sanga connection engine banauna use huncha
from sqlalchemy import create_engine

# SQLAlchemy ORM bata sessionmaker ra declarative_base import gareko
# sessionmaker -> database session create garna
# declarative_base -> model/table class banauna base class provide garna
from sqlalchemy.orm import sessionmaker, declarative_base


# .env file load gareko
# Example: DATABASE_URL="postgresql://neev:1234@localhost:5432/studentdb"
load_dotenv()


# .env file bata DATABASE_URL variable read gareko
# DATABASE_URL ma database connection string huncha
DATABASE_URL = os.getenv("DATABASE_URL")


# Database engine create gareko
# Engine vaneko Python app ra database bich ko main connection manager ho
engine = create_engine(DATABASE_URL)

# DB Session = Python app र Database बीचको temporary working connection/transaction object हो।
# Database session factory create gareko
# SessionLocal use garera later database operation garne session banaunchau
SessionLocal = sessionmaker(
    # autocommit=False means database changes automatically commit hudaina
    # commit garna manually db.commit() garnu parcha
    autocommit=False,

    # autoflush=False means SQLAlchemy le automatically pending changes database ma flush gardaina
    # Usually manual control ko lagi False rakhincha
    autoflush=False,

    # Yo session kun engine/database sanga bind huncha vanera specify gareko
    bind=engine
)


# Base class create gareko
# Sabai ORM models/classes yo Base inherit garera table define garchan
Base = declarative_base()