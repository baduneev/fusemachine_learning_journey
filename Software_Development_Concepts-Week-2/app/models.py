# app/models.py
# यो file मा database tables को SQLAlchemy ORM models define गरिन्छ


# SQLAlchemy bata required column types import gareko
# Column     -> table ko column define garna
# Integer    -> integer number type column
# String     -> text/string type column
# Numeric    -> decimal number type column, e.g. money/amount/creditLimit
# ForeignKey -> another table ko primary key sanga relation banauna
# Date       -> date type column
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date


# relationship import gareko
# Yo tables/classes बीच relation define garna use huncha
# Example: Customer ko multiple orders huncha
from sqlalchemy.orm import relationship


# database.py bata Base import gareko
# Sabai model classes le Base inherit garchan
from .database import Base


# Customer model class define gareko
# Yo Python class database ko customers table sanga map huncha
class Customer(Base):

    # Database table ko actual name define gareko
    __tablename__ = "customers"

    # customerNumber column define gareko
    # Integer type, primary key, index for faster searching
    customerNumber = Column(Integer, primary_key=True, index=True)

    # customerName column define gareko
    # String type text data store garna
    customerName = Column(String)

    # Customer contact person's last name
    contactLastName = Column(String)

    # Customer contact person's first name
    contactFirstName = Column(String)

    # Customer phone number
    phone = Column(String)

    # Customer address line 1
    addressLine1 = Column(String)

    # Customer address line 2
    addressLine2 = Column(String)

    # Customer city
    city = Column(String)

    # Customer state/province
    state = Column(String)

    # Customer postal/zip code
    postalCode = Column(String)

    # Customer country
    country = Column(String)

    # Sales representative employee number
    # यो column employee table sanga relate हुन सक्छ, तर यहाँ ForeignKey define गरिएको छैन
    salesRepEmployeeNumber = Column(Integer)

    # Customer ko credit limit
    # Numeric use gareko because money/decimal value accurate store गर्न राम्रो हुन्छ
    creditLimit = Column(Numeric)

    # Customer र Order बीच relationship define gareko
    # One customer can have many orders
    # back_populates="customer" means Order class ko customer relationship sanga link huncha
    orders = relationship("Order", back_populates="customer")

    # Customer र Payment बीच relationship define gareko
    # One customer can have many payments
    # back_populates="customer" means Payment class ko customer relationship sanga link huncha
    payments = relationship("Payment", back_populates="customer")


# Order model class define gareko
# Yo Python class database ko orders table sanga map huncha
class Order(Base):

    # Database table ko actual name define gareko
    __tablename__ = "orders"

    # orderNumber column define gareko
    # Integer type, primary key, index for faster searching
    orderNumber = Column(Integer, primary_key=True, index=True)

    # Order placed date
    orderDate = Column(Date)

    # Order required delivery date
    requiredDate = Column(Date)

    # Order shipped date
    shippedDate = Column(Date)

    # Order status, e.g. Shipped, Cancelled, In Process
    status = Column(String)

    # Extra comments related to order
    comments = Column(String)

    # customerNumber column define gareko
    # Yo orders table ko foreign key ho
    # It references customers table ko customerNumber column
    customerNumber = Column(Integer, ForeignKey("customers.customerNumber"))

    # Order र Customer बीच relationship define gareko
    # Each order belongs to one customer
    # back_populates="orders" means Customer class ko orders relationship sanga link huncha
    customer = relationship("Customer", back_populates="orders")


# Payment model class define gareko
# Yo Python class database ko payments table sanga map huncha
class Payment(Base):

    # Database table ko actual name define gareko
    __tablename__ = "payments"

    # customerNumber column define gareko
    # ForeignKey le customers table ko customerNumber lai reference garcha
    # primary_key=True because payments table ma composite primary key ko part ho
    customerNumber = Column(Integer, ForeignKey("customers.customerNumber"), primary_key=True)

    # checkNumber column define gareko
    # String type
    # primary_key=True, so customerNumber + checkNumber मिलेर composite primary key bancha
    checkNumber = Column(String, primary_key=True)

    # Payment date
    paymentDate = Column(Date)

    # Payment amount
    # Numeric use gareko because amount/money decimal value ho
    amount = Column(Numeric)

    # Payment र Customer बीच relationship define gareko
    # Each payment belongs to one customer
    # back_populates="payments" means Customer class ko payments relationship sanga link huncha
    customer = relationship("Customer", back_populates="payments")
    
    
    
class Product(Base):
    __tablename__ = "products"

    productCode = Column(String, primary_key=True, index=True)
    productName = Column(String)
    productLine = Column(String)
    productScale = Column(String)
    productVendor = Column(String)
    productDescription = Column(String)
    quantityInStock = Column(Integer)
    buyPrice = Column(Numeric)
    MSRP = Column(Numeric)


class Employee(Base):
    __tablename__ = "employees"

    employeeNumber = Column(Integer, primary_key=True, index=True)
    lastName = Column(String)
    firstName = Column(String)
    extension = Column(String)
    email = Column(String)
    officeCode = Column(String)
    reportsTo = Column(Integer)
    jobTitle = Column(String)


class Office(Base):
    __tablename__ = "offices"

    officeCode = Column(String, primary_key=True, index=True)
    city = Column(String)
    phone = Column(String)
    addressLine1 = Column(String)
    addressLine2 = Column(String)
    state = Column(String)
    country = Column(String)
    postalCode = Column(String)
    territory = Column(String)


class OrderDetail(Base):
    __tablename__ = "orderdetails"

    orderNumber = Column(Integer, primary_key=True)
    productCode = Column(String, primary_key=True)
    quantityOrdered = Column(Integer)
    priceEach = Column(Numeric)
    orderLineNumber = Column(Integer)


class ProductLine(Base):
    __tablename__ = "productlines"

    productLine = Column(String, primary_key=True, index=True)
    textDescription = Column(String)
    htmlDescription = Column(String)
    image = Column(String)