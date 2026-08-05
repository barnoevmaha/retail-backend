from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str = "customer"


class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str | None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
