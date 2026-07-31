import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competency import Competency
from app.repositories.competency import CompetencyRepository
from app.schemas.competency import CompetencyCreate


class CompetencyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = CompetencyRepository(session)

    async def create(self, payload: CompetencyCreate) -> Competency:
        if await self.repository.get_by_code(payload.code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Competency code exists",
            )
        try:
            competency = await self.repository.add(Competency(**payload.model_dump()))
            await self.session.commit()
            return competency
        except IntegrityError as exc:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Competency already exists") from exc

    async def get(self, competency_id: uuid.UUID) -> Competency:
        competency = await self.repository.get(competency_id)
        if competency is None:
            raise HTTPException(status_code=404, detail="Competency not found")
        return competency
