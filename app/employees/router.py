from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.employees.schemas import EmployeeRead, EmployeeFilters
from app.employees.repository import get_filtered_employees, get_by_id
from app.db.session import get_session
from app.utils.http_utils import json_or_csv_response

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/")
async def get_employees(
    session: AsyncSession = Depends(get_session),
    filters: EmployeeFilters = Depends(),
):
    employees = await get_filtered_employees(session, filters)
    readable = [EmployeeRead.model_validate(e) for e in employees]
    return json_or_csv_response(readable, filters.format)

@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(employee_id: str, session: AsyncSession = Depends(get_session)) -> EmployeeRead:
    employee = await get_by_id(session, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee
