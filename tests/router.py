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
from tests.schemas import TestSchema, QuestionSchema, AnswerSchema, QuestionsCategories, AlertSchema
# from users.service import get_user, usersGet, setPhoto, getAll, disableUser, activateUser, editUser
from tests.service import testGetAll, createTest, getAgeCategories, getCategories, getTestById, addQuestion, addAnswer, \
    bindCategory, getQuestion, getQuestionsByCategoryAndAge, getLastAlert, setLastAlert, checkAnswer, \
    getHistoryUsersAdmin, getHistoryUser, getRecommendationsUser, getRecommendationsAdmin, getMainRecommend

test_router = APIRouter()

security = HTTPBearer()

alerts_router = APIRouter()


@alerts_router.get("/last", tags=["Alerts"])
def get_last(
        db: Session = Depends(get_db)
):
    return getLastAlert(db)


@alerts_router.post("/setLast", tags=["Alerts", "Admin"])
def set_last(
        alert: AlertSchema,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["admin"])
    id = int(rules["sub"])
    return setLastAlert(db, alert)



@test_router.get("/getAll", summary="Получение информации о Test", tags=["Tests"])
def getAll(
        db: Session = Depends(get_db)
):
    return testGetAll(db)


@test_router.get("/getAgeCategories", summary="Получит возрастные категории", tags=["Tests"])
def get_categories_age(
        db: Session = Depends(get_db)
):
    return getAgeCategories(db)


@test_router.get("/getCategories", summary="Получить категории(темы вопросов)", tags=["Tests"])
def get_categories(
        db: Session = Depends(get_db)
):
    return getCategories(db)


@test_router.post("/addTest", summary="Добавляет тест", tags=["Tests", "Admin"])
def create_test(
        test: TestSchema,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["admin"])
    id = int(rules["sub"])
    return createTest(db, id, test)


@test_router.get("/getById", summary="Получить тест по id", tags=["Tests"])
def get_test_by_id(
        test_id: int,
        db: Session = Depends(get_db)
):
    return getTestById(db, test_id)


@test_router.post("/addQuestion", summary="Добавить вопрос", tags=["Tests", "Questions", "Admin"])
def add_question(
        question: QuestionSchema,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["admin"])
    id = int(rules["sub"])
    return addQuestion(db, id, question)


@test_router.post("/addVariant", summary="Добавить ответ(админ)", tags=["Tests", "Admin"])
def add_variant(
        variant: AnswerSchema,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["admin"])
    return addAnswer(db, variant)


@test_router.post("/bindCategory", summary="Привязать категорию к тесту", tags=["Tests", "Admin"])
def bind_category(
        qc: QuestionsCategories,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
):
    rules = auth(token, ["admin"])
    id = int(rules["sub"])
    return bindCategory(db, qc)


@test_router.get("/getQuestionById", summary="Получить запрос по id", tags=["Tests", "Questions"])
def get_question_by_id(
        q_id: int,
        db: Session = Depends(get_db),
):
    return getQuestion(db, q_id)


@test_router.get("/getQuestionByCategory", summary="Получить вопросы по категориям", tags=["Tests", "Questions"])
def get_question_by_categories(
        category_id: int = None,
        age_category_id: int = None,
        count: int = 30,
        db: Session = Depends(get_db),
):
    return getQuestionsByCategoryAndAge(db, category_id, age_category_id, count)


@test_router.post("/checkAnswer", summary="Сверить результаты", tags=["Users", "Tests"])
def check_answer(
        question_id: int,
        answer_id: int,
        answer_time: int,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
):
    rules = auth(token, ["*"])
    u_id = int(rules["sub"])
    return checkAnswer(db, question_id, answer_id, u_id, answer_time)


@test_router.get("/getHistoryAdmin", summary="Получить историю пользователей(админ)", tags=["Users", "Admin"])
def get_history_users_admin(
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
):
    rules = auth(token, ["admin"])
    return getHistoryUsersAdmin(db)


@test_router.get("/getHistoryUser", summary="Получить историю пользователя", tags=["Users"])
def get_history_users(
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
):
    rules = auth(token, ["user"])
    id = int(rules["sub"])
    return getHistoryUser(db, id)


@test_router.get("/getRecommendations", summary="Получить последние запросы пользователя вместе с необходимостью еще показывать их", tags=["Users"])
def get_recommendations(
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
):
    rules = auth(token, ["user"])
    id = int(rules["sub"])
    return getRecommendationsUser(db, id)


@test_router.get("/getMainRecommend", summary="Получить персональную рекомендацию", tags=["Users"])
def get_main_recommended(
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
):
    rules = auth(token, ["user"])
    id = int(rules["sub"])
    return getMainRecommend(db, id)


@test_router.get("/getRecommendationsAdmin", summary="Получить последние запросы пользователей", tags=["Admin"])
def get_recommendations(
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
):
    rules = auth(token, ["admin"])
    return getRecommendationsAdmin(db)

