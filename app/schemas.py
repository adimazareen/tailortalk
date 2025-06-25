from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentRequest(BaseModel):
    user_input: str
    intent: Optional[str] = None
    date: Optional[str] = None
    time_range: Optional[str] = None
    duration: Optional[int] = None  # in minutes

class AppointmentSlot(BaseModel):
    start_time: datetime
    end_time: datetime

class ConfirmedAppointment(BaseModel):
    summary: str
    start_time: datetime
    end_time: datetime
    confirmation_link: str