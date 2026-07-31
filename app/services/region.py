import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.region import Region
from app.repositories.region import RegionRepository
from app.schemas.region import RegionCreate


class RegionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = RegionRepository(session)

    async def create(self, payload: RegionCreate) -> Region:
        if await self.repository.get_by_code(payload.code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Region code exists")
        try:
            region = await self.repository.add(Region(**payload.model_dump()))
            await self.session.commit()
            return region
        except IntegrityError as exc:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Region already exists") from exc

    async def get(self, region_id: uuid.UUID) -> Region:
        region = await self.repository.get(region_id)
        if region is None:
            raise HTTPException(status_code=404, detail="Region not found")
        return region
