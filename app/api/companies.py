import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyList, CompanyRead, CompanyUpdate
from app.services.company import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, session: SessionDep) -> CompanyRead:
    company = await CompanyService(session).create(payload)
    return CompanyRead.model_validate(company)


@router.get("", response_model=CompanyList)
async def list_companies(
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    name: str | None = None,
    edrpou: str | None = None,
    region: str | None = None,
    region_id: uuid.UUID | None = None,
    city: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
) -> CompanyList:
    items, total = await CompanyRepository(session).list(
        limit=limit,
        offset=offset,
        name=name,
        edrpou=edrpou,
        region=region,
        region_id=region_id,
        city=city,
        status=status_filter,
    )
    return CompanyList(
        items=[CompanyRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: uuid.UUID, session: SessionDep) -> CompanyRead:
    company = await CompanyService(session).get(company_id)
    return CompanyRead.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: uuid.UUID, payload: CompanyUpdate, session: SessionDep
) -> CompanyRead:
    company = await CompanyService(session).update(company_id, payload)
    return CompanyRead.model_validate(company)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: uuid.UUID, session: SessionDep) -> Response:
    await CompanyService(session).delete(company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
