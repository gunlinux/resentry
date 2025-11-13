from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, DateTime

from resentry.database.database import Base


class Envelope(Base):
    __tablename__ = "envelopes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    payload = Column(LargeBinary)
    event_id = Column(String, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    dsn = Column(String, nullable=True)


class EnvelopeItem(Base):
    __tablename__ = "envelope_items"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("envelopes.id"))
    item_id = Column(String, index=True)
    payload = Column(LargeBinary)
