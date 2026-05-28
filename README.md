# Employee Service

## Overview
This is a project that fetches employee data from an upstream server, stores them in local db and exposes them via an API.

## Tech stack
Poetry for package management
Python version 3.12
Alembic for db migrations
pytest for testing
Ruff for lint + format (Black is obsolete because Ruff can do both things now)
Mypy for type checking

## Setup

### Prerequisites
This project uses Python 3.12 and assumes Poetry is already installed.

### Environment variables
Copy the .env.example file into .env and replace the environment variables with your own.
The following variables are related to the upstream server for authentication.
```
EMPLOYEE_API_BASE_URL=http://localhost:8001
EMPLOYEE_API_CLIENT_ID=your-client-id
EMPLOYEE_API_CLIENT_SECRET=your-client-secret
EMPLOYEE_API_USERNAME=your-username
EMPLOYEE_API_PASSWORD=your-password
EMPLOYEE_API_GRANT_TYPE=password
AUTH_HEADER_NAME=Access-Token
```

These are for DB configuration in our app. We need the first async url for 
usage by FastAPI and we need the sync url for the db migrations.
The last variable is to configure the log level.
```
# Database
DATABASE_URL=sqlite+aiosqlite:///./dev.db
DATABASE_URL_SYNC=sqlite:///./dev.db

# Logging
LOG_LEVEL=INFO
```

### Install
Installs all dependencies, and applies db migrations.

`make install`

### Run
Starts our employee service

`make run` 

### Run server
Starts a sample upstream server, if you don't have a separate one configured.

`make run-server`

### Fetch employees data
This command will pull employee data from upstream server and store them in local db.

`make fetch`

### Run tests
Runs all tests

`make test`

### Start via Docker
Builds and starts the app via docker on port 8000

`make docker`

## Database
We use a local SQLite database with Alembic migrations. 
Currently we have one table called 'employees'.
The database operations are performed using the SQLAlchemy ORM.


## How it works
The application performs two major functions.
1. Fetch and store employees data from an upstream server
2. Expose the stored employees data via 

### Assumptions
#### Data is within size limits

The full employee data is within the size limit to fit in a single HTTP response.
If it wasn't, we would implement a streaming response, but since we have the offset and limit parameters
an api client can pull data in multiple steps.

#### Fetch can be run multiple times

When fetching employees from upstream we are performing upsert based on the employee id, so the command is safe
to be run multiple times.


#### Our e2e test mocks the http endpoint
We have one e2e test that performs the full flow of fetch -> store -> get. It is a 'trully' e2e because 
it is testing the full flow within our app, but it does not depend on a real upstream server, because that
would make it harder to test and dependent on a separate service that we don't necesarily control.

## Sample output data
We have `employees.json` and `employees.csv` in the /outputs folder.