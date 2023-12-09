import random
from datetime import datetime, timedelta
from json import loads

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from ml.train import getModelResult
from users.schemas import user_to_response_admin
from .models import Test as TestModel
from .models import Category as CategoryModel
from .models import AgeCategory as AgeCategoryModel
from .models import Question as QuestionModel
from .models import QuestionCategory as QuestionCategoryModel
from .models import Answer as AnswerModel
from users.models import User as UserModel
from .models import Alert as AlertModel
from users.service import user_to_response
from .schemas import TestSchema, QuestionSchema, AnswerSchema, QuestionsCategories, AlertSchema
from .models import QuestionsHistory as QuestionsHistoryModel
from ml import train


def getTestById(db: Session, test_id: int):
    test = (
        db.query(TestModel)
        .filter(TestModel.id == test_id)
        .options(
            joinedload(TestModel.owner),
            joinedload(TestModel.questions).joinedload(QuestionModel.answers)
        )
        .first()
    )

    if not test:
        raise HTTPException(detail="Тест не найден", status_code=404)

    test_response = {
        "id": test.id,
        "title": test.title,
        "owner_id": test.owner_id,
        "created_at": test.created_at,
        "description": test.description,
        "category_age_id": test.category_age_id,
        "owner": user_to_response(test.owner) if test.owner else [],
        "questions": [
            {
                "id": question.id,
                "owner_id": question.owner_id,
                "test_id": question.test_id,
                "text_question": question.text_question,
                "weight": question.weight,
                "answers": [
                    {
                        "id": answer.id,
                        "question_id": answer.question_id,
                        "answer": answer.answer
                    }
                    for answer in question.answers
                ]
            }
            for question in test.questions
        ] if test.questions else []
    }

    return {"status": True, "test": test_response}


def testGetAll(db: Session):
    tests = (
        db.query(TestModel)
        .options(
            joinedload(TestModel.owner),
            joinedload(TestModel.questions).joinedload(QuestionModel.answers)
        )
        .all()
    )

    tests_response = [
        {
            "id": test.id,
            "title": test.title,
            "owner_id": test.owner_id,
            "created_at": test.created_at,
            "description": test.description,
            "category_age_id": test.category_age_id,
            "owner": user_to_response(test.owner) if test.owner else [],
            "questions": [
                {
                    "id": question.id,
                    "owner_id": question.owner_id,
                    "test_id": question.test_id,
                    "text_question": question.text_question,
                    "weight": question.weight,
                    "answers": [
                        {
                            "id": answer.id,
                            "question_id": answer.question_id,
                            "answer": answer.answer
                        }
                        for answer in question.answers
                    ]
                }
                for question in test.questions
            ] if test.questions else []
        }
        for test in tests
    ]

    return {"status": True, "tests": tests_response}


def createTest(db: Session, owner_id: int, test: TestSchema):
    test_data = {
        "title": test.title,
        "description": test.description,
        "owner_id": owner_id,
        "category_age_id": test.category_age_id
    }

    new_test = TestModel(**test_data)
    try:
        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return {"status": True, "test": new_test}
    except:
        raise HTTPException(detail="Вероятно, введен неверный id", status_code=404)


def getAgeCategories(db: Session):
    categories = db.query(AgeCategoryModel).all()
    return {"status": True, "ageCategories": categories}


def getCategories(db: Session):
    categories = db.query(CategoryModel).all()
    return {"status": True, "categories": categories}


def addQuestion(db: Session, owner_id: int, question: QuestionSchema):
    question_data = {
        "test_id": question.test_id,
        "text_question": question.text_question,
        "owner_id": owner_id,
        "weight": question.weight,
        "category_age_id": question.category_age_id
    }

    new_question = QuestionModel(**question_data)
    try:
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        return {"status": True, "question": new_question}
    except:
        raise HTTPException(detail="Вероятно, введен неверный id", status_code=403)


def addAnswer(db: Session, answer: AnswerSchema):
    answer_data = {
        "question_id": answer.question_id,
        "answer": answer.answer,
        "correct": answer.correct
    }

    new_answer = AnswerModel(**answer_data)
    try:
        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)
        return {"status": True, "answer": new_answer}
    except:
        raise HTTPException(detail="Вероятно, введен неверный id", status_code=403)


def bindCategory(db: Session, qc: QuestionsCategories):
    data = {
        "question_id": qc.question_id,
        "category_id": qc.category_id
    }

    try:
        new_qc = QuestionCategoryModel(**data)
        db.add(new_qc)
        db.commit()
        db.refresh(new_qc)
        return {"status": True, "response": new_qc}
    except:
        raise HTTPException(detail="Вероятно, введен неверный id", status_code=403)


def getQuestion(db: Session, q_id: int):
    question = (
        db.query(QuestionModel)
        .filter(QuestionModel.id == q_id)
        .options(
            joinedload(QuestionModel.owner),
            joinedload(QuestionModel.test),
            joinedload(QuestionModel.answers),
            joinedload(QuestionModel.categories).joinedload(QuestionCategoryModel.category)
        )
        .first()
    )

    if not question:
        raise HTTPException(detail="Вопрос не найден", status_code=404)

    question_response = {
        "id": question.id,
        "owner_id": question.owner_id,
        "text_question": question.text_question,
        "weight": question.weight,
        "answers": [
            {
                "id": answer.id,
                "answer": answer.answer,
            }
            for answer in question.answers
        ],
        "categories": [
            {
                "id": category.id,
                "title": category.title,
                "owner_id": category.owner_id,
                "created_at": category.created_at
            }
            for category in [qc.category for qc in question.categories]
        ]
    }

    return {"status": True, "question": question_response}


def getQuestionsByCategoryAndAge(db: Session, category_id: int, age_category_id: int = None, count: int = 10):
    query = (
        db.query(QuestionModel)
        .join(QuestionCategoryModel)
        .join(AgeCategoryModel)
    )

    if category_id is not None:
        query = query.filter(QuestionCategoryModel.category_id == category_id)

    if age_category_id is not None:
        query = query.filter(AgeCategoryModel.id == age_category_id)

    query = query.limit(count)

    questions = (
        query
        .options(
            joinedload(QuestionModel.owner),
            joinedload(QuestionModel.test),
            joinedload(QuestionModel.answers),
            joinedload(QuestionModel.categories).joinedload(QuestionCategoryModel.category)
        )
        .all()
    )

    questions_response = [
        {
            "id": question.id,
            "owner_id": question.owner_id,
            "text_question": question.text_question,
            "weight": question.weight,
            "answers": [
                {
                    "id": answer.id,
                    "answer": answer.answer,
                }
                for answer in question.answers
            ],
            "categories": [
                {
                    "id": category.id,
                    "title": category.title,
                    "owner_id": category.owner_id,
                    "created_at": category.created_at
                }
                for category in [qc.category for qc in question.categories]
            ]
        }
        for question in questions
    ]

    return {"status": True, "questions": questions_response}


def getLastAlert(db: Session):
    current_time = datetime.utcnow()
    threshold_time = current_time - timedelta(minutes=30)

    last_alert = (
        db.query(AlertModel)
        .filter(AlertModel.created_at >= threshold_time)
        .order_by(AlertModel.created_at.desc())
        .first()
    )
    return {"status": True, "last_alert": last_alert}


def setLastAlert(db: Session, alert: AlertSchema):
    data = {
        "title": alert.title,
        "description": alert.description,
    }

    new = AlertModel(**data)
    try:
        db.add(new)
        db.commit()
        db.refresh(new)
        return {"status": True, "answer": new}
    except:
        raise HTTPException(detail="Не кайфанули", status_code=404)


