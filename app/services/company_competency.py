import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.company_competency import CompanyCompetency
from app.models.competency import Competency
from app.repositories.company_competency import CompanyCompetencyRepository
from app.schemas.company_competency import CompanyCompetencyUpsert


class CompanyCompetencyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = CompanyCompetencyRepository(session)

    async def upsert(
        self,
        company_id: uuid.UUID,
        competency_id: uuid.UUID,
        payload: CompanyCompetencyUpsert,
    ) -> CompanyCompetency:
        if await self.session.get(Company, company_id) is None:
            raise HTTPException(status_code=404, detail="Company not found")
        if await self.session.get(Competency, competency_id) is None:
            raise HTTPException(status_code=404, detail="Competency not found")

        link = await self.repository.get(company_id, competency_id)
        if link is None:
            link = CompanyCompetency(company_id=company_id, competency_id=competency_id)
            self.session.add(link)

        changes = payload.model_dump(mode="python")
        if payload.source_url is not None:
            changes["source_url"] = str(payload.source_url)
        for field, value in changes.items():
            setattr(link, field, value)

        await self.session.commit()
        refreshed = await self.repository.get(company_id, competency_id)
        if refreshed is None:
            raise RuntimeError("Company competency was not persisted")
        return refreshed

    async def list_for_company(self, company_id: uuid.UUID) -> list[CompanyCompetency]:
        if await self.session.get(Company, company_id) is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return await self.repository.list_for_company(company_id)

    async def delete(self, company_id: uuid.UUID, competency_id: uuid.UUID) -> None:
        link = await self.repository.get(company_id, competency_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Company competency not found")
        await self.repository.delete(link)
        await self.session.commit()
