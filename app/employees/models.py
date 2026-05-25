from app.db.base import Base
from sqlalchemy import String, Date, Float, Column, DateTime, func


class EmployeeRow(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True)
    date_of_birth = Column(Date)
    image = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    title = Column(String)
    address = Column(String)
    country = Column(String)
    bio = Column(String)
    rating = Column(Float)
    fetched_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

