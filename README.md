# MV Integra API

A Python FastAPI application designed to integrate with the MV system (Oracle SQL DB) using raw SQL queries.

## Project Structure
- `app/main.py`: Application entry point.
- `app/dependencies.py`: Database connection dependency using `oracledb`.
- `app/routers/`: API route definitions.
- `app/core/`: Configuration and logging.
- `app/schemas/`: Pydantic models.

## Requirements
- Python 3.8+
- Oracle Database (connection via `oracledb` thin mode)

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mv-integra
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration:**
   Copy `.env.example` to `.env` and fill in your Oracle DB credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual `DB_USER`, `DB_PASSWORD`, and `DB_DSN`.

## Running the Application

### Option 1: Local Development
Start the server using `uvicorn`:
```bash
uvicorn app.main:app --reload
```

### Option 2: Docker
Build and run with Docker Compose:
```bash
# Build and start the application
docker-compose up --build

# Or run in background
docker-compose up -d --build

# Stop the application
docker-compose down
```

The API will be available at `http://localhost:8000`.

## Documentation

Interactive API documentation (Swagger UI) is available at:
`http://localhost:8000/docs`

## Usage

### Test Connection
`GET /mv/test-connection`
Returns a status if the database connection is successful.

### Example Query
`GET /mv/example-query`
Executes a sample raw SQL query context.

## Logging

Logs are output to standard output (console), suitable for containerized environments. Log level can be set in `.env` (e.g., `LOG_LEVEL=DEBUG`).
