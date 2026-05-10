# app/database.py
# यो file database connection र DB session manage गर्न प्रयोग हुन्छ


# os module import gareko
# Environment variable read garna use huncha
import os


# dotenv bata load_dotenv import gareko
# .env file vitra ko variables load garna use huncha
from dotenv import load_dotenv


# SQLAlchemy bata create_engine import gareko
# Database connection engine create garna use huncha
from sqlalchemy import create_engine


# SQLAlchemy ORM bata sessionmaker ra declarative_base import gareko
# sessionmaker      -> database session banaune factory
# declarative_base  -> ORM model classes ko base class banauna
from sqlalchemy.orm import sessionmaker, declarative_base


# .env file load gareko
# Example: DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
load_dotenv()


# .env file bata DATABASE_URL value read gareko
# DATABASE_URL database connect garne full connection string ho
DATABASE_URL = os.getenv("DATABASE_URL")


# Database engine create gareko
# Engine = Python app ra database bich ko main connection manager
engine = create_engine(DATABASE_URL)


# SessionLocal database session create garne factory ho
# Later: db = SessionLocal() garera actual session banaincha
SessionLocal = sessionmaker(

    # autocommit=False means database changes automatically save hudaina
    # Save garna manually db.commit() garnu parcha
    autocommit=False,

    # autoflush=False means SQLAlchemy le pending changes automatic flush gardaina
    # Manual control ko lagi False rakhincha
    autoflush=False,

    # Yo session kun database engine sanga connected cha vanera specify gareko
    bind=engine
)


# Base class create gareko
# Sabai SQLAlchemy model classes le yo Base inherit garchan
# Example: class Student(Base):
Base = declarative_base()


# get_db function database session provide garna banako
# FastAPI ma dependency injection ko lagi use huncha
def get_db():

    # New database session create gareko
    # Yo session bata query, add, update, delete garna sakincha
    db = SessionLocal()

    try:
        # yield le db session route/function lai provide garcha
        # db session लाई temporarily FastAPI route मा पठाउने।
        # Function complete नभएसम्म session open रहन्छ
        yield db

    finally:
        # Request complete भएपछि database session close garcha
        # Connection leak prevent garna important cha
        db.close()
        
    # db route लाई दिन्छ
    # function temporarily pause हुन्छ
    # route को काम सकिएपछि function फेरि continue हुन्छ
    # अनि finally भित्रको db.close() चल्छ