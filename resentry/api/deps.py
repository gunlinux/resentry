from sqlalchemy.orm import Session

from resentry.database.database import get_sync_db


def get_db_session() -> Session:
    db = next(get_sync_db())
    try:
        yield db
    finally:
        db.close()