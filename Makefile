.PHONY: run test lint fetch docker

lint:
	poetry run ruff check .
	poetry run ruff format --check .
	poetry run mypy .

test:
	poetry run pytest -v

fetch:
	poetry run fetch-employees

run-server:
	poetry run uvicorn server.main:app --host 0.0.0.0 --port 8001

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker:
	docker build -t rumble-test .
	docker run --env-file .env -p 8000:8000 rumble-test
