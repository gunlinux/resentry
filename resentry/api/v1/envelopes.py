from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import datetime

from resentry.api.deps import get_db_session
from resentry.database.models.envelope import Envelope as EnvelopeModel
from resentry.database.models.project import Project as ProjectModel
from resentry.database.schemas.envelope import Envelope as EnvelopeSchema
from resentry.sentry import unpack_sentry_envelope_from_request

envelopes_router = APIRouter()


@envelopes_router.post("/{project_id}/envelope/")
async def store_envelope(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db_session)
):
    # Check if project exists
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Read the raw body bytes
    body = await request.body()
    content_encoding = request.headers.get("content-encoding", None)
    
    # Parse the envelope using existing sentry functionality
    try:
        envelope = unpack_sentry_envelope_from_request(body, content_encoding)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid envelope format: {str(e)}")
    
    # Create envelope record in database
    envelope_db = EnvelopeModel(
        project_id=project_id,
        payload=body,
        event_id=envelope.event_id,
        sent_at=datetime.datetime.fromisoformat(envelope.headers.get("sent_at")) if envelope.headers.get("sent_at") else None,
        dsn=envelope.headers.get("dsn")
    )
    
    db.add(envelope_db)
    db.commit()
    db.refresh(envelope_db)
    
    return {"message": "Envelope stored successfully", "envelope_id": envelope_db.id}


@envelopes_router.get("/projects/events", response_model=List[EnvelopeSchema])
def get_project_events(db: Session = Depends(get_db_session)):
    envelopes = db.query(EnvelopeModel).all()
    return envelopes