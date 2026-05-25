from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl, field_validator


class UpstreamEmployee(BaseModel):
    """Raw shape returned by the upstream server API."""

    id: str
    date_of_birth: date
    image: str
    email: EmailStr
    first_name: str
    last_name: str
    title: str
    address: str
    country: str
    bio: str
    rating: float

    @field_validator("date_of_birth")
    def validate_date_of_birth(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class EmployeeRead(BaseModel):
    """Shape served by this app's API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    date_of_birth: date
    image: HttpUrl
    email: EmailStr
    first_name: str
    last_name: str
    title: str
    address: str
    country: str
    bio: str
    rating: float
