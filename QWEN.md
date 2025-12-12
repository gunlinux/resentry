# Resentry - Sentry Envelope Storage and Processing System

## Project Overview

Resentry is a FastAPI-based web application that serves as a Sentry-compatible envelope storage and processing system. It receives Sentry envelopes (collections of error events and related data) via HTTP requests, parses them, and stores them in a database for later analysis. This project acts as a self-hosted alternative to Sentry's official service for capturing and storing error events.

### Core Technologies
- **Framework**: FastAPI (Python web framework with built-in API documentation)
- **Database**: SQLModel ORM (combines SQLAlchemy ORM with Pydantic features) with async support for multiple database backends (defaults to SQLite)
- **Serialization**: Pydantic for data validation and serialization
- **Authentication**: PyJWT for secure token-based authentication and bcrypt for password hashing
- **Package Management**: uv (Python package manager)
- **Compression Support**: gzip and brotli for envelope compression handling
- **Database Migrations**: Alembic for schema migration management
- **Async Operations**: Full async/await support for improved performance
- **Web Server**: Granian (Rust-based ASGI server) for high-performance serving

### Architecture

The application follows a modular architecture pattern with separation of concerns across different layers:

- **API Layer**: Async REST endpoints in `/resentry/api/v1/` for handling different resources
- **Database Layer**: Async SQLAlchemy models and schemas in `/resentry/database/`
- **Repository Layer**: Data access patterns in `/resentry/repos/` for database operations
- **Use Cases Layer**: Business logic implementations in `/resentry/usecases/` for specific application functionality
- **Domain Layer**: Domain entities and business rules in `/resentry/domain/` (e.g., Event, LogLevel)
- **Infrastructure Layer**: External service integrations in `/resentry/infra/` (e.g., Telegram service)
- **Core Layer**: Core functionality like password hashing, dependency injection, and event processing in `/resentry/core/`
- **Business Logic**: Additional core functionality in `/resentry/sentry.py` with synchronous support
- **Configuration**: Settings management via Pydantic Settings in `/resentry/config.py`

### Key Components

#### Domain Layer
- **Event System**: Defines domain entities like `Event` and `LogLevel` in `/resentry/domain/queue.py`
- **Event Model**: Represents application events with properties like level, project, payload, and associated users
- **Log Levels**: Enum defining different log levels (critical, error, warning, info, debug, etc.)

#### Infrastructure Layer
- **Notification Services**: Handles external integrations like Telegram notifications in `/resentry/infra/telegram.py`
- **Telegram Service**: Implements Telegram bot API integration for sending notifications
- **External Communication**: Manages communication with external services such as messaging platforms

#### Envelope Processing
- The core functionality is in `/resentry/sentry.py` which handles Sentry envelope parsing synchronously
- Supports compressed envelopes (gzip, brotli) with synchronous decompression
- Extracts event items, transactions, and other Sentry data types
- Stores raw envelope data in the database for later processing
- Uses synchronous helper functions for JSON parsing and data handling

#### Event Processing and Notifications
- **Event Worker**: Asynchronous event processor that handles different log levels in `/resentry/core/events.py`
- **Notification System**: Sends notifications to users via registered handlers (currently Telegram)
- **Event Registration**: Allows registering different actions for different event levels (e.g., send Telegram message on error)
- **Dependency Injection**: Uses fastapi-injectable for managing dependencies in event processing

#### Repository Layer
- **Base Repository**: Generic repository pattern in `/resentry/repos/base.py` for common database operations
- **Project Repository**: Project-specific database operations in `/resentry/repos/project.py`
- **Envelope Repository**: Envelope-specific database operations in `/resentry/repos/envelope.py`
- **User Repository**: User-specific database operations in `/resentry/repos/user.py`, including `get_by_name` method for authentication
- Provides a clean abstraction over direct database access with proper async session management

#### Use Case Layer
- **Project Use Cases**: Business logic for project management in `/resentry/usecases/project.py`
- **Envelope Use Cases**: Business logic for envelope processing in `/resentry/usecases/envelope.py` (now uses synchronous envelope parsing)
- **Authentication Use Cases**: Business logic for authentication in `/resentry/usecases/auth.py`, including Login and RefreshToken functionality
- Contains the core business rules and application-specific logic separated from API layer concerns

#### Database Models
- **Project**: Represents a project that can send Sentry events
- **Envelope**: Stores the complete Sentry envelope with its raw payload
- **EnvelopeItem**: Individual items within an envelope (events, transactions, etc.)
- **User**: Represents application users, primarily for notifications

