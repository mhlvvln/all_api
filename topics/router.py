from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from auth_service import auth
from database.database import get_db
from topics.schemas import TopicSchema, CommentSchema
from topics.service import createTopic, getTopicById, getAllTopic, sendComment

topics_router = APIRouter()

security = HTTPBearer()


@topics_router.post("/create", tags=["Topics", "Admin"], summary="Создать лекцию")
def create_topic(
        topic: TopicSchema,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["admin"])
    id = int(rules["sub"])
    return createTopic(db, id, topic)


@topics_router.get("/getById", tags=["Topics"], summary="Получить  лекцию по id")
def get_topic_by_id(
        id: int,
        db: Session = Depends(get_db)
):
    return getTopicById(db, id)


@topics_router.get("/getAll", tags=["Topics"], summary="Получить все лекции")
def get_all_topics(
        db: Session = Depends(get_db)
):
    return getAllTopic(db)


@topics_router.post("/sendComment", tags=["Topics"], summary="Отправить комментарий")
def send_comment(
        comment: CommentSchema,
        token: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    rules = auth(token, ["*"])
    id = int(rules["sub"])
    return sendComment(db, comment, id)
