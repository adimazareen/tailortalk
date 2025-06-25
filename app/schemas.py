from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentRequest(BaseModel):
    """Request for booking an appointment"""
    user_input: str
    intent: Optional[str] = None
    date: Optional[str] = None
    time_range: Optional[str] = None
    duration: Optional[int] = None  # in minutes

    class Config:
        extra = "forbid"  # Prevent extra fields
        schema_extra = {
            "example": {
                "user_input": "Book a meeting tomorrow afternoon",
                "intent": "book_appointment",
                "date": "2023-12-01",
                "time_range": "13:00-17:00",
                "duration": 30
            }
        }

class AppointmentSlot(BaseModel):
    """Available time slot for an appointment"""
    start_time: datetime
    end_time: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConfirmedAppointment(BaseModel):
    """Confirmed appointment details"""
    summary: str
    start_time: datetime
    end_time: datetime
    confirmation_link: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%A, %B %d at %I:%M %p")
        }