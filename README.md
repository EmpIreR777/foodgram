# Проект Foodgram
Доменное имя проекта: https://foodgram-best.zapto.org/
Документация API эндпоинтов Бекенда. https://foodgram-best.zapto.org/api/docs/

## Назначение проекта:
Foodgram предназначен для размещения кулинарных рецептов. Зарегистрированные пользователи могут делиться своими рецептами, подписываться на других участников, добавлять рецепты в список избранного, а также автоматически составлять и экспортировать список покупок в формате PDF.

Установка на локальном компьютере

1. Клонируйте репозиторий:
```
git@github.com:EmpIreR777/foodgram.git
```

2. Установите и активируйте виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate  - для Windows
source venv/bin/activate - для Linux
```

3. Установите зависимости:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Выполните миграции:
```

python manage.py migrate
```

5. Создайте суперпользователя:
```
python manage.py createsuperuser
```

6. Запустите проект:
```
python manage.py runserver
```

## Технологии:
    *Python 3.10
    *Django 5.0.6
    *Django REST framework 3.15
    *Nginx
    *Docker
    *Postgres

## https://github.com/EmpIreR777