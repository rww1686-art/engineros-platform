import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_competency import CompanyCompetency


class CompanyCompetencyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(
        self, company_id: uuid.UUID, competency_id: uuid.UUID
    ) -> CompanyCompetency | None:
        result = await self.session.execute(
            select(CompanyCompetency).where(
                CompanyCompetency.company_id == company_id,
                CompanyCompetency.competency_id == competency_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_company(self, company_id: uuid.UUID) -> list[CompanyCompetency]:
        rows = await self.session.execute(
            select(CompanyCompetency)
            .where(CompanyCompetency.company_id == company_id)
            .order_by(CompanyCompetency.competency_id)
        )
        return list(rows.scalars().unique().all())

    async def delete(self, link: CompanyCompetency) -> None:
        await self.session.delete(link)
