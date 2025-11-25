# Resentry API Routes Documentation

## Overview
This document provides a comprehensive overview of all API routes available in the Resentry application. Resentry is a Sentry-compatible envelope storage and processing system built with FastAPI.

## Base URL
All routes assume the base URL of your Resentry instance (e.g., `http://your-resentry-host/`).

## Authentication
The API now requires authentication using JWT Bearer tokens for specific endpoints. To access protected endpoints, you must include a valid access token in the Authorization header.

**Authorization Header Format:**
```
Authorization: Bearer <access_token>
```

Protected endpoints require a valid JWT token with a valid expiration time. The token must be properly signed with the server's secret key.

## Route Details

### Health Check Routes

#### GET `/health/`
Returns the health status of the application.

**Parameters:** None

**Response:**
```json
{
  "status": "OK"
}
```

**Response Model:** HealthCheck

---

### User Management Routes

All user management routes are prefixed with `/api/v1/users/`.

#### GET `/api/v1/users/`
Get all users.

**Authentication:** Required - Bearer token

**Parameters:** None

**Response:** List of User objects

**Response Model:** `List[User]`

#### POST `/api/v1/users/`
Create a new user.

**Authentication:** Required - Bearer token

**Parameters:** None

**Request Body:**
```json
{
  "name": "string",
  "telegram_chat_id": "string"
}
```

**Request Model:** UserCreate

**Response:** Created User object

**Response Model:** User

#### GET `/api/v1/users/{user_id}`
Get a specific user by ID.

**Authentication:** Required - Bearer token

**Path Parameters:**
- `user_id` (integer): The ID of the user to retrieve

**Response:** User object

**Response Model:** User

**Status Codes:**
- 404: User not found

#### PUT `/api/v1/users/{user_id}`
Update a specific user by ID.

**Authentication:** Required - Bearer token

**Path Parameters:**
- `user_id` (integer): The ID of the user to update

**Request Body:**
```json
{
  "name": "string",
  "telegram_chat_id": "string"
}
```

**Request Model:** UserUpdate

**Response:** Updated User object

**Response Model:** User

**Status Codes:**
- 404: User not found

#### DELETE `/api/v1/users/{user_id}`
Delete a specific user by ID.

**Authentication:** Required - Bearer token

**Path Parameters:**
- `user_id` (integer): The ID of the user to delete

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

**Status Codes:**
- 404: User not found

---

### Project Management Routes

All project management routes are prefixed with `/api/v1/projects/`.

#### GET `/api/v1/projects/`
Get all projects.

**Authentication:** Required - Bearer token

**Parameters:** None

**Response:** List of Project objects

**Response Model:** `List[Project]`

#### POST `/api/v1/projects/`
Create a new project.

**Authentication:** Required - Bearer token

**Parameters:** None

**Request Body:**
```json
{
  "name": "string",
  "lang": "string"
}
```

**Request Model:** ProjectCreate

**Response:** Created Project object

**Response Model:** Project

#### GET `/api/v1/projects/{project_id}`
Get a specific project by ID.

**Authentication:** Required - Bearer token

**Path Parameters:**
- `project_id` (integer): The ID of the project to retrieve

**Response:** Project object

**Response Model:** Project

**Status Codes:**
- 404: Project not found

#### PUT `/api/v1/projects/{project_id}`
Update a specific project by ID.

**Authentication:** Required - Bearer token

**Path Parameters:**
- `project_id` (integer): The ID of the project to update

**Request Body:**
```json
{
  "name": "string",
  "lang": "string"
}
```

**Request Model:** ProjectUpdate

**Response:** Updated Project object

**Response Model:** Project

**Status Codes:**
- 404: Project not found

#### DELETE `/api/v1/projects/{project_id}`
Delete a specific project by ID.

**Authentication:** Required - Bearer token

**Path Parameters:**
- `project_id` (integer): The ID of the project to delete

**Response:**
```json
{
  "message": "Project deleted successfully"
}
```

**Status Codes:**
- 404: Project not found

---

### Envelope Processing Routes

All envelope processing routes are prefixed with `/api/v1/` (except where noted).

#### POST `/api/v1/{project_id}/envelope/`
Store a Sentry envelope for a specific project. This is the main endpoint that Sentry SDKs would send data to.

**Path Parameters:**
- `project_id` (integer): The ID of the project to store the envelope for

**Headers:**
- `Content-Encoding`: (Optional) For compressed envelopes (e.g., gzip, br)

**Request Body:**
Raw Sentry envelope data in the format expected by Sentry (multiple JSON lines with headers and payload).

**Response:**
```json
{
  "message": "Envelope stored successfully",
  "envelope_id": 123
}
```

**Status Codes:**
- 200: Success
- 400: Invalid envelope format
- 404: Project not found

#### GET `/api/v1/projects/events`
Get all envelope events from all projects.

**Authentication:** Required - Bearer token

**Parameters:** None

**Response:** List of Envelope objects

**Response Model:** `List[Envelope]`

#### GET `/api/projects/events`
Alternative endpoint to get all envelope events from all projects.

**Authentication:** Required - Bearer token

**Parameters:** None

**Response:** List of Envelope object

**Response Model:** `List[Envelope]`

---

### Authentication Routes

All authentication routes are prefixed with `/api/v1/auth/`.

#### POST `/api/v1/auth/login`
Authenticate a user and return JWT tokens.

**Parameters:** None

**Request Body:**
```json
{
  "login": "string",
  "password": "string"
}
```

**Request Model:** LoginSchema

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string"
}
```

**Response Model:** TokenSchema

**Status Codes:**
- 200: Successful authentication
- 401: Invalid credentials

#### POST `/api/v1/auth/refresh_token`
Refresh an expired access token using a refresh token.

**Parameters:** None

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Request Model:** RefreshTokenSchema

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string"
}
```

**Response Model:** TokenSchema

**Status Codes:**
- 200: Token refreshed successfully
- 401: Invalid refresh token

---

## Schema Definitions

### Project
- `id` (integer): Unique identifier for the project
- `name` (string): Name of the project
- `lang` (string): Programming language of the project

### User
- `id` (integer): Unique identifier for the user
- `name` (string): Name of the user
- `telegram_chat_id` (string, optional): Telegram chat ID for the user
- `password` (string): Password for user authentication (hashed)

### LoginSchema
- `login` (string): User login identifier (typically username)
- `password` (string): User password for authentication

### RefreshTokenSchema
- `refresh_token` (string): Refresh token used to obtain new access token

### AccessTokenSchema
- `access_token` (string): JWT access token for API authentication

### TokenSchema
- `access_token` (string): JWT access token for API authentication
- `refresh_token` (string): Refresh token used to obtain new access token

### TokenPayload
- `user_id` (integer): ID of the authenticated user
- `exp` (datetime): Expiration time of the token

### Envelope
- `id` (integer): Unique identifier for the envelope
- `project_id` (integer): ID of the project this envelope belongs to
- `payload` (string): Base64 encoded payload of the envelope
- `event_id` (string, optional): Event ID from the envelope headers
- `sent_at` (string, optional): Timestamp when the envelope was sent
- `dsn` (string, optional): DSN from the envelope headers

---

## Error Responses

Common error responses include:
- 404: Resource not found (with detail message)
- 400: Bad request (with detail message)

Example error response:
```json
{
  "detail": "Project not found"
}
```