from pydantic import BaseModel


class TestSchema(BaseModel):
    title: str
    description: str
    category_age_id: int


class QuestionSchema(BaseModel):
    test_id: int
    text_question: str
    weight: float
    category_age_id: int


class AnswerSchema(BaseModel):
    question_id: int
    answer: str
    correct: bool


class QuestionsCategories(BaseModel):
    question_id: int
    category_id: int


class AlertSchema(BaseModel):
    title: str
    description: str