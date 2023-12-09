import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from auth_service import auth
from database.database import get_db
from tests.service import getRating
from users.schemas import AchievementSchema
from users.service import get_user, usersGet, setPhoto, getAll, disableUser, activateUser, editUser, getArrayUsers, \
    setAchievement, getAchievementsByUserId

user_router = APIRouter()

security = HTTPBearer()


@user_router.get("/get", summary="Получение информации о User", tags=["Users"])
def get(
        id: int,
        db: Session = Depends(get_db)
):
    return usersGet(db, id)


@user_router.get("/getArray", summary="Получить много пользователей User", tags=["Users"])
def get_array_users(
        ids: str,
        db: Session = Depends(get_db)
):
    return getArrayUsers(db, ids)


@user_router.post("/setPhoto", summary="Установить фотографию пользователю", tags=["Users"])
def set_photo(
        photo_url: str,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["*"])
    id = int(rules["sub"])
    return setPhoto(db, id, photo_url)


@user_router.get("/getAll", tags=["Admin"], summary="Получить список всех user")
def get_all(
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["admin"])
    return getAll(db)
    # raise HTTPException(status_code=403, detail="Нет прав доступа, только для админа")


@user_router.get("/disable", tags=["Admin"], summary="Удалить юзера(пометить его disabled)")
def disable(
        user_id: int,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["admin"])
    return disableUser(db, user_id)
    #raise HTTPException(status_code=403, detail="Нет прав доступа, только для админа")


@user_router.get("/activate", tags=["Admin"], summary="Восстановить юзера(убрать пометку disabled)")
def activate(
        user_id: int,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["admin"])
    return activateUser(db, user_id)
    #raise HTTPException(status_code=403, detail="Нет прав доступа, только для админа")


@user_router.post("/edit",
                  tags=["Admin", "Users"],
                  summary="Изменить информацию о человеке. Обязателен хотя бы один параметр. Для пользователей user_id не обязателен.")
def edit(
        user_id: int = 0,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        photo: str = None,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
):
    rules = auth(token, ["*"])
    if rules["role"] == "admin":
        return editUser(db, user_id, first_name=first_name, last_name=last_name, email=email, photo=photo)
    else:
        return editUser(db, int(rules["sub"]), first_name=first_name, last_name=last_name, email=email, photo=photo)
    #raise HTTPException(status_code=403, detail="Нет прав доступа, только для админа")


@user_router.get("/me", tags=["Users", "Admin"])
def users_me(
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["*"])
    id = int(rules["sub"])
    return usersGet(db, id)


@user_router.get("/getRating", tags=["Users", "Admin"])
def get_rating(
        db: Session = Depends(get_db)
):
    return getRating(db)


@user_router.post("/setAchievement", tags=["Admin"])
def set_achievement(
        user_id: int,
        achievement: AchievementSchema,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["admin"])
    return setAchievement(db, user_id, achievement)


@user_router.post("/getAchievement", tags=["User"])
def get_achievement(
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["user"])
    id = int(rules["sub"])
    return getAchievementsByUserId(db, id)