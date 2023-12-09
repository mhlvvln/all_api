database - хранит файлы подключения к БД
ml - хранит в себе скрипт создания модели машинного обучения, функцию получения результата по входным данным, файл, в котором сохранены данные модели

tests/router.py - прописаны маршруты и вызовы функций
tests/service.py - прописаны функции, вызываемые из router.py
tests/models.py - модели подключения к базам данных, связанные с Test
tests/schemas.py - классы валидации данных, связанных с Test

topics/router.py - прописаны маршруты для topics(лекций)
topics/service.py - основной функционал, работа с базой данных для topics
topics/models.py - модели для работы с sqlalchemy
topics/schemas.py - классы валидации данных, связанных с Test

topics/router.py - прописаны маршруты для работы с API Users
topics/service.py - основной функционал, работа с базой данных для users
topics/models.py - модели для работы с sqlalchemy, связанные с users
topics/schemas.py - классы валидации данных, связанных с Users

auth_service.py - функции для проверки прав пользователя
main.py - собирает все роуты, всю программу в себя
