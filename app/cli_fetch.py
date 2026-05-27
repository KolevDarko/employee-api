import asyncio

from app.db.session import AsyncSessionLocal
from app.employees.service import fetch_and_store_employees


async def run_fetch_employees() -> None:
    async with AsyncSessionLocal() as session:
        await fetch_and_store_employees(session)


def main() -> None:
    asyncio.run(run_fetch_employees())
    print("Employees fetched and stored successfully")


if __name__ == "__main__":
    main()
