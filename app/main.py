from fastapi import FastAPI

from app.employees.router import router as employees_router
from app.logging_config import configure_logging

configure_logging()

app = FastAPI()

app.include_router(employees_router)
