from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.employees.router import router as employees_router
from app.logging_config import configure_logging

configure_logging()

app = FastAPI()

app.include_router(employees_router)

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/", response_class=HTMLResponse)
async def root():
    return (STATIC_DIR / "index.html").read_text()
