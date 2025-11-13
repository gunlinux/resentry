# Resentry Database Models Documentation

## Overview
This document provides comprehensive documentation for all database models in the Resentry application. These models define the structure of data stored in the database and are implemented using SQLAlchemy ORM.

## Base Model
All models inherit from the `Base` class provided by SQLAlchemy's `declarative_base()`. This base class provides common functionality and ensures proper table creation and management.

## Model Details

### User Model
**Table Name:** `users`

The User model represents application users, primarily for managing user accounts and notifications.

**Fields:**
- `id` (Integer, Primary Key, Indexed)
  - Unique identifier for the user
  - Auto-incremented integer value
  - Primary key for the table
  - Indexed for faster lookups

- `name` (String, Indexed)
  - Name of the user
  - String field with variable length
  - Indexed for faster lookups

- `telegram_chat_id` (String, Nullable)
  - Telegram chat ID for the user
  - String field with variable length
  - Nullable - can be left empty if user doesn't have Telegram integration
  - Used for sending notifications to users via Telegram

**Usage:**
- Manages user accounts within the application
- Facilitates communication with users via Telegram (if configured)

---

### Project Model
**Table Name:** `projects`

The Project model represents software projects that send Sentry events to this Resentry instance.

**Fields:**
- `id` (Integer, Primary Key, Indexed)
  - Unique identifier for the project
  - Auto-incremented integer value
  - Primary key for the table
  - Indexed for faster lookups

- `name` (String, Indexed)
  - Name of the project
  - String field with variable length
  - Indexed for faster lookups

- `lang` (String, Indexed)
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
- `id` (Integer, Primary Key, Indexed)
  - Unique identifier for the envelope
  - Auto-incremented integer value
  - Primary key for the table
  - Indexed for faster lookups

- `project_id` (Integer, Foreign Key to `projects.id`)
  - Reference to the project this envelope belongs to
  - Establishes the relationship with the Project model
  - Required field (not nullable)

- `payload` (LargeBinary)
  - Raw envelope data in binary format
  - Stores the complete envelope data as received from Sentry SDK
  - LargeBinary type to accommodate potentially large payloads

- `event_id` (String, Nullable)
  - Event ID from the envelope headers
  - String field with variable length
  - Nullable - may not always be present in the envelope
  - Contains the unique event identifier from Sentry

- `sent_at` (DateTime, Nullable)
  - Timestamp when the envelope was sent
  - DateTime field storing the time of envelope submission
  - Nullable - may not always be present in the envelope
  - Used for tracking when events occurred

- `dsn` (String, Nullable)
  - DSN (Data Source Name) from the envelope headers
  - String field with variable length
  - Nullable - may not always be present in the envelope
  - Contains the DSN that was used to send the envelope

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
- `id` (Integer, Primary Key, Indexed)
  - Unique identifier for the envelope item
  - Auto-incremented integer value
  - Primary key for the table
  - Indexed for faster lookups

- `event_id` (Integer, Foreign Key to `envelopes.id`)
  - Reference to the envelope this item belongs to
  - Establishes the relationship with the Envelope model
  - Required field (not nullable)

- `item_id` (String, Indexed)
  - ID of the specific item within the envelope
  - String field with variable length
  - Indexed for faster lookups
  - Represents the identifier for this particular item in the envelope

- `payload` (LargeBinary)
  - Raw item payload data in binary format
  - Stores the complete item data as part of the envelope
  - LargeBinary type to accommodate potentially large payloads

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
The models are designed to work with multiple database backends supported by SQLAlchemy, with the default configuration using:
- Async operations with `asyncpg` for PostgreSQL
- SQLite with `aiosqlite` for development/testing
- Can be configured for other databases via the `DATABASE_URL` setting

## Data Types
- **Integer:** Used for primary keys and foreign keys
- **String:** Used for text fields (name, telegram_chat_id, event_id, dsn, lang, item_id)
- **LargeBinary:** Used for storing raw payloads in binary format
- **DateTime:** Used for timestamp fields (sent_at)
- **Nullable fields:** Several fields can be NULL depending on the data received from Sentry

## Usage Considerations
- The payload fields (in both Envelope and EnvelopeItem) store binary data and should be handled carefully to avoid memory issues with large payloads
- The models support both sync and async database operations
- Foreign key constraints ensure referential integrity between related records