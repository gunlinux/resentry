# Resentry - Sentry Envelope Storage and Processing System

## Project Overview

Resentry is a FastAPI-based web application that serves as a Sentry-compatible envelope storage and processing system. It receives Sentry envelopes (collections of error events and related data) via HTTP requests, parses them, and stores them in a database for later analysis. This project acts as a self-hosted alternative to Sentry's official service for capturing and storing error events.

### Core Technologies
- **Framework**: FastAPI (Python web framework with built-in API documentation)
- **Database**: SQLAlchemy ORM with async support for multiple database backends (defaults to SQLite)
- **Serialization**: Pydantic for data validation and serialization
- **Package Management**: uv (Python package manager)
- **Compression Support**: gzip and brotli for envelope compression handling
- **Async Operations**: Full async/await support for improved performance

### Architecture

The application follows a standard FastAPI structure with:

- **API Layer**: Async REST endpoints in `/resentry/api/v1/` for handling different resources
- **Database Layer**: Async SQLAlchemy models and schemas in `/resentry/database/`
- **Business Logic**: Sentry envelope processing in `/resentry/sentry.py` with async support
- **Configuration**: Settings management via Pydantic Settings in `/resentry/config.py`

### Key Components

#### Envelope Processing
- The core functionality is in `/resentry/sentry.py` which handles Sentry envelope parsing with async support
- Supports compressed envelopes (gzip, brotli) with async decompression
- Extracts event items, transactions, and other Sentry data types
- Stores raw envelope data in the database for later processing
- Uses async helper functions for JSON parsing and data handling

#### Database Models
- **Project**: Represents a project that can send Sentry events
- **Envelope**: Stores the complete Sentry envelope with its raw payload
- **EnvelopeItem**: Individual items within an envelope (events, transactions, etc.)

#### API Endpoints
- **Health check**: `/health/` - Basic health status
- **Projects**: `/api/v1/projects/` - CRUD operations for projects
- **Envelopes**: `/api/v1/{project_id}/envelope/` - Receive and store Sentry envelopes
- **Events**: `/api/projects/events` - Retrieve all stored events

## Building and Running

### Prerequisites
- Python 3.11 or higher
- uv package manager (https://github.com/astral-sh/uv)

### Setup Instructions

1. **Install dependencies**:
   ```bash
   make install
   # Or alternatively:
   uv sync
   ```

2. **Run development server**:
   ```bash
   # Using the run-dev script from pyproject.toml:
   uv run run-dev
   
   # Or directly:
   uvicorn resentry.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Run production server**:
   ```bash
   # Using the run-prod script from pyproject.toml:
   uv run run-prod
   
   # Or directly:
   uvicorn resentry.main:app --host 0.0.0.0 --port 8000
   ```

4. **Initialize database** (if needed):
   ```bash
   python init_db.py
   ```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
DATABASE_URL=sqlite+aiosqlite:///./resentry.db  # Default SQLite database
SECRET_KEY=your-secret-key-here  # Secret key for security purposes
ALGORITHM=HS256  # Algorithm for JWT tokens
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Token expiration time
```

## Testing

### Run Tests
```bash
# Run all tests
make test

# Run tests with verbose output and print statements
make test-dev

# Or directly with pytest:
uv run pytest
uv run pytest -vv -s  # With verbose output
```

### Test Structure
- Tests are located in the `/tests/` directory
- Uses pytest with TestClient for API testing
- Each test file corresponds to an API module
- Uses in-memory SQLite database for isolated test runs

## Development Conventions

### Code Style
- Formatting: Ruff (with Black-like formatting)
- Type checking: Pyright
- Linting: Ruff

### Run Code Quality Checks
```bash
# Check formatting and linting
make lint
```

### Package Management
- Dependencies are managed via `uv` and `pyproject.toml`
- Lock file: `uv.lock`
- Development dependencies are specified in the `[project.optional-dependencies].dev` section

### API Documentation
- Interactive API documentation is automatically available at `/docs` when the server is running
- Alternative API documentation at `/redoc`

## Key Features

1. **Sentry Compatibility**: Accepts Sentry envelopes in the same format as official Sentry
2. **Multiple Compression Support**: Handles both gzip and brotli compressed envelopes
3. **Project Management**: CRUD operations for projects that send events
4. **Database Storage**: Persistent storage of Sentry envelopes with event metadata
5. **RESTful API**: Standard REST endpoints for all operations
6. **Full Async Support**: Complete async/await implementation for improved performance and scalability
7. **Environment Configuration**: Environment variable-based configuration

## Integration with Sentry SDK

To use Resentry with Sentry SDKs, configure the DSN in your client applications to point to your Resentry instance with the project ID:

```
http://<resentry-host>/api/v1/<project_id>/envelope/
```

## Async Architecture

The application uses an asynchronous architecture throughout to maximize performance and scalability:

- **Async Dependency Injection**: Uses `AsyncSession` for database connections with proper lifecycle management
- **Async Database Queries**: All database operations use `async/await` pattern with SQLAlchemy's async methods
- **Async Request Handling**: HTTP request processing is fully asynchronous from reception to database storage
- **Async Utility Functions**: Helper functions for JSON parsing, compression, and data handling execute asynchronously using thread pools
- **Async Testing**: Test configuration supports async database operations for more accurate testing

## Project Structure

```
resentry/
├── resentry/
│   ├── api/              # API endpoints and routers
│   │   ├── deps.py       # Async dependency injection
│   │   ├── health.py     # Health check endpoint
│   │   └── v1/           # Version 1 API endpoints
│   ├── database/         # Database models, schemas and connections
│   ├── utils/            # Utility functions (JSON parsing, compression, etc.)
│   │   └── helpers.py    # Async helper functions
│   ├── config.py         # Configuration settings
│   ├── main.py           # Main FastAPI application
│   └── sentry.py         # Sentry envelope parsing logic with async support
├── tests/                # Test files
├── pyproject.toml        # Project dependencies and configuration
├── uv.lock               # Dependency lock file
├── Makefile              # Build commands
├── init_db.py            # Database initialization script
└── .env                  # Environment variables (not in repo)
```

## Database Schema

The database contains three main tables:
- `projects`: Information about projects that send Sentry events
- `envelopes`: Raw Sentry envelope data with metadata
- `envelope_items`: Individual items within each envelope (events, transactions, etc.)

## Qwen Added Memories
- /home/loki/qwen/python.md
- docs/models.md
- docs/routes.md


## Memory

- On routes changes - update routes.md
- On models change - update models.md
- Refresh memory after it

