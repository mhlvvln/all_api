import os

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from users.models import User as UserModel

from database.database import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_current_user(token: str, db: Session = Depends(get_db)):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail={""},
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = str(payload.get("sub"))
        role: str = payload.get("role")
        if id is None:
            return JSONResponse({"status": False, "error": "не авторизован"}, status_code=401)
        token_data = payload.get("email")
    except JWTError as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=401)
    user = get_user(db, email=token_data)
    if user is None:
        return JSONResponse({"status": False, "error": "не авторизован"}, status_code=401)
    return user


def verify_token(authorization: dict = Header(..., convert_underscores=False)):
    # print(f"{authorization=}")
    try:
        scheme, token = authorization["scheme"], authorization["credentials"]
        print(scheme, token)
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = str(payload.get("sub"))
        if id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    return payload


def auth(token: HTTPAuthorizationCredentials, rules: list):
    token = token.model_dump()
    token = verify_token(token)
    for rule in rules:
        if rule == "*" or rule == token['role']:
            return token
    raise HTTPException(status_code=403, detail="Нет прав")


def get_user(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()