import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.models.company import Company


class CompanyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, company_id: uuid.UUID) -> Company | None:
        return await self.session.get(Company, company_id)

    async def get_by_edrpou(self, edrpou: str) -> Company | None:
        result = await self.session.execute(select(Company).where(Company.edrpou == edrpou))
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        limit: int,
        offset: int,
        name: str | None = None,
        edrpou: str | None = None,
        region: str | None = None,
        region_id: uuid.UUID | None = None,
        city: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Company], int]:
        filters: list[ColumnElement[bool]] = []
        if name:
            filters.append(Company.name.ilike(f"%{name}%"))
        if edrpou:
            filters.append(Company.edrpou == edrpou)
        if region:
            filters.append(Company.region == region)
        if region_id:
            filters.append(Company.region_id == region_id)
        if city:
            filters.append(Company.city == city)
        if status:
            filters.append(Company.status == status)

        query = select(Company).where(*filters).order_by(Company.name).limit(limit).offset(offset)
        count_query = select(func.count()).select_from(Company).where(*filters)
        rows = await self.session.execute(query)
        total = await self.session.scalar(count_query)
        return list(rows.scalars().all()), int(total or 0)

    async def add(self, company: Company) -> Company:
        self.session.add(company)
        await self.session.flush()
        await self.session.refresh(company)
        return company

    async def delete(self, company: Company) -> None:
        await self.session.delete(company)
        await self.session.flush()
