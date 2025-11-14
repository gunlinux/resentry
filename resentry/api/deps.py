from typing import Generator
from sqlmodel import Session


from resentry.database.database import get_sync_db


def get_db_session() -> Generator[Session, None, None]:
    db = next(get_sync_db())
    try:
        yield db
    finally:
        db.close()
