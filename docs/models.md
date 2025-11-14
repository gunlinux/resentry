# Resentry Database Models Documentation

## Overview
This document provides comprehensive documentation for all database models in the Resentry application. These models define the structure of data stored in the database and are implemented using SQLModel, which combines SQLAlchemy ORM with Pydantic features for enhanced type safety and validation.

## Base Model
All models inherit from the `SQLModel` class with the `table=True` parameter. This provides common functionality combining SQLAlchemy's ORM capabilities with Pydantic's validation and serialization features, ensuring proper table creation and management.

## Model Details

### User Model
**Table Name:** `users`

The User model represents application users, primarily for managing user accounts and notifications.

**Fields:**
- `id` (int, Primary Key, Indexed)
  - Unique identifier for the user
  - Auto-incremented integer value
  - Primary key for the table
  - Indexed for faster lookups

- `name` (str, Indexed)
  - Name of the user
  - String field with variable length
  - Indexed for faster lookups

- `telegram_chat_id` (str | None)
  - Telegram chat ID for the user
  - String field with variable length
  - Optional - can be left empty if user doesn't have Telegram integration
  - Used for sending notifications to users via Telegram
  - Defaults to None

**Usage:**
- Manages user accounts within the application
- Facilitates communication with users via Telegram (if configured)

---

### Project Model
**Table Name:** `projects`

The Project model represents software projects that send Sentry events to this Resentry instance.

**Fields:**
- `id` (int, Primary Key, Indexed)
  - Unique identifier for the project
  - Auto-incremented integer value
  - Primary key for the table
  - Indexed for faster lookups

- `name` (str, Indexed)
  - Name of the project
  - String field with variable length
  - Indexed for faster lookups

- `lang` (str, Indexed)
  - Programming language of the project
  - String field with variable length
  - Indexed for faster lookups
  - Represents the language used in the project (e.g., "python", "javascript", "java")

**Usage:**
- Organizes Sentry events by project
- Allows for project-specific filtering and management
- Tracks the programming language of each project

---

### Envelope Model
**Table Name:** `envelopes`

The Envelope model stores Sentry envelopes received from client applications. Each envelope contains one or more events or other data items.

**Fields:**
- `id` (int, Primary Key, Indexed)
  - Unique identifier for the envelope
  - Auto-incremented integer value
  - Primary key for the table
  - Indexed for faster lookups

- `project_id` (int, Foreign Key to `projects.id`)
  - Reference to the project this envelope belongs to
  - Establishes the relationship with the Project model
  - Required field

- `payload` (bytes)
  - Raw envelope data in binary format
  - Stores the complete envelope data as received from Sentry SDK
  - Bytes type to accommodate binary payloads

- `event_id` (str | None)
  - Event ID from the envelope headers
  - String field with variable length
  - Optional - may not always be present in the envelope
  - Contains the unique event identifier from Sentry
  - Defaults to None

- `sent_at` (datetime | None)
  - Timestamp when the envelope was sent
  - DateTime field storing the time of envelope submission
  - Optional - may not always be present in the envelope
  - Used for tracking when events occurred
  - Defaults to None

- `dsn` (str | None)
  - DSN (Data Source Name) from the envelope headers
  - String field with variable length
  - Optional - may not always be present in the envelope
  - Contains the DSN that was used to send the envelope
  - Defaults to None

**Usage:**
- Stores raw Sentry envelopes for later processing
- Associates envelopes with specific projects
- Preserves envelope metadata for analysis
- Maintains the original payload for potential reprocessing

---

### EnvelopeItem Model
**Table Name:** `envelope_items`

The EnvelopeItem model represents individual items within a Sentry envelope. Each envelope can contain multiple items such as events, transactions, attachments, etc.

**Fields:**
- `id` (int, Primary Key, Indexed)
  - Unique identifier for the envelope item
  - Auto-incremented integer value
  - Primary key for the table
  - Indexed for faster lookups

- `event_id` (int, Foreign Key to `envelopes.id`)
  - Reference to the envelope this item belongs to
  - Establishes the relationship with the Envelope model
  - Required field

- `item_id` (str, Indexed)
  - ID of the specific item within the envelope
  - String field with variable length
  - Indexed for faster lookups
  - Represents the identifier for this particular item in the envelope

- `payload` (bytes)
  - Raw item payload data in binary format
  - Stores the complete item data as part of the envelope
  - Bytes type to accommodate binary payloads

**Usage:**
- Stores individual items that make up a Sentry envelope
- Enables detailed analysis of envelope contents
- Allows for separate processing of different item types within envelopes

---

## Model Relationships

### One-to-Many Relationships:

1. **Project ↔ Envelope**
   - One Project can have many Envelopes
   - Envelope has a foreign key `project_id` referencing Project.id
   - Implemented as: `Envelope.project_id` → `Project.id`

2. **Envelope ↔ EnvelopeItem**
   - One Envelope can have many EnvelopeItems
   - EnvelopeItem has a foreign key `event_id` referencing Envelope.id
   - Implemented as: `EnvelopeItem.event_id` → `Envelope.id`

### Relationship Diagram:
```
Project (1) ────< Envelope (Many)
                    │
                    └──< EnvelopeItem (Many)
```

## Indexes
Multiple fields across models are indexed to improve query performance:
- `id` fields are automatically indexed as primary keys
- `name` in User model (for faster user lookups)
- `name` and `lang` in Project model (for faster project filtering)
- `project_id` in Envelope model (foreign key optimization)
- `item_id` in EnvelopeItem model (for faster item lookups)
- `event_id` in EnvelopeItem model (foreign key optimization)

## Database Engine Support
The models are designed to work with multiple database backends supported by SQLModel/SQLAlchemy, with the default configuration using:
- Async operations with `asyncpg` for PostgreSQL
- SQLite with `aiosqlite` for development/testing
- Can be configured for other databases via the `DATABASE_URL` setting

## Data Types
- **int:** Used for primary keys and foreign keys
- **str:** Used for text fields (name, telegram_chat_id, event_id, dsn, lang, item_id)
- **bytes:** Used for storing raw payloads in binary format
- **datetime:** Used for timestamp fields (sent_at)
- **Optional types:** Several fields can be None using Union types (str | None)

## Usage Considerations
- The payload fields (in both Envelope and EnvelopeItem) store binary data and should be handled carefully to avoid memory issues with large payloads
- The models support both sync and async database operations through SQLModel's session management
- Foreign key constraints ensure referential integrity between related records
- Pydantic-style field definitions provide better type hints and validation