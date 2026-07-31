import uuid

from fastapi import APIRouter, Response, status

from app.api.companies import SessionDep
from app.schemas.company_competency import CompanyCompetencyRead, CompanyCompetencyUpsert
from app.services.company_competency import CompanyCompetencyService

router = APIRouter(prefix="/companies/{company_id}/competencies", tags=["companies"])


@router.put("/{competency_id}", response_model=CompanyCompetencyRead)
async def assign_company_competency(
    company_id: uuid.UUID,
    competency_id: uuid.UUID,
    payload: CompanyCompetencyUpsert,
    session: SessionDep,
) -> CompanyCompetencyRead:
    link = await CompanyCompetencyService(session).upsert(
        company_id,
        competency_id,
        payload,
    )
    return CompanyCompetencyRead.model_validate(link)


@router.get("", response_model=list[CompanyCompetencyRead])
async def list_company_competencies(
    company_id: uuid.UUID,
    session: SessionDep,
) -> list[CompanyCompetencyRead]:
    links = await CompanyCompetencyService(session).list_for_company(company_id)
    return [CompanyCompetencyRead.model_validate(link) for link in links]


@router.delete("/{competency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_competency(
    company_id: uuid.UUID,
    competency_id: uuid.UUID,
    session: SessionDep,
) -> Response:
    await CompanyCompetencyService(session).delete(company_id, competency_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
