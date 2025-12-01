"""Command-line interface for Resentry API client."""

import json
import click
from dotenv import load_dotenv
from client.api_client import ResentryAPIClient
from client.config import Config
from client.models import UserCreate, UserUpdate, ProjectCreate, ProjectUpdate

load_dotenv()


@click.group()
@click.option("--api-url", default=None, help="Resentry API URL")
@click.pass_context
def cli(ctx, api_url):
    """Command-line interface for interacting with Resentry API."""
    # Load config from environment or override with CLI options
    config = Config()

    if api_url:
        config.api_url = api_url
    print(f"working with {config.api_url}")

    # Store the API client in the context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["client"] = ResentryAPIClient(config)


@cli.command()
def health():
    """Check API health."""
    client = click.get_current_context().obj["client"]
    try:
        result = client.health_check()
        click.echo(f"API Health: {result.status}")
    except Exception as e:
        click.echo(f"Error checking health: {e}")


@cli.command()
@click.argument("login")
@click.password_option()
def login(login, password):
    """Authenticate with the API."""
    client = click.get_current_context().obj["client"]
    try:
        tokens = client.login(login, password)
        click.echo("Login successful!")
        click.echo(f"Access Token: {tokens.access_token}")
        click.echo(f"Refresh Token: {tokens.refresh_token}")
    except Exception as e:
        click.echo(f"Login failed: {e}")


# User commands
@cli.group()
def user():
    """User management commands."""
    pass


@user.command(name="list")
def user_list():
    """List all users."""
    client = click.get_current_context().obj["client"]
    try:
        users = client.get_users()
        for user in users:
            click.echo(
                f"ID: {user.id}, Name: {user.name}, Telegram: {user.telegram_chat_id}"
            )
    except Exception as e:
        click.echo(f"Error getting users: {e}")


@user.command()
@click.argument("user_id", type=int)
def get_user(user_id):
    """Get user by ID."""
    client = click.get_current_context().obj["client"]
    try:
        user = client.get_user(user_id)
        click.echo(f"ID: {user.id}")
        click.echo(f"Name: {user.name}")
        click.echo(f"Telegram: {user.telegram_chat_id}")
    except Exception as e:
        click.echo(f"Error getting user: {e}")


@user.command()
@click.option("--name", required=True, help="User name")
@click.option("--telegram-chat-id", help="Telegram chat ID")
@click.password_option()
def create_user(name, telegram_chat_id, password):
    """Create a new user."""
    client = click.get_current_context().obj["client"]
    try:
        user_create = UserCreate(
            name=name, telegram_chat_id=telegram_chat_id, password=password
        )
        user = client.create_user(user_create)
        click.echo(f"Created user: ID={user.id}, Name={user.name}")
    except Exception as e:
        click.echo(f"Error creating user: {e}")


@user.command()
@click.argument("user_id", type=int)
@click.option("--name", help="New user name")
@click.option("--telegram-chat-id", help="New Telegram chat ID")
def update_user(user_id, name, telegram_chat_id):
    """Update a user."""

    client = click.get_current_context().obj["client"]
    try:
        print(name, telegram_chat_id)
        user_update = UserUpdate(name=name, telegram_chat_id=telegram_chat_id)
        user = client.update_user(user_id, user_update)
        click.echo(f"Updated user: ID={user.id}, Name={user.name}")
    except Exception as e:
        click.echo(f"Error updating user: {e}")


@user.command()
@click.argument("user_id", type=int)
def delete(user_id):
    """Delete a user."""
    client = click.get_current_context().obj["client"]
    try:
        client.delete_user(user_id)
        click.echo(f"Deleted user with ID: {user_id}")
    except Exception as e:
        click.echo(f"Error deleting user: {e}")


# Project commands
@cli.group()
def project():
    """Project management commands."""
    pass


@project.command(name="list")
def project_list():
    """List all projects."""
    client = click.get_current_context().obj["client"]
    try:
        projects = client.get_projects()
        for proj in projects:
            click.echo(
                f"ID: {proj.id}, Name: {proj.name}, Lang: {proj.lang}, Key: {proj.key}"
            )
    except Exception as e:
        click.echo(f"Error getting projects: {e}")


@project.command()
@click.argument("project_id", type=int)
def get(project_id):
    """Get project by ID."""
    client = click.get_current_context().obj["client"]
    try:
        project = client.get_project(project_id)
        click.echo(f"ID: {project.id}")
        click.echo(f"Name: {project.name}")
        click.echo(f"Lang: {project.lang}")
        click.echo(f"Key: {project.key}")
    except Exception as e:
        click.echo(f"Error getting project: {e}")


@project.command()
@click.option("--name", required=True, help="Project name")
@click.option("--lang", required=True, help="Project language")
def create(name, lang):
    """Create a new project."""
    client = click.get_current_context().obj["client"]
    try:
        project_create = ProjectCreate(name=name, lang=lang)
        project = client.create_project(project_create)
        click.echo(
            f"Created project: ID={project.id}, Name={project.name}, Lang={project.lang}"
        )
    except Exception as e:
        click.echo(f"Error creating project: {e}")


@project.command()
@click.argument("project_id", type=int)
@click.option("--name", help="New project name")
@click.option("--lang", help="New project language")
def update(project_id, name, lang):
    """Update a project."""
    if not name and not lang:
        click.echo("At least one field (name or lang) must be specified for update")
        return

    client = click.get_current_context().obj["client"]
    try:
        # Get the current project to fill in non-updated values
        current_project = client.get_project(project_id)

        # Update only the values that were specified
        update_data = {
            "name": name if name is not None else current_project.name,
            "lang": lang if lang is not None else current_project.lang,
        }
        project_update = ProjectUpdate(**update_data)

        project = client.update_project(project_id, project_update)
        click.echo(
            f"Updated project: ID={project.id}, Name={project.name}, Lang={project.lang}"
        )
    except Exception as e:
        click.echo(f"Error updating project: {e}")


@project.command()
@click.argument("project_id", type=int)
def delete_project(project_id):
    """Delete a project."""
    client = click.get_current_context().obj["client"]
    try:
        client.delete_project(project_id)
        click.echo(f"Deleted project with ID: {project_id}")
    except Exception as e:
        click.echo(f"Error deleting project: {e}")


# Events/Envelopes commands
@cli.group()
def events():
    """Event management commands."""
    pass


@events.command(name="list")
@click.argument("project_id", type=int)
def events_list(project_id: int):
    """List all events."""
    client = click.get_current_context().obj["client"]
    try:
        envelopes = client.get_project_events(project_id)
        for envelope in envelopes:
            click.echo(
                f"ID: {envelope.id}, Project ID: {envelope.project_id}, Event ID: {envelope.event_id}"
            )
    except Exception as e:
        click.echo(f"Error getting events: {e}")


def main():
    """Main entry point."""
    cli()
