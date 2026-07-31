import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competency import Competency


class CompetencyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, competency_id: uuid.UUID) -> Competency | None:
        return await self.session.get(Competency, competency_id)

    async def get_by_code(self, code: str) -> Competency | None:
        result = await self.session.execute(
            select(Competency).where(Competency.code == code)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        category: str | None = None,
        is_active: bool | None = None,
    ) -> list[Competency]:
        query = select(Competency)
        if category:
            query = query.where(Competency.category == category)
        if is_active is not None:
            query = query.where(Competency.is_active == is_active)
        rows = await self.session.execute(query.order_by(Competency.name))
        return list(rows.scalars().all())

    async def add(self, competency: Competency) -> Competency:
        self.session.add(competency)
        await self.session.flush()
        await self.session.refresh(competency)
        return competency
