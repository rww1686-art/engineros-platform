import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = CompanyRepository(session)

    async def create(self, payload: CompanyCreate) -> Company:
        if payload.edrpou and await self.repository.get_by_edrpou(payload.edrpou):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="EDRPOU already exists")
        company = Company(**payload.model_dump(mode="json"))
        try:
            company = await self.repository.add(company)
            await self.session.commit()
            return company
        except IntegrityError as exc:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Company conflicts with existing data") from exc

    async def get(self, company_id: uuid.UUID) -> Company:
        company = await self.repository.get(company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return company

    async def update(self, company_id: uuid.UUID, payload: CompanyUpdate) -> Company:
        company = await self.get(company_id)
        changes = payload.model_dump(exclude_unset=True, mode="json")
        new_edrpou = changes.get("edrpou")
        if new_edrpou:
            existing = await self.repository.get_by_edrpou(new_edrpou)
            if existing and existing.id != company.id:
                raise HTTPException(status_code=409, detail="EDRPOU already exists")
        for field, value in changes.items():
            setattr(company, field, value)
        try:
            await self.session.commit()
            await self.session.refresh(company)
            return company
        except IntegrityError as exc:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Company conflicts with existing data") from exc

    async def delete(self, company_id: uuid.UUID) -> None:
        company = await self.get(company_id)
        await self.repository.delete(company)
        await self.session.commit()
