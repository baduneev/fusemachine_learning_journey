# app/router.py
# यो file मा customer-related API routes/endpoints define गरिन्छ
import asyncio
import logging
import time

logger = logging.getLogger(__name__)    


# FastAPI bata APIRouter, Depends, HTTPException import gareko
# APIRouter     -> routes lai separate file/module ma organize garna
# Depends       -> dependency injection ko lagi, e.g. DB session get garna
# HTTPException -> error response return garna, e.g. 404, 400
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy ORM bata Session import gareko
# Type hint ko lagi use huncha: db: Session
from sqlalchemy.orm import Session

# typing bata List import gareko
# Response model ma list type define garna use huncha
from typing import List


# database.py bata get_db import gareko
# get_db le database session provide garcha
from .database import SessionLocal, get_db

# same app package bata crud ra schemas import gareko
# crud    -> database operation functions
# schemas -> Pydantic request/response schemas
from . import crud, schemas


# APIRouter object create gareko
# Yo router ma customer-related endpoints group garincha
router = APIRouter(

    # सबै routes ko अगाडि /customers prefix add huncha
    # Example: "/" route actually "/customers/" huncha
    prefix="/customers",

    # Swagger UI/docs ma yo group "Customers" name le dekhincha
    tags=["Customers"]
)


@router.get("/overall_counts")
async def overall_counts():
    logger.info("GET /overall_counts called")
    start_time = time.time()

    try:
        logger.info("Starting all 8 count tasks concurrently")

        tasks = [
            asyncio.to_thread(run_count_function, crud.get_customers_count),
            asyncio.to_thread(run_count_function, crud.get_orders_count),
            asyncio.to_thread(run_count_function, crud.get_products_count),
            asyncio.to_thread(run_count_function, crud.get_employees_count),
            asyncio.to_thread(run_count_function, crud.get_offices_count),
            asyncio.to_thread(run_count_function, crud.get_payments_count),
            asyncio.to_thread(run_count_function, crud.get_orderdetails_count),
            asyncio.to_thread(run_count_function, crud.get_productlines_count),
        ]

        results = await asyncio.gather(*tasks)

        logger.info("asyncio.gather completed successfully")

        response = {
            "customers": results[0],
            "orders": results[1],
            "products": results[2],
            "employees": results[3],
            "offices": results[4],
            "payments": results[5],
            "orderdetails": results[6],
            "productlines": results[7],
        }

        total_time = time.time() - start_time
        logger.info(f"/overall_counts completed in {total_time:.4f} seconds")

        return response

    except Exception as e:
        logger.error(f"Error in /overall_counts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch overall counts")






@router.get("/customers/count")
def customers_count(db: Session = Depends(get_db)):
    logger.info("GET /customers/count called")
    return {"customers": crud.get_customers_count(db)}





# GET endpoint define gareko
# URL: /customers/
# काम: customers ko list read garne
# response_model=List[schemas.CustomerOut] means response list of CustomerOut format ma huncha
@router.get("/", response_model=List[schemas.CustomerOut])
def read_customers(
    # skip query parameter ho
    # Example: /customers/?skip=10
    # first 10 records skip garna
    skip: int = 0,

    # limit query parameter ho
    # Example: /customers/?limit=20
    # maximum 20 records return garna
    limit: int = 10,

    # FastAPI le get_db() bata DB session automatically provide garcha
    db: Session = Depends(get_db)
):
    # crud.py ko get_customers function call gareko
    # skip ra limit pass gareko for pagination
    return crud.get_customers(db, skip=skip, limit=limit)


# GET endpoint define gareko with path parameter
# URL: /customers/{customer_number}
# Example: /customers/103
# काम: particular customer detail read garne
# response_model=schemas.CustomerDetailOut means customer + orders + payments return huncha
@router.get("/{customer_number}", response_model=schemas.CustomerDetailOut)
def read_customer(
    # URL bata customer_number receive huncha
    customer_number: int,

    # DB session dependency
    db: Session = Depends(get_db)
):
    # customer_number ko basis ma customer search gareko
    customer = crud.get_customer(db, customer_number)

    # यदि customer भेटिएन भने 404 error raise garne
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Customer भेटियो भने customer detail return garne
    return customer


# POST endpoint define gareko
# URL: /customers/
# काम: new customer add/create garne
# response_model=schemas.CustomerOut means created customer response format
@router.post("/", response_model=schemas.CustomerOut)
def add_customer(
    # Request body bata आउने customer data
    # CustomerCreate schema le data validate garcha
    customer: schemas.CustomerCreate,

    # DB session dependency
    db: Session = Depends(get_db)
):
    # Create गर्नु अघि same customerNumber भएको customer already छ कि check gareko
    existing_customer = crud.get_customer(db, customer.customerNumber)

    # यदि customer already exists cha भने 400 Bad Request error
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer already exists")

    # Existing छैन भने new customer create gareko
    return crud.create_customer(db, customer)


# PATCH endpoint define gareko
# URL: /customers/{customer_number}
# Example: /customers/103
# काम: existing customer ko selected fields update garne
# response_model=schemas.CustomerOut means updated customer response format
@router.patch("/{customer_number}", response_model=schemas.CustomerOut)
def edit_customer(
    # URL bata update garna parne customer number receive huncha
    customer_number: int,

    # Request body bata update data receive huncha
    # CustomerUpdate schema ma सबै fields optional छन
    customer_update: schemas.CustomerUpdate,

    # DB session dependency
    db: Session = Depends(get_db)
):
    # crud.py ko update_customer function call gareko
    updated_customer = crud.update_customer(db, customer_number, customer_update)

    # यदि customer भेटिएन भने 404 error
    if updated_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Updated customer return gareko
    return updated_customer


# DELETE endpoint define gareko
# URL: /customers/{customer_number}
# Example: /customers/103
# काम: particular customer delete garne
@router.delete("/{customer_number}")
def remove_customer(customer_number: int, db: Session = Depends(get_db)):
    deleted_customer = crud.delete_customer(db, customer_number)

    if deleted_customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    if deleted_customer == "HAS_RELATED_DATA":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete customer because this customer has related orders or payments"
        )

    return {"message": "Customer deleted successfully"}





@router.get("/orders/count")
def orders_count(db: Session = Depends(get_db)):
    logger.info("GET /orders/count called")
    return {"orders": crud.get_orders_count(db)}


@router.get("/products/count")
def products_count(db: Session = Depends(get_db)):
    logger.info("GET /products/count called")
    return {"products": crud.get_products_count(db)}


@router.get("/employees/count")
def employees_count(db: Session = Depends(get_db)):
    logger.info("GET /employees/count called")
    return {"employees": crud.get_employees_count(db)}


@router.get("/offices/count")
def offices_count(db: Session = Depends(get_db)):
    logger.info("GET /offices/count called")
    return {"offices": crud.get_offices_count(db)}


@router.get("/payments/count")
def payments_count(db: Session = Depends(get_db)):
    logger.info("GET /payments/count called")
    return {"payments": crud.get_payments_count(db)}


@router.get("/orderdetails/count")
def orderdetails_count(db: Session = Depends(get_db)):
    logger.info("GET /orderdetails/count called")
    return {"orderdetails": crud.get_orderdetails_count(db)}


@router.get("/productlines/count")
def productlines_count(db: Session = Depends(get_db)):
    logger.info("GET /productlines/count called")
    return {"productlines": crud.get_productlines_count(db)}


def run_count_function(count_function):
    db = SessionLocal()
    try:
        return count_function(db)
    finally:
        db.close()
        
