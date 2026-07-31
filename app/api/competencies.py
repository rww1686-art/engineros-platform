import uuid

from fastapi import APIRouter, Query, status

from app.api.companies import SessionDep
from app.repositories.competency import CompetencyRepository
from app.schemas.competency import CompetencyCreate, CompetencyRead
from app.services.competency import CompetencyService

router = APIRouter(prefix="/competencies", tags=["competencies"])


@router.post("", response_model=CompetencyRead, status_code=status.HTTP_201_CREATED)
async def create_competency(payload: CompetencyCreate, session: SessionDep) -> CompetencyRead:
    competency = await CompetencyService(session).create(payload)
    return CompetencyRead.model_validate(competency)


@router.get("", response_model=list[CompetencyRead])
async def list_competencies(
    session: SessionDep,
    category: str | None = None,
    is_active: bool | None = Query(default=None),
) -> list[CompetencyRead]:
    competencies = await CompetencyRepository(session).list(
        category=category,
        is_active=is_active,
    )
    return [CompetencyRead.model_validate(competency) for competency in competencies]


@router.get("/{competency_id}", response_model=CompetencyRead)
async def get_competency(competency_id: uuid.UUID, session: SessionDep) -> CompetencyRead:
    competency = await CompetencyService(session).get(competency_id)
    return CompetencyRead.model_validate(competency)
