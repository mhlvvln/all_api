from pydantic import BaseModel
from .models import User as UserModel


class UserResponse(BaseModel):
    """
        Стандартное отображение Users
    """
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    created_at: str
    photo: str | None
    experience: float | None


class UserResponseAdmin(UserResponse):
    """
        Дополнить поля, которые выводим
    """
    disabled: bool
    experience: float | None


def user_to_response(user: UserModel):
    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        created_at=str(user.created_at),
        photo=user.photo,
        experience=user.experience
    )


def user_to_response_admin(user: UserModel):
    return UserResponseAdmin(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        created_at=str(user.created_at),
        photo=user.photo,
        experience=user.experience,
        disabled=user.disabled
    )


class AchievementSchema(BaseModel):
    title: str
    description: str
    photo: str | None