# Pydantic bata BaseModel import gareko
# BaseModel use garera data validation/schema define garincha
from pydantic import BaseModel


# Common student fields define gareko base schema
# Yo class direct API ma use nagare pani reuse garna useful huncha
class StudentBase(BaseModel):
    # Student ko name string type hunuparcha
    name: str

    # Student ko age integer type hunuparcha
    age: int

    # Student ko department string type hunuparcha
    department: str

    # Student ko GPA float/decimal type hunuparcha
    gpa: float


# Student create garna use hune schema
# StudentBase ka सबै fields inherit garcha
class StudentCreate(StudentBase):
    # pass means yo class ma extra field add gareko chaina
    # Create गर्दा name, age, department, gpa सबै required huncha
    pass


# Student update garna use hune schema
# Update ma सबै fields optional banako cha
class StudentUpdate(BaseModel):
    # name optional cha
    # None default means user le name नपठाए पनि huncha
    name: str | None = None

    # age optional cha
    age: int | None = None

    # department optional cha
    department: str | None = None

    # gpa optional cha
    gpa: float | None = None


# API response ma return garna use hune schema
# StudentBase inherit gareko, so name, age, department, gpa already cha
class StudentResponse(StudentBase):
    # Response ma database bata generated id pani include huncha
    id: int

    # Pydantic configuration class
    class Config:
        # SQLAlchemy ORM object bata pani data read garna allow garcha
        # Example: Student model object lai StudentResponse schema ma convert garna milcha
        from_attributes = True  
        # SQLAlchemy model object ko attributes lai Pydantic schema (JSON) ma map garcha
        