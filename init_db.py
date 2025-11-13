#!/usr/bin/env python3
"""
Database initialization script for Resentry
"""

import asyncio
from resentry.database.database import create_db_and_tables


async def init_db():
    print("Initializing database...")
    await create_db_and_tables()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
