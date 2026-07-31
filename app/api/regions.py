import uuid

from fastapi import APIRouter, Query, status

from app.api.companies import SessionDep
from app.repositories.region import RegionRepository
from app.schemas.region import RegionCreate, RegionRead
from app.services.region import RegionService

router = APIRouter(prefix="/regions", tags=["regions"])


@router.post("", response_model=RegionRead, status_code=status.HTTP_201_CREATED)
async def create_region(payload: RegionCreate, session: SessionDep) -> RegionRead:
    region = await RegionService(session).create(payload)
    return RegionRead.model_validate(region)


@router.get("", response_model=list[RegionRead])
async def list_regions(
    session: SessionDep,
    is_active: bool | None = Query(default=None),
) -> list[RegionRead]:
    regions = await RegionRepository(session).list(is_active=is_active)
    return [RegionRead.model_validate(region) for region in regions]


@router.get("/{region_id}", response_model=RegionRead)
async def get_region(region_id: uuid.UUID, session: SessionDep) -> RegionRead:
    region = await RegionService(session).get(region_id)
    return RegionRead.model_validate(region)
