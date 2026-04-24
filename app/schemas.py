import datetime

from pydantic import BaseModel, ConfigDict


class BookingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    guest_name: str
    unit_id: str
    check_in_date: datetime.date
    number_of_nights: int
    
class ExtendStay(BaseModel):
    number_of_nights: int
