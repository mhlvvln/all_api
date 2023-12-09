from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    disabled = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    photo = Column(String, nullable=False)
    experience = Column(Float)

    categories = relationship("Category", back_populates="owner")
    tests = relationship("Test", back_populates="owner")
    questions = relationship("Question", back_populates="owner")
    comments = relationship("Comment", back_populates="user")


class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    photo = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

