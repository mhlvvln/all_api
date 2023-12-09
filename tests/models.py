from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, ForeignKey, FLOAT, Float
from sqlalchemy.orm import relationship

from users.models import User
from database.database import Base
from users.schemas import UserResponse


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

    owner = relationship(User, back_populates="categories")
    questions = relationship("QuestionCategory", back_populates="category")


class AgeCategory(Base):
    __tablename__ = "category_age"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    age_from = Column(Integer)
    age_to = Column(Integer)


class Test(Base):
    __tablename__ = "tests"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP, server_default=func.now())
    description = Column(String)
    category_age_id = Column(Integer, ForeignKey("category_age.id"))

    owner = relationship(User, back_populates="tests")
    questions = relationship("Question", back_populates="test")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    test_id = Column(Integer, ForeignKey("tests.id"))
    text_question = Column(String)
    weight = Column(Float)
    category_age_id = Column(Integer, ForeignKey("category_age.id"))

    owner = relationship(User, back_populates="questions")
    test = relationship("Test", back_populates="questions")

    answers = relationship("Answer", back_populates="question")
    categories = relationship("QuestionCategory", back_populates="question")


class QuestionCategory(Base):
    __tablename__ = "questions_categories"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    question = relationship("Question", back_populates="categories")
    category = relationship("Category", back_populates="questions")


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(String, nullable=False)
    correct = Column(Boolean, default=False)

    question = relationship("Question", back_populates="answers")


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())


class QuestionsHistory(Base):
    __tablename__ = "questions_history"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer)
    topic = Column(Integer)
    user_answer = Column(Integer)
    is_correct = Column(Integer)
    question_id = Column(Integer)
    number_of_attempts = Column(Integer)
    response_time = Column(Integer)
    question_rating = Column(Float)
    date = Column(TIMESTAMP, server_default=func.now())

