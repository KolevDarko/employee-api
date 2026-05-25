from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl


class UpstreamEmployee(BaseModel):
    """Raw shape returned by the upstream server API."""

    id: str
    date_of_birth: str
    image: str
    email: str
    first_name: str
    last_name: str
    title: str
    address: str
    country: str
    bio: str
    rating: str


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
