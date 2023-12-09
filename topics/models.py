from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, ForeignKey, FLOAT, Float
from sqlalchemy.orm import relationship

from users.models import User
from database.database import Base


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    owner_id = Column(String, index=True)
    text = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    disabled = Column(Boolean, default=False)

    comments = relationship("Comment", back_populates="topic")


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    message = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    disable = Column(Boolean, default=False)

    user = relationship("User", back_populates="comments")
    topic = relationship("Topic", back_populates="comments")
