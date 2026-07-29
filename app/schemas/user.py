from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "customer"


class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
