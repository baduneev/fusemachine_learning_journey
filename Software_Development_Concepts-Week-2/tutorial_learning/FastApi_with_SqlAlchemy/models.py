# SQLAlchemy bata Column, Integer, String, Float import gareko
# Column  -> table ko column define garna
# Integer -> integer type data ko lagi
# String  -> text/string data ko lagi
# Float   -> decimal number data ko lagi
from sqlalchemy import Column, Integer, String, Float

# database.py file bata Base import gareko
# Base ORM model classes ko parent class ho
from database import Base


# Student class banako
# Yo Python class database ko "students" table sanga map huncha
class Student(Base):

    # Database table ko actual name define gareko
    # PostgreSQL/MySQL/SQLite ma table name "students" huncha
    __tablename__ = "students"

    # id column define gareko
    # Integer type ko huncha
    # primary_key=True means yo unique identifier ho
    # index=True means search/query fast garna index bancha
    id = Column(Integer, primary_key=True, index=True)

    # name column define gareko
    # String type ko huncha
    # nullable=False means yo field empty/null huna paudaina
    name = Column(String, nullable=False)

    # age column define gareko
    # Integer type ko huncha
    # nullable=False means age compulsory field ho
    age = Column(Integer, nullable=False)

    # department column define gareko
    # String type ko huncha
    # nullable=False means department compulsory field ho
    department = Column(String, nullable=False)

    # gpa column define gareko
    # Float type ko huncha, example: 3.75
    # nullable=False means gpa compulsory field ho
    gpa = Column(Float, nullable=False)