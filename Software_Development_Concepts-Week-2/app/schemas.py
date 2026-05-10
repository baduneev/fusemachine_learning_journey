# app/schemas.py
# यो file मा Pydantic schemas define गरिन्छ
# Schemas = API request/response को data format + validation rules


# Pydantic bata BaseModel import gareko
# BaseModel inherit गरेर schema class बनाइन्छ
from pydantic import BaseModel

# typing bata Optional ra List import gareko
# Optional -> value हुन पनि सक्छ, None/null हुन पनि सक्छ
# List     -> list/array type define गर्न
from typing import Optional, List

# datetime bata date import gareko
# Date field define गर्न, e.g. orderDate, paymentDate
from datetime import date

# decimal bata Decimal import gareko
# Money/amount/creditLimit जस्ता exact decimal values को लागि
from decimal import Decimal


# Order ko response/output schema define gareko
# API response ma order data कुन format मा जाने भन्ने define गर्छ
class OrderOut(BaseModel):

    # Order number integer type huncha
    orderNumber: int

    # Order date date type huncha
    orderDate: date

    # Required delivery date date type huncha
    requiredDate: date

    # Shipped date optional date ho
    # None default means shippedDate null हुन सक्छ
    shippedDate: Optional[date] = None

    # Order status string type huncha
    status: str

    # Order comments optional string ho
    # None default means comments null हुन सक्छ
    comments: Optional[str] = None

    # Pydantic configuration class
    class Config:
        # SQLAlchemy ORM object bata attributes read garna allow garcha
        # Example: order.orderNumber, order.status bata value लिन सक्छ
        # object format to dict/JSON मा convert गर्दा काम लाग्छ
        from_attributes = True


# Payment ko response/output schema define gareko
# API response ma payment data कुन format मा जाने भन्ने define गर्छ
class PaymentOut(BaseModel):

    # Payment check number string type huncha
    checkNumber: str

    # Payment date date type huncha
    paymentDate: date

    # Payment amount Decimal type huncha
    # Money value ko lagi Decimal better than float
    amount: Decimal

    # Pydantic configuration class
    class Config:
        # SQLAlchemy Payment object bata value read garna allow garcha
        from_attributes = True


# Customer ko common/base schema define gareko
# Create ra response schemas मा reuse garna banako
class CustomerBase(BaseModel):

    # Customer company/person name
    customerName: str

    # Contact person ko last name
    contactLastName: str

    # Contact person ko first name
    contactFirstName: str

    # Customer phone number
    phone: str

    # Customer address line 1 required field ho
    addressLine1: str

    # Customer address line 2 optional field ho
    # None default means यो field नआए पनि हुन्छ
    addressLine2: Optional[str] = None

    # Customer city required field ho
    city: str

    # Customer state optional field ho
    state: Optional[str] = None

    # Customer postal code optional field ho
    postalCode: Optional[str] = None

    # Customer country required field ho
    country: str

    # Sales representative employee number optional integer ho
    salesRepEmployeeNumber: Optional[int] = None

    # Customer credit limit optional Decimal ho
    creditLimit: Optional[Decimal] = None


# Customer create garna use hune schema
# CustomerBase ko सबै fields inherit garcha
class CustomerCreate(CustomerBase):

    # New customer create गर्दा customerNumber पनि required छ
    # किनकि database model मा customerNumber primary key हो
    customerNumber: int


# Customer update garna use hune schema
# Update ma सबै fields optional banako छ
# यसले partial update/PATCH support गर्छ
class CustomerUpdate(BaseModel):

    # Customer name optional update field
    customerName: Optional[str] = None

    # Contact last name optional update field
    contactLastName: Optional[str] = None

    # Contact first name optional update field
    contactFirstName: Optional[str] = None

    # Phone optional update field
    phone: Optional[str] = None

    # Address line 1 optional update field
    addressLine1: Optional[str] = None

    # Address line 2 optional update field
    addressLine2: Optional[str] = None

    # City optional update field
    city: Optional[str] = None

    # State optional update field
    state: Optional[str] = None

    # Postal code optional update field
    postalCode: Optional[str] = None

    # Country optional update field
    country: Optional[str] = None

    # Sales representative employee number optional update field
    salesRepEmployeeNumber: Optional[int] = None

    # Credit limit optional update field
    creditLimit: Optional[Decimal] = None


# Customer ko normal output/response schema
# CustomerBase inherit gareko, so common fields already included छन्
class CustomerOut(CustomerBase):

    # Response ma customerNumber पनि include huncha
    customerNumber: int

    # Pydantic configuration class
    class Config:
        # SQLAlchemy Customer object bata attributes read garna allow garcha
        # Example: customer.customerName, customer.country bata data लिन सक्छ
        from_attributes = True


# Customer ko detailed output schema
# यो normal customer info + related orders + payments return garna use huncha
class CustomerDetailOut(CustomerOut):

    # Customer ko related orders list
    # List[OrderOut] means orders array भित्र OrderOut format ko data huncha
    # [] default means orders छैन भने empty list return huncha
    orders: List[OrderOut] = []

    # Customer ko related payments list
    # List[PaymentOut] means payments array भित्र PaymentOut format ko data huncha
    # [] default means payments छैन भने empty list return huncha
    payments: List[PaymentOut] = []