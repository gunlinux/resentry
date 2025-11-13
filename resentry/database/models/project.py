from sqlalchemy import Column, Integer, String

from resentry.database.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    lang = Column(String, index=True)