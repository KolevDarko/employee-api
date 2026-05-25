from fastapi import FastAPI

from app.logging_config import configure_logging

configure_logging()

app = FastAPI()

app.include_router()