def fillHistory(db: Session, owner_id, topic, user_answer, is_correct, question_id, number_of_attempts, response_time,
                question_rating):
    history_entry = QuestionsHistoryModel(
        owner_id=owner_id,
        topic=topic,
        user_answer=user_answer,
        is_correct=is_correct,
        question_id=question_id,
        number_of_attempts=number_of_attempts,
        response_time=response_time,
        question_rating=question_rating
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
    return history_entry


def count_attempts(db: Session, user_id: int, question_id: int) -> int:
    count = db.query(QuestionsHistoryModel).filter(
        QuestionsHistoryModel.owner_id == user_id,
        QuestionsHistoryModel.question_id == question_id
    ).count()
    return count


def getTopicCategory(db: Session, question_id: int):
    topic = db.query(QuestionCategoryModel).filter(QuestionCategoryModel.question_id == question_id).first()
    print(topic)
    if not topic:
        raise HTTPException(status_code=404, detail="Не найдена категория для этого вопроса")
    return topic.category_id


def question_rating(db: Session, question_id: int):
    rating = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if not rating:
        raise HTTPException(status_code=403, detail="Неверный question_id")
    return rating.weight


def checkAnswer(db: Session, question_id: int, answer_id: int, u_id: int, answer_time: int):
    question = db.query(QuestionModel).get(question_id)
    answer = db.query(AnswerModel).get(answer_id)

    if not question or not answer:
        raise HTTPException(status_code=403, detail="Not question or not answer")

    user = db.query(UserModel).filter(UserModel.id == u_id).first()
    if answer.correct:
        user.experience += 10
        res = f"Ваш рейтинг повышен на 10 - до {user.experience}"
    else:
        user.experience -= 15
        res = f"Ваш рейтинг унижен на 15 - до {user.experience}"
    db.commit()

    count_att = count_attempts(db, u_id, question_id)

    topic = getTopicCategory(db, question_id)
    question_rate = question_rating(db, question_id)
    correct = 1 if answer.correct else 0
    fillHistory(db, u_id, topic, answer_id, correct, question_id, count_att, answer_time, question_rate)

    return {"status": True, "result": res}


def getRating(db: Session):
    users = db.query(UserModel).order_by(UserModel.experience.desc()).all()
    users_list = []
    for user in users:
        users_list.append(user_to_response_admin(user))
    return {
        "status": True,
        "users": users_list
    }


def getHistoryUsersAdmin(db: Session):
    history = db.query(QuestionsHistoryModel).all()
    return {"status": True, "response": history}


def getHistoryUser(db: Session, user_id: int):
    history = db.query(QuestionsHistoryModel).filter(QuestionsHistoryModel.owner_id == user_id).all()
    return {"status": True, "response": history}


def getRecommendationsUser(db: Session, user_id: int):
    history = db.query(QuestionsHistoryModel).order_by(QuestionsHistoryModel.id.desc()).filter(
        QuestionsHistoryModel.owner_id == user_id).all()

    history_dict_list = [
        {
            "id": item.id,
            "owner_id": item.owner_id,
            "topic": item.topic,
            "user_answer": item.user_answer,
            "is_correct": item.is_correct,
            "question_id": item.question_id,
            "number_of_attempts": item.number_of_attempts,
            "response_time": item.response_time,
            "question_rating": item.question_rating
        }
        for item in history
    ]

    for item in history_dict_list:
        item["recommend"] = getModelResult(
            item["owner_id"],
            item["topic"],
            item["user_answer"],
            item["is_correct"],
            item["question_id"],
            item["number_of_attempts"],
            item["response_time"],
            item["question_rating"]
        )

    sorted_history = sorted(history_dict_list, key=lambda x: x['recommend'], reverse=True)
    return {"status": True, "result": sorted_history}


def getRecommendationsAdmin(db: Session):
    history = db.query(QuestionsHistoryModel).order_by(QuestionsHistoryModel.id.desc()).all()

    history_dict_list = [
        {
            "id": item.id,
            "owner_id": item.owner_id,
            "topic": item.topic,
            "user_answer": item.user_answer,
            "is_correct": item.is_correct,
            "question_id": item.question_id,
            "number_of_attempts": item.number_of_attempts,
            "response_time": item.response_time,
            "question_rating": item.question_rating
        }
        for item in history
    ]

    for item in history_dict_list:
        item["recommend"] = getModelResult(
            item["owner_id"],
            item["topic"],
            item["user_answer"],
            item["is_correct"],
            item["question_id"],
            item["number_of_attempts"],
            item["response_time"],
            item["question_rating"]
        )

    sorted_history = sorted(history_dict_list, key=lambda x: x['recommend'], reverse=True)
    return {"status": True, "result": sorted_history}


def getMainRecommend(db: Session, user_id: int):
    try:
        user_rec = getRecommendationsUser(db, user_id)["result"][0]
        topic = int(user_rec['topic'])
        category = db.query(CategoryModel).filter(CategoryModel.id == topic).first()
        title = category.title
        msg = f"Напиши случайную полезную рекомендацию по кибербезопасности из темы: {title}"

        url = 'http://127.0.0.1:8006/sendMessage'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        params = {
            'temperature': str(random.uniform(0.80, 1.0)),
        }

        data = [
            {"role": "user", "content": msg}
        ]

        response = requests.post(url, headers=headers, params=params, json=data)
        try:
            return {"status": True, "recommendation": loads(response.text)['choices'][0]['message']['content']}
        except:
            raise HTTPException(status_code=403, detail="Скорее всего, у юзера еще не сформиорваны рекомендации")
    except:
        raise HTTPException(detail="Скорее всего, рекомендации еще не сфоримированы", status_code=403)


def counting(n: int, marks: list, koefs: list, p: list):
    """
    n - count
    marks - оценки
    koefs - кфц сложности
    p: список вероятности случайного ответа
    """
    result = 0
    for i in range(n):
        result += marks[i] * koefs[i] * (1 - p[i])
    return result


def line_func(t: int, t_max: int, t_zad: int, zmax: int):
    if t <= t_zad:
        return zmax
    if t_zad < t <= t_max:
        return (zmax * (t + t_max))/t_zad-t_max
    if t > t_zad:
        return 0
