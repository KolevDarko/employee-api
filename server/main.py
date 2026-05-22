from fastapi import Depends, FastAPI

from server.middleware import verify_token
from server.routers import auth, employee

app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(employee.router, prefix="/api", dependencies=[Depends(verify_token)])
