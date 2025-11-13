from sqlalchemy import Column, Integer, String

from resentry.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    telegram_chat_id = Column(String, nullable=True)