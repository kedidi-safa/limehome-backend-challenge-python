from typing import Tuple
import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from . import models, schemas


class UnableToBook(Exception):
    pass

class UnableToUpdateBook(Exception):
    pass


def create_booking(db: Session, booking: schemas.BookingBase) -> models.Booking:
    is_possible, reason = is_booking_possible(db=db, booking=booking)
    if not is_possible:
        raise UnableToBook(reason)
    db_booking = models.Booking(
        guest_name=booking.guest_name, unit_id=booking.unit_id,
        check_in_date=booking.check_in_date, number_of_nights=booking.number_of_nights)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def update_booking(booking_id: int, db: Session, number_of_nights: int) -> models.Booking:
    existing_booking = db.query(models.Booking).filter(models.Booking.id==booking_id).first()
    if not existing_booking:
        raise UnableToUpdateBook(f"Booking with id {booking_id} not found")
    
    if number_of_nights <= existing_booking.number_of_nights:
        raise UnableToUpdateBook("New number of nights must be greater than the current number")
    
    #Check Unit is available for the extanded period
    new_checkout_date = existing_booking.check_in_date + datetime.timedelta(number_of_nights)
    is_not_possible = db.execute(
        select(models.Booking).where(
            models.Booking.unit_id == existing_booking.unit_id,
            models.Booking.id != existing_booking.id,
            existing_booking.check_in_date < func.date(
                models.Booking.check_in_date,
                func.concat(models.Booking.number_of_nights, ' days')
            ),
            new_checkout_date > models.Booking.check_in_date
        )
    ).scalars().first()

    if is_not_possible:
        raise UnableToUpdateBook("Can not extend, the unit is already occupied")

    existing_booking.number_of_nights = number_of_nights
    db.commit()
    db.refresh(existing_booking)
    return existing_booking


def is_booking_possible(db: Session, booking: schemas.BookingBase) -> Tuple[bool, str]:
    # check 1 : The Same guest cannot book the same unit multiple times
    if db.execute(
        select(models.Booking).where(
            models.Booking.guest_name == booking.guest_name,
            models.Booking.unit_id == booking.unit_id,
        )
    ).scalars().first():
        return False, 'The given guest name cannot book the same unit multiple times'

    # check 2 : the same guest cannot be in multiple units at the same time
    if db.execute(
        select(models.Booking).where(models.Booking.guest_name == booking.guest_name)
    ).scalars().first():
        return False, 'The same guest cannot be in multiple units at the same time'
    
    new_check_in_date= booking.check_in_date
    new_checkout_date= booking.check_in_date + datetime.timedelta(booking.number_of_nights)

    # check 3 : Unit is available for the check-in date
    if db.execute(
        select(models.Booking).where(
            models.Booking.unit_id == booking.unit_id,
            new_check_in_date < func.date(
                models.Booking.check_in_date,
                func.concat(models.Booking.number_of_nights, ' days')
            ),
            new_checkout_date > models.Booking.check_in_date
            
        )
    ).scalars().first():
        return False, 'For the given check-in date, the unit is already occupied'

    return True, 'OK'
