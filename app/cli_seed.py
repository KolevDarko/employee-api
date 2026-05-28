import asyncio

from tests.data.seed_employees import seed_employees_data

from app.db.session import AsyncSessionLocal
from app.employees import repository


async def run_seed_employees() -> None:
    async with AsyncSessionLocal() as session:
        await repository.upsert_many(session, seed_employees_data())


def main() -> None:
    asyncio.run(run_seed_employees())
    print("Employees seeded successfully")


if __name__ == "__main__":
    main()
