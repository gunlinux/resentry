from typing import List
import typing
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import datetime

from resentry.api.deps import get_async_db_session
from resentry.database.models.envelope import Envelope as EnvelopeModel, EnvelopeItem
from resentry.database.models.project import Project as ProjectModel
from resentry.database.schemas.envelope import Envelope as EnvelopeSchema
from resentry.sentry import unpack_sentry_envelope_from_request_async

envelopes_router = APIRouter()


@envelopes_router.post("/{project_id}/envelope/")
async def store_envelope(
    request: Request, project_id: int, db: AsyncSession = Depends(get_async_db_session)
):
    # Check if project exists
    result = await db.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    project = result.first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    project = project[0]  # Get the actual project object

    # Read the raw body bytes
    body = await request.body()
    content_encoding = request.headers.get("content-encoding", None)

    # Parse the envelope using existing sentry functionality
    try:
        envelope = await unpack_sentry_envelope_from_request_async(
            body, content_encoding
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid envelope format: {str(e)}"
        )

    # Create envelope record in database
    sent_at_str = envelope.headers.get("sent_at")
    sent_at = datetime.datetime.fromisoformat(sent_at_str) if sent_at_str else None

    envelope_db = EnvelopeModel(
        project_id=project_id,
        payload=body,
        event_id=envelope.event_id,
        sent_at=sent_at,
        dsn=envelope.headers.get("dsn"),
    )
    db.add(envelope_db)
    await db.commit()
    await db.refresh(envelope_db)
    for item_id, item in enumerate(envelope.items):
        item_db = EnvelopeItem(
            event_id=typing.cast(int, envelope_db.id),
            item_id=str(item_id),
            payload=item.get_payload_bytes(),
        )
        db.add(item_db)
    await db.commit()

    return {"message": "Envelope stored successfully", "envelope_id": envelope_db.id}


@envelopes_router.get("/projects/events", response_model=List[EnvelopeSchema])
async def get_project_events(db: AsyncSession = Depends(get_async_db_session)):
    result = await db.execute(select(EnvelopeModel))
    envelopes = result.all()
    return [envelope[0] for envelope in envelopes]
