from fastapi import FastAPI

from app.lib.fetch_employees import fetch_employees

app = FastAPI()

app.include_router()
