from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictError, NotFoundError
from app.models import Member
from app.repositories.member_repository import MemberRepository
from app.schemas import MemberCreate, MemberUpdate


class MemberService:
    def __init__(self, repository: MemberRepository) -> None:
        self.repository = repository

    def create_member(self, payload: MemberCreate) -> Member:
        normalized_email = self._normalize_email(payload.email)
        if self.repository.get_by_email(normalized_email):
            raise ConflictError("Member email already exists")
        try:
            return self.repository.create(
                name=payload.name,
                email=normalized_email,
                phone=payload.phone,
            )
        except IntegrityError as exc:
            raise ConflictError("Member email already exists") from exc

    def update_member(self, member_id: int, payload: MemberUpdate) -> Member:
        member = self.repository.get(member_id)
        if not member:
            raise NotFoundError("Member not found")

        updated_fields = payload.model_dump(exclude_unset=True)
        if "email" in updated_fields:
            updated_fields["email"] = self._normalize_email(updated_fields["email"])

        if "email" in updated_fields and updated_fields[
            "email"
        ] != self._normalize_email(member.email):
            if self.repository.get_by_email(updated_fields["email"]):
                raise ConflictError("Member email already exists")

        for key, value in updated_fields.items():
            setattr(member, key, value)

        try:
            return self.repository.save(member)
        except IntegrityError as exc:
            raise ConflictError("Member email already exists") from exc

    def list_members(self) -> list[Member]:
        return self.repository.list_all()

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()