#### API Endpoints
- **Health check**: `/health/` - Basic health status
- **Users**: `/api/v1/users/` - CRUD operations for users
- **User by ID**: `/api/v1/users/{user_id}` - Get, update, or delete a specific user
- **Projects**: `/api/v1/projects/` - CRUD operations for projects
- **Project by ID**: `/api/v1/projects/{project_id}` - Get, update, or delete a specific project
- **Authentication**: `/api/v1/auth/` - JWT-based authentication including `/login` and `/refresh_token` endpoints
- **Envelopes**: `/api/v1/{project_id}/envelope/` - Receive and store Sentry envelopes (requires authentication via X-Sentry-Auth header)
- **Events**: `/api/projects/events` - Retrieve all stored events
- **Events Alternative**: `/api/v1/projects/events` - Alternative endpoint to retrieve all stored events
- **Project Events**: `/api/v1/projects/events` - Retrieve all stored events (v1 endpoint with authentication)

## Building and Running

### Prerequisites
- Python 3.13 or higher
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
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Access token expiration time
REFRESH_TOKEN_EXPIRE_MINUTES=10080  # Refresh token expiration time (7 days: 60*24*7)
SALT=$2b$12$gj7lkAtmwGLm8W8Wg50h6.  # Salt for password hashing
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
7. **JWT Authentication**: Secure authentication system with login and token refresh functionality
8. **Environment Configuration**: Environment variable-based configuration
9. **Event-Driven Notifications**: Support for sending notifications via registered handlers (e.g., Telegram)
10. **Command-Line Interface**: Built-in CLI for managing users, projects, and interacting with the API
11. **Client Module**: Python client library for programmatic access to the API
12. **Dependency Injection**: FastAPI integration with fastapi-injectable for managing dependencies

## Command-Line Interface

The application includes a command-line interface with the following commands:

### Server Management
- `resentry runserver`: Run the Resentry server
  - Options: `--host`, `--port`, `--reload`
  - Example: `uv run resentry runserver --port 8080 --reload`

### User Management
- `resentry add-user <username>`: Add a new user to the database
  - Option: `--password` (optional, will prompt if not provided)
  - Example: `uv run resentry add-user admin --password mypassword`

### Client CLI
- `python -m client`: Command-line interface for interacting with the Resentry API
  - `health`: Check API health status
  - `login`: Authenticate with API using username and password
  - `user list`: List all users
  - `user get-user <user_id>`: Get user by ID
  - `user create-user`: Create a new user
  - `user update-user <user_id>`: Update a user
  - `user delete <user_id>`: Delete a user
  - `project list`: List all projects
  - `project get <project_id>`: Get project by ID
  - `project create`: Create a new project
  - `project update <project_id>`: Update a project
  - `project delete-project <project_id>`: Delete a project
  - `events list <project_id>`: List all events for a project

## Notification System

The application includes a notification system with Telegram integration:

- **User Notification Setup**: Users can have Telegram chat IDs stored in their profile for receiving notifications
- **Event-Based Notifications**: The system sends notifications when specific events occur, such as error logs
- **Telegram Service**: Built-in Telegram bot API integration for sending messages to users
- **Event Registration**: Different event types (critical, error, warning, etc.) can be bound to notification handlers
- **Asynchronous Processing**: Notification sending happens asynchronously using an event queue system
- **Extensible Architecture**: The event system allows for easy addition of other notification methods

## Integration with Sentry SDK

To use Resentry with Sentry SDKs, configure the DSN in your client applications to point to your Resentry instance with the project ID:

```
http://<resentry-host>/api/v1/<project_id>/envelope/
```

## Synchronous Architecture

The application now uses a synchronous architecture for envelope processing to simplify operations and improve performance:

- **Sync Dependency Injection**: Uses `AsyncSession` for database connections with proper lifecycle management
- **Async Database Queries**: All database operations use `async/await` pattern with SQLAlchemy's async methods
- **Sync Request Handling**: HTTP request processing for envelope parsing is synchronous from reception to database storage
- **Async Repository Layer**: Async data access patterns in repository classes for clean separation of concerns
- **Async Use Case Layer**: Business logic implemented with async/await for long-running operations
- **Sync Utility Functions**: Helper functions for JSON parsing, compression, and data handling execute synchronously
- **Async Testing**: Test configuration supports async database operations for more accurate testing

## Event Handling and Notification Architecture

The application includes an event-driven notification system:

- **Event Loop**: Asynchronous event loop in the application lifespan that processes events from a queue
- **Event Worker**: `EventWorker` class manages different event types and registered handlers
- **Notification System**: Supports registering different notification handlers for various log levels
- **Telegram Integration**: Built-in Telegram integration for sending notifications to users
- **Dependency Injection**: Uses `fastapi-injectable` for managing dependencies in event processing
- **Queue System**: Implements an asyncio.Queue for handling events asynchronously
- **Lifespan Management**: Event worker is initialized during application startup and cleaned up on shutdown

