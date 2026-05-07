# FastAPI bata required classes/functions import gareko
# FastAPI      -> app create garna
# Depends      -> dependency injection ko lagi, e.g. DB session automatically provide garna
# HTTPException -> error response pathauna, e.g. 404 Student not found
from fastapi import FastAPI, Depends, HTTPException

# SQLAlchemy ORM ko Session import gareko
# Type hint ko lagi use huncha: db: Session
from sqlalchemy.orm import Session


# models.py import gareko
# Yo file ma SQLAlchemy models/tables define gareko huncha
import models

# crud.py import gareko
# Yo file ma create, read, update, delete functions huncha
import crud

# database.py bata engine ra SessionLocal import gareko
# engine       -> database connection manager
# SessionLocal -> database session banaune factory
from database import engine, SessionLocal

# schemas.py bata Pydantic schemas import gareko
# StudentCreate   -> create request body validation
# StudentUpdate   -> update request body validation
# StudentResponse -> API response format
from schemas import StudentCreate, StudentUpdate, StudentResponse


# Database ma tables create garne line
# models.py ma define gareko सबै tables database ma create huncha
# यदि table पहिले नै exist cha भने फेरि duplicate create गर्दैन
models.Base.metadata.create_all(bind=engine)


# FastAPI application object create gareko
# title Swagger UI/docs ma देखिन्छ
app = FastAPI(title="Student CRUD API with PostgreSQL")


# Database session provide garne dependency function
# प्रत्येक API request ko lagi separate DB session open/close garna use huncha
def get_db():

    # New database session create gareko
    db = SessionLocal()

    try:
        # yield le यो db session route function lai provide garcha
        # Example: db: Session = Depends(get_db)
        yield db

    finally:
        # Request complete भएपछि database session close garcha
        # यो important ho, connection leak hunna
        db.close()


# POST API endpoint
# URL: /students
# काम: new student create garne
# response_model=StudentResponse means response StudentResponse format ma return huncha
@app.post("/students", response_model=StudentResponse)
def create_student(
    # Request body bata आउने student data validate huncha StudentCreate schema bata
    student: StudentCreate,

    # FastAPI le get_db() call garera db session provide garcha
    db: Session = Depends(get_db)
):
    # crud.py ko create_student function call gareko
    # db session ra validated student data pass gareko
    return crud.create_student(db, student)


# GET API endpoint
# URL: /students
# काम: database bata सबै students read garne
# response_model=list[StudentResponse] means response students ko list huncha
@app.get("/students", response_model=list[StudentResponse])
def read_students(
    # DB session dependency
    db: Session = Depends(get_db)
):
    # crud.py ko get_all_students function call gareko
    return crud.get_all_students(db)


# GET API endpoint with path parameter
# URL example: /students/1
# काम: particular id भएको student read garne
@app.get("/students/{student_id}", response_model=StudentResponse)
def read_student(
    # URL bata student_id receive huncha
    student_id: int,

    # DB session dependency
    db: Session = Depends(get_db)
):
    # Given id ko student database bata खोजेको
    student = crud.get_student_by_id(db, student_id)

    # यदि student भेटिएन भने 404 error return garne
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # Student भेटियो भने response return garne
    return student


# PATCH API endpoint
# URL example: /students/1
# काम: particular student ko केही fields update garne
# PATCH usually partial update ko lagi use huncha
@app.patch("/students/{student_id}", response_model=StudentResponse)
def update_student(
    # URL bata update garna parne student ko id receive huncha
    student_id: int,

    # Request body bata update garna parne data receive huncha
    # StudentUpdate schema ma सबै fields optional छन
    student_data: StudentUpdate,

    # DB session dependency
    db: Session = Depends(get_db)
):
    # crud.py ko update_student function call gareko
    student = crud.update_student(db, student_id, student_data)

    # यदि student भेटिएन भने 404 error
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # Updated student return gareko
    return student


# DELETE API endpoint
# URL example: /students/1
# काम: particular id भएको student delete garne
@app.delete("/students/{student_id}")
def delete_student(
    # URL bata delete garna parne student id receive huncha
    student_id: int,

    # DB session dependency
    db: Session = Depends(get_db)
):
    # crud.py ko delete_student function call gareko
    student = crud.delete_student(db, student_id)

    # यदि student भेटिएन भने 404 error
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # Delete successful भएपछि custom message return gareko
    return {
        "message": "Student deleted successfully",
        "deleted_student_id": student_id
    }