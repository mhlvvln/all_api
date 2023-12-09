from fastapi import HTTPException
from sqlalchemy.orm import Session
from .models import User as UserModel
from .models import Achievement as AchievementModel
from .schemas import UserResponse, user_to_response, user_to_response_admin, AchievementSchema


def get_user(db: Session, id: int, disabled=False):
    user = db.query(UserModel).filter(UserModel.id == id, UserModel.disabled == disabled).first()
    if user is None:
        raise HTTPException(detail=f"Пользователь с {id=}, {disabled=} не найден", status_code=404)
    return user


def usersGet(db: Session, id: int):
    user = get_user(db, id)
    return {
        "status": True,
        "user": user_to_response(user)
    }


def checkPhotoHost(photo_url: str):
    photo_hosts = [
        "http://26.65.125.199:8001",
        "https://26.65.125.199:8001",
        "http://127.0.0.1:8001",
        "https://127.0.0.1:8001",
        "http://fileserver-bxwzgfn0.b4a.run",
        "https://fileserver-bxwzgfn0.b4a.run",
    ]

    for host in photo_hosts:
        if host in photo_url:
            return True
    return False


# print(checkPhotoHost("http://26.65.125.199:8001/photos/3b1fa5f649bc912ba6d16e8cdd13e7909dcbb9ff.jpeg"))


def setPhoto(db: Session, user_id: int, photo_url: str):
    if checkPhotoHost(photo_url):
        user = get_user(db, user_id)
        user.photo = photo_url
        db.commit()
        return {
            "status": True,
            "user": user_to_response(user)
        }
    raise HTTPException(status_code=403, detail="Позволяем загружать только с нашего сервачка")


def getArrayUsers(db: Session, ids: str):
    try:
        ids = ids.split(",")
        ids = [int(id) for id in ids]
        users = db.query(UserModel).filter(UserModel.id.in_(ids)).all()

        users_list = [user_to_response_admin(user) for user in users]

        return {
            "status": True,
            "users": users_list
        }
    except:
        raise HTTPException(detail="Ошибка где-то случилась", status_code=403)


def getAll(db: Session):
    users = db.query(UserModel).all()
    users_list = []
    for user in users:
        users_list.append(user_to_response_admin(user))
    return {
        "status": True,
        "users": users_list
    }


def disableUser(db: Session, user_id: int):
    user = get_user(db, user_id)
    user.disabled = True
    db.commit()
    return {
        "status": True,
        "user": user_to_response_admin(user)
    }


def activateUser(db: Session, user_id: int):
    user = get_user(db, user_id, True)
    user.disabled = False
    db.commit()
    return {
        "status": True,
        "user": user_to_response_admin(user)
    }


def editUser(db: Session, user_id: int, *args, **kwargs):
    if user_id == 0 or user_id is None:
        raise HTTPException(status_code=404, detail=f"user_id обязательный параметр, передано {user_id=}")

    user = get_user(db, user_id)

    change = False

    if kwargs['first_name']:
        user.first_name = kwargs['first_name']
        change = True
    if kwargs['last_name']:
        user.last_name = kwargs['last_name']
        change = True
    if kwargs['email']:
        user.email = kwargs['email']
        change = True
    if kwargs['photo']:
        setPhoto(db, user_id, kwargs['photo'])
        change = True

    if change:
        try:
            db.commit()
            return {
                "status": True,
                "user": user_to_response_admin(user)
            }
        except:
            raise HTTPException(status_code=403, detail="Некорректные данные(почта/photo, и тд)")
    raise HTTPException(status_code=403, detail="Должен быть передан хотя бы один параметр")


def setAchievement(db: Session, user_id: int, achievement: AchievementSchema):
    new_data = {
        "title": achievement.title,
        "description": achievement.description,
        "photo": achievement.photo,
        "owner_id": user_id
    }
    new_achievement = AchievementModel(**new_data)
    db.add(new_achievement)
    db.commit()

    return {"status": True, "achievement": new_achievement}


def getAchievementsByUserId(db: Session, user_id: int):
    achievements = db.query(AchievementModel).filter(AchievementModel.owner_id == user_id).all()
    if not achievements:
        return HTTPException(detail="Нет наград", status_code=404)
    return {"status": True, "achievements": achievements}

