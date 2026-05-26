import uuid
from datetime import UTC, datetime

from faker import Faker

from app.employees.models import EmployeeRow

fake = Faker()


def make_employee(**overrides: dict) -> EmployeeRow:
    defaults = {
        "id": str(uuid.uuid4()),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=75),
        "image": fake.image_url(),
        "email": fake.unique.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "title": fake.job(),
        "address": fake.address(),
        "country": "USA",
        "bio": fake.text(max_nb_chars=200),
        "rating": fake.pyfloat(min_value=1, max_value=5, right_digits=1),
        "fetched_at": datetime.now(UTC),
    }
    return EmployeeRow(**{**defaults, **overrides})
