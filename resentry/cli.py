"""Command line interface for Resentry application"""

import asyncio
import sys
from typing import Optional
import argparse
import getpass

from resentry.main import create_app
from resentry.config import settings
from resentry.core.hashing import Hasher
from resentry.database.database import create_db_and_tables
from resentry.database.schemas.user import UserCreate
from resentry.usecases.user import CreateUser
from resentry.repos.user import UserRepository


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the Resentry server"""
    import uvicorn

    app = create_app()

    if reload:
        uvicorn.run(app, host=host, port=port, reload=True)
    else:
        uvicorn.run(app, host=host, port=port, reload=False)


async def add_user_async(username: str, password: Optional[str] = None):
    """Add a new user to the database asynchronously using usecase"""
    # Get password from user if not provided
    if password is None:
        password = getpass.getpass("Enter password: ")

    # Initialize database tables if they don't exist
    await create_db_and_tables()

    # Create the hasher
    from resentry.database.database import create_async_session

    hasher = Hasher(
        settings.SALT.encode() if isinstance(settings.SALT, str) else settings.SALT
    )

    async with create_async_session() as session:
        # Create repository
        user_repo = UserRepository(session)

        # Check if user already exists
        existing_user = await user_repo.get_by_name(username)
        if existing_user:
            print(f"Error: User '{username}' already exists.")
            return False

        # If user doesn't exist, create the new user
        # Create usecase
        create_user = CreateUser(user_repo, hasher)

        # Prepare user data
        user_data = UserCreate(name=username, password=password)

        # Create new user using the usecase
        try:
            user = await create_user.execute(user_data)
            await session.commit()  # Explicitly commit the transaction
            print(f"User '{user.name}' created successfully.")
            return True
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            await session.rollback()
            return False


def add_user(username: str, password: Optional[str] = None):
    """Add a new user to the database"""
    return asyncio.run(add_user_async(username, password))


def main():
    parser = argparse.ArgumentParser(description="Resentry CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Runserver command
    runserver_parser = subparsers.add_parser(
        "runserver", help="Run the Resentry server"
    )
    runserver_parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to run the server on"
    )
    runserver_parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    runserver_parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload"
    )

    # Add-user command
    adduser_parser = subparsers.add_parser("add-user", help="Add a new user")
    adduser_parser.add_argument("username", type=str, help="Username for the new user")
    adduser_parser.add_argument(
        "--password",
        type=str,
        help="Password for the new user (optional, will prompt if not provided)",
    )

    # Parse arguments
    args = parser.parse_args()

    if args.command == "runserver":
        run_server(host=args.host, port=args.port, reload=args.reload)
    elif args.command == "add-user":
        success = add_user(args.username, args.password)
        if not success:
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
