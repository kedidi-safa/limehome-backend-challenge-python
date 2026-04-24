from http import HTTPStatus

from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .crud import UnableToBook, UnableToUpdateBook
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def hello_world():
    return {"message": "OK"}


@app.post("/api/v1/booking", response_model=schemas.BookingBase)
def create_booking(booking: schemas.BookingBase, db: Session = Depends(get_db)):
    try:
        return crud.create_booking(db=db, booking=booking)
    except UnableToBook as unable_to_book:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=str(unable_to_book))
        
@app.patch("/api/v1/booking/{id}", response_model=schemas.BookingBase)
def update_booking(id:int, booking: schemas.ExtendStay, db: Session = Depends(get_db)):
    try:
        return crud.update_booking(booking_id=id, db=db, number_of_nights=booking.number_of_nights)
    except UnableToUpdateBook as unable_to_update_book:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=str(unable_to_update_book))
