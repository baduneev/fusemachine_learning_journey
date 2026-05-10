# app/crud.py
# यो file मा database CRUD operations define गरिन्छ
# CRUD = Create, Read, Update, Delete

import logging
# SQLAlchemy ORM bata Session import gareko
# Session database sanga query, insert, update, delete garna use huncha
from sqlalchemy.orm import Session

# same app package bata models ra schemas import gareko
# models  -> SQLAlchemy database table classes
# schemas -> Pydantic request/response validation classes
from . import models, schemas

logger = logging.getLogger(__name__)
# Customers list fetch garne function
# skip = kati ota records skip garne
# limit = maximum kati ota records return garne
def get_customers(db: Session, skip: int = 0, limit: int = 10):

    # Customer table ma query gareko
    # offset(skip) le suru ko records skip garcha
    # limit(limit) le max records limit garcha
    # all() le matching records list ko form ma return garcha
    return db.query(models.Customer).offset(skip).limit(limit).all()


# Single customer fetch garne function
# customer_number ko basis ma customer search garcha
def get_customer(db: Session, customer_number: int):

    # Customer table ma query gareko
    # filter le customerNumber match garne record खोज्छ
    return db.query(models.Customer).filter(

        # models.Customer.customerNumber column ko value
        # customer_number sanga equal cha ki check gareko
        models.Customer.customerNumber == customer_number

    # first() le first matching record return garcha
    # यदि भेटिएन भने None return garcha
    ).first()


# New customer create garne function
# customer parameter CustomerCreate schema bata validated data ho
def create_customer(db: Session, customer: schemas.CustomerCreate):

    # Pydantic schema lai dictionary ma convert gareko
    # ** le dictionary unpack garera Customer model ko fields ma pass garcha
    # Example:
    # {"customerName": "ABC", "city": "Kathmandu"}
    # becomes:
    # Customer(customerName="ABC", city="Kathmandu")
    db_customer = models.Customer(**customer.model_dump())

    # New customer object database session ma add gareko
    # यो अझै permanently database ma save भएको छैन
    db.add(db_customer)

    # Database ma permanently save gareko
    db.commit()

    # Database bata latest data reload gareko
    # Auto-generated/default values refresh garna useful huncha
    db.refresh(db_customer)

    # Created customer object return gareko
    return db_customer


# Existing customer update garne function
# customer_number = कुन customer update garne
# customer_update = update गर्न आएको validated data
def update_customer(db: Session, customer_number: int, customer_update: schemas.CustomerUpdate):

    # पहिले customer database ma exists cha ki छैन check gareko
    db_customer = get_customer(db, customer_number)

    # यदि customer भेटिएन भने None return garne
    if db_customer is None:
        return None

    # Pydantic update object lai dictionary ma convert gareko
    # exclude_unset=True means user le पठाएको fields मात्र include huncha
    # Example: only {"city": "Pokhara"} पठायो भने city मात्र update huncha
    update_data = customer_update.model_dump(exclude_unset=True)

    # update_data dictionary ko each key-value pair loop gareko
    for key, value in update_data.items():

        # setattr le object ko attribute dynamically update garcha
        # Example: setattr(db_customer, "city", "Pokhara")
        # means db_customer.city = "Pokhara"
        setattr(db_customer, key, value)

    # Updated changes database ma permanently save gareko
    db.commit()

    # Database bata updated object reload gareko
    db.refresh(db_customer)

    # Updated customer object return gareko
    return db_customer


# Customer delete garne function
# customer_number ko basis ma customer delete garcha
def delete_customer(db: Session, customer_number: int):
    db_customer = db.query(models.Customer).filter(
        models.Customer.customerNumber == customer_number
    ).first()

    if db_customer is None:
        return None

    order_count = db.query(models.Order).filter(
        models.Order.customerNumber == customer_number
    ).count()

    payment_count = db.query(models.Payment).filter(
        models.Payment.customerNumber == customer_number
    ).count()

    if order_count > 0 or payment_count > 0:
        return "HAS_RELATED_DATA"

    db.delete(db_customer)
    db.commit()

    return db_customer




def get_customers_count(db: Session):
    logger.info("Starting customers count query")
    count = db.query(models.Customer).count()
    logger.info(f"Customers count completed: {count}")
    return count


def get_orders_count(db: Session):
    logger.info("Starting orders count query")
    count = db.query(models.Order).count()
    logger.info(f"Orders count completed: {count}")
    return count


def get_products_count(db: Session):
    logger.info("Starting products count query")
    count = db.query(models.Product).count()
    logger.info(f"Products count completed: {count}")
    return count


def get_employees_count(db: Session):
    logger.info("Starting employees count query")
    count = db.query(models.Employee).count()
    logger.info(f"Employees count completed: {count}")
    return count


def get_offices_count(db: Session):
    logger.info("Starting offices count query")
    count = db.query(models.Office).count()
    logger.info(f"Offices count completed: {count}")
    return count


def get_payments_count(db: Session):
    logger.info("Starting payments count query")
    count = db.query(models.Payment).count()
    logger.info(f"Payments count completed: {count}")
    return count


def get_orderdetails_count(db: Session):
    logger.info("Starting orderdetails count query")
    count = db.query(models.OrderDetail).count()
    logger.info(f"Orderdetails count completed: {count}")
    return count


def get_productlines_count(db: Session):
    logger.info("Starting productlines count query")
    count = db.query(models.ProductLine).count()
    logger.info(f"Productlines count completed: {count}")
    return count