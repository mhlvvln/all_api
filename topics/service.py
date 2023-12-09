from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from topics.schemas import TopicSchema, CommentSchema
from .models import Topic as TopicModel
from .models import Comment as CommentModel
from users.models import User as UserModel


def createTopic(db: Session, owner_id: int, topic: TopicSchema):
    data = {
        "title": topic.title,
        "text": topic.text,
        "owner_id": owner_id
    }

    new = TopicModel(**data)
    try:
        db.add(new)
        db.commit()
        db.refresh(new)
        return {"status": True, "topic": new}
    except:
        raise HTTPException(detail="Вероятно, введен неверный id", status_code=403)


def getTopicById(db: Session, id: int):
    topic = (
        db.query(TopicModel)
        .join(CommentModel, isouter=True)
        .join(UserModel, CommentModel.owner_id == UserModel.id, isouter=True)
        .options(joinedload(TopicModel.comments).joinedload(CommentModel.user))
        .filter(TopicModel.id == id)
        .first()
    )

    if not topic:
        raise HTTPException(detail="Не найдена лекция", status_code=404)

    topic_response = {
        "id": topic.id,
        "title": topic.title,
        "owner_id": topic.owner_id,
        "text": topic.text,
        "created_at": topic.created_at,
        "disabled": topic.disabled,
        "comments": [
            {
                "id": comment.id,
                "owner_id": comment.owner_id,
                "topic_id": comment.topic_id,
                "message": comment.message,
                "created_at": comment.created_at,
                "disable": comment.disable,
                "user": {
                    "photo": comment.user.photo if comment.user else None,
                    "first_name": comment.user.first_name if comment.user else None,
                    "last_name": comment.user.last_name if comment.user else None
                }
            }
            for comment in topic.comments
        ]
    }

    return {"status": True, "topic": topic_response}


def getAllTopic(db: Session):
    topics = (
        db.query(TopicModel)
        .join(CommentModel, isouter=True)
        .join(UserModel, CommentModel.owner_id == UserModel.id, isouter=True)
        .options(joinedload(TopicModel.comments).joinedload(CommentModel.user))
        .all()
    )

    topics_response = [
        {
            "id": topic.id,
            "title": topic.title,
            "owner_id": topic.owner_id,
            "text": topic.text,
            "created_at": topic.created_at,
            "disabled": topic.disabled,
            "comments": [
                {
                    "id": comment.id,
                    "owner_id": comment.owner_id,
                    "topic_id": comment.topic_id,
                    "message": comment.message,
                    "created_at": comment.created_at,
                    "disable": comment.disable,
                    "user": {
                        "photo": comment.user.photo if comment.user else None,
                        "first_name": comment.user.first_name if comment.user else None,
                        "last_name": comment.user.last_name if comment.user else None
                    }
                }
                for comment in topic.comments
            ]
        }
        for topic in topics
    ]

    return {"status": True, "topics": topics_response}


def sendComment(db: Session, comment: CommentSchema, owner_id: int):
    data = {
        "topic_id": comment.topic_id,
        "message": comment.message,
        "owner_id": owner_id,
    }

    new = CommentModel(**data)
    try:
        db.add(new)
        db.commit()
        db.refresh(new)
        return {"status": True, "comment": new}
    except:
        raise HTTPException(detail="Вероятно, введен неверный id", status_code=403)
