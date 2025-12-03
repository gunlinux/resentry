from typing import Sequence
from sqlmodel import select
from sqlalchemy.orm import selectinload

from resentry.repos.base import BaseRepo
from resentry.database.models.envelope import Envelope, EnvelopeItem


class EnvelopeRepository(BaseRepo):
    entity_type = Envelope

    async def get_all_by_project(self, project_id: int) -> Sequence[Envelope]:
        result = await self.db.exec(
            select(Envelope)
            .options(selectinload(Envelope.items))  # pyright: ignore[reportArgumentType]
            .where(Envelope.project_id == project_id)
        )
        return result.all()


class EnvelopeItemRepository(BaseRepo):
    entity_type = EnvelopeItem
