from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, ChangePasswordRequest
from app.core.security import hash_password
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    return UserRepository(db).list_all()


@router.post("/", response_model=UserResponse)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin")),
):
    repo = UserRepository(db)
    user = repo.create(body.email, hash_password(body.password), body.role)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin")),
):
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = body.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    updated = repo.update(user, **update_data)
    return UserResponse.model_validate(updated)


@router.put("/me/change-password")
def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    AuthService(UserRepository(db), db).change_password(
        user, body.current_password, body.new_password, body.confirm_password
    )
    return {"message": "Password changed successfully"}
