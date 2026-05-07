# SQLAlchemy ORM bata Session import gareko
# Session database sanga CRUD operation garna use huncha
from sqlalchemy.orm import Session

# models.py bata Student ORM model import gareko
# Yo database ko students table sanga map huncha
from models import Student

# schemas.py bata Pydantic schemas import gareko
# StudentCreate -> new student create garna
# StudentUpdate -> existing student update garna
from schemas import StudentCreate, StudentUpdate


# New student create garne function
# db: Session means database session receive garcha
# student: StudentCreate means validated input data receive garcha
def create_student(db: Session, student: StudentCreate):

    # Student ORM object create gareko
    # Pydantic schema bata आएको data lai database model object ma convert gareko
    new_student = Student(
        name=student.name,
        age=student.age,
        department=student.department,
        gpa=student.gpa
    )

    # New student object lai database session ma add gareko
    # यो अझै permanently save भएको छैन
    db.add(new_student)

    # Database ma permanently save gareko
    db.commit()

    # Database bata latest data reload gareko
    # Example: auto-generated id fetch garna useful huncha
    db.refresh(new_student)

    # Created student object return gareko
    return new_student


# सबै students database bata read garne function
def get_all_students(db: Session):

    # Student table bata सबै records fetch gareko
    # .all() le list of students return garcha
    return db.query(Student).all()


# Particular student id ko आधारमा student find garne function
def get_student_by_id(db: Session, student_id: int):

    # Student table ma id match garne first record search gareko
    # भेटिए student object return huncha, नभेटिए None return huncha
    return db.query(Student).filter(Student.id == student_id).first()


# Existing student update garne function
def update_student(db: Session, student_id: int, student_data: StudentUpdate):

    # पहिले given student_id भएको student database ma खोजेको
    student = db.query(Student).filter(Student.id == student_id).first()

    # यदि student भेटिएन भने None return garne
    if student is None:
        return None

    # Pydantic object lai dictionary ma convert gareko
    # exclude_unset=True means user le पठाएको fields मात्र dictionary ma आउँछ
    # Example: only {"gpa": 3.9} पठायो भने अरू fields update हुँदैनन्
    update_data = student_data.model_dump(exclude_unset=True)

    # Dictionary vitra भएका key-value pair loop gareko
    for key, value in update_data.items():

        # setattr() le object ko attribute dynamically update garcha
        # Example: setattr(student, "name", "Ram") means student.name = "Ram"
        setattr(student, key, value)

    # Updated data database ma permanently save gareko
    db.commit()

    # Database bata latest updated student reload gareko
    db.refresh(student)

    # Updated student return gareko
    return student


# Student delete garne function
def delete_student(db: Session, student_id: int):

    # पहिले delete garna खोजिएको student database ma छ कि छैन check gareko
    student = db.query(Student).filter(Student.id == student_id).first()

    # यदि student भेटिएन भने None return garne
    if student is None:
        return None

    # Student object lai delete mark gareko
    # यो अझै permanently delete भएको छैन
    db.delete(student)

    # Database ma delete operation permanently save gareko
    db.commit()
    

    # Deleted student object return gareko
    return student