import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.region import Region


class RegionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, region_id: uuid.UUID) -> Region | None:
        return await self.session.get(Region, region_id)

    async def get_by_code(self, code: str) -> Region | None:
        result = await self.session.execute(select(Region).where(Region.code == code))
        return result.scalar_one_or_none()

    async def list(self, *, is_active: bool | None = None) -> list[Region]:
        query = select(Region)
        if is_active is not None:
            query = query.where(Region.is_active == is_active)
        rows = await self.session.execute(query.order_by(Region.name))
        return list(rows.scalars().all())

    async def add(self, region: Region) -> Region:
        self.session.add(region)
        await self.session.flush()
        await self.session.refresh(region)
        return region
