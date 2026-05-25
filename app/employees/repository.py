from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.employees.models import EmployeeRow


async def get_all(session: AsyncSession) -> list[EmployeeRow]:
    result = await session.scalars(select(EmployeeRow))
    return list(result.all())


async def upsert_many(session: AsyncSession, employees: list[EmployeeRow]) -> None:
    if not employees:
        return
    rows = [
        {c.key: getattr(emp, c.key) for c in EmployeeRow.__table__.columns}
        for emp in employees
    ]
    columns_to_update = [c.key for c in EmployeeRow.__table__.columns if c.key != "id"]
    stmt = insert(EmployeeRow).values(rows).on_conflict_do_update(
        index_elements=["id"],
        set_={c: insert(EmployeeRow).excluded[c] for c in columns_to_update},
    )
    await session.execute(stmt)
    await session.commit()
