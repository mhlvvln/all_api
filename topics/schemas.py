from pydantic import BaseModel


class TopicSchema(BaseModel):
    title: str
    text: str


class CommentSchema(BaseModel):
    topic_id: int
    message: str
