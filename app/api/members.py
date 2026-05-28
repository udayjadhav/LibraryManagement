from fastapi import APIRouter, Depends, status

from app.dependencies import get_member_service
from app.models import Member
from app.schemas import MemberCreate, MemberOut, MemberUpdate
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["members"])

VALIDATION_ERROR = {
    422: {"description": "Request validation failed (invalid body or query params)"}
}


@router.post(
    "",
    response_model=MemberOut,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Member email already exists"}, **VALIDATION_ERROR},
)
async def create_member(
    payload: MemberCreate, service: MemberService = Depends(get_member_service)
) -> Member:
    return await service.create_member(payload)


@router.put(
    "/{member_id}",
    response_model=MemberOut,
    responses={
        404: {"description": "Member not found"},
        409: {"description": "Member email already exists"},
        **VALIDATION_ERROR,
    },
)
async def update_member(
    member_id: int,
    payload: MemberUpdate,
    service: MemberService = Depends(get_member_service),
) -> Member:
    return await service.update_member(member_id, payload)


@router.get("", response_model=list[MemberOut])
async def list_members(
    service: MemberService = Depends(get_member_service),
) -> list[Member]:
    return await service.list_members()