## Project Structure

```
resentry/
├── alembic/              # Database migration files
├── client/               # Client command-line interface and API client
│   ├── api_client.py     # Client for interacting with Resentry API
│   ├── cli.py            # Command-line interface implementation
│   ├── config.py         # Client configuration
│   ├── http_client.py    # HTTP client utilities
│   ├── models.py         # Client data models
│   └── test_client.py    # Client testing utilities
├── docs/                 # Documentation files
├── resentry/             # Main application package
│   ├── api/              # API endpoints and routers
│   │   ├── deps.py       # Async dependency injection
│   │   ├── health.py     # Health check endpoint
│   │   └── v1/           # Version 1 API endpoints
│   │       ├── auth.py   # Authentication endpoints (login, refresh token)
│   │       ├── envelopes.py # Envelope processing endpoints
│   │       ├── projects.py  # Project management endpoints
│   │       ├── users.py     # User management endpoints
│   │       └── router.py    # Main API router including auth routes
│   ├── core/             # Core functionality
│   │   ├── deps.py       # Dependency injection utilities
│   │   ├── events.py     # Event processing and notification handlers
│   │   └── hashing.py    # Password hashing utilities
│   ├── database/         # Database models, schemas and connections
│   │   ├── models/       # Database model definitions
│   │   │   ├── base.py   # Base model definitions
│   │   │   ├── envelope.py # Envelope model
│   │   │   ├── project.py  # Project model
│   │   │   └── user.py     # User model
│   │   ├── schemas/      # Pydantic schemas for API serialization
│   │   │   ├── auth.py     # Authentication-related schemas
│   │   │   ├── envelope.py # Envelope schemas
│   │   │   ├── project.py  # Project schemas
│   │   │   └── user.py     # User schemas
│   │   └── database.py     # Database connection setup
│   ├── domain/           # Domain entities and business rules
│   │   └── queue.py      # Event and LogLevel definitions
│   ├── infra/            # Infrastructure services
│   │   └── telegram.py   # Telegram notification service
│   ├── repos/            # Repository layer for database operations
│   │   ├── base.py       # Base repository
│   │   ├── envelope.py   # Envelope repository
│   │   ├── project.py    # Project repository
│   │   └── user.py       # User repository
│   ├── usecases/         # Business logic and use case implementations
│   │   ├── auth.py       # Authentication use cases (login, refresh token)
│   │   ├── envelope.py   # Envelope use cases
│   │   ├── project.py    # Project use cases
│   │   └── user.py       # User use cases
│   ├── utils/            # Utility functions (JSON parsing, compression, etc.)
│   │   └── helpers.py    # Synchronous helper functions
│   ├── cli.py            # Command-line interface entry point
│   ├── config.py         # Configuration settings
│   ├── main.py           # Main FastAPI application with event processing
│   └── sentry.py         # Sentry envelope parsing logic with synchronous support
├── tests/                # Test files
├── alembic.ini           # Alembic configuration
├── client.py             # Client command-line interface entry point
├── dev.py                # Development utilities
├── Makefile              # Build commands
├── pyproject.toml        # Project dependencies and configuration
└── uv.lock               # Dependency lock file
```

## Database Schema

The database contains four main tables:
- `projects`: Information about projects that send Sentry events
- `envelopes`: Raw Sentry envelope data with metadata
- `envelope_items`: Individual items within each envelope (events, transactions, etc.)
- `users`: Information about application users, primarily for notifications

## Database Migrations

The project uses Alembic for database migrations with SQLModel support:
- **Migration Configuration**: Located in `alembic.ini` and `alembic/env.py`
- **Migration Commands**:
  - `uv run alembic upgrade head` - Apply all pending migrations
  - `uv run alembic downgrade -1` - Revert the last migration
  - `uv run alembic revision --autogenerate -m "message"` - Create a new migration based on model changes
  - `uv run alembic current` - Show current revision
  - `uv run alembic history` - Show migration history
- **Initial Migration**: The initial migration (`23a1582e0e04_initial_database_schema.py`) creates all necessary tables with proper constraints and indexes

## Qwen Added Memories
- /home/loki/qwen/python.md
- docs/models.md
- docs/routes.md


## Documentation Files

- **docs/models.md**: Detailed documentation of database models and their relationships
- **docs/routes.md**: Comprehensive documentation of API routes and their functionality

## Memory

- On routes changes - update routes.md
- On models change - update models.md
- On database changes - update migration system
- Refresh memory after it


