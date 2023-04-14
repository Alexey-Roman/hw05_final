# Yatube - Социальная сеть блогеров

## Описание

Yatube - это социальная сеть для блогеров, где они могут делиться своими идеями и мнениями.

## Технологии

* Python 3.7
* Django 2.2.19
* Pillow9.0.1
* pytest6.2.4
* pytest-django4.4.0
* pytest-pythonpath0.7.3
* requests2.26.0
* six1.16.0
* sorl-thumbnail12.7.0
* django-environ0.8.1

## Функциональность

* Создание и настройка баз данных
* Управление аутентификацией пользователей
* Применение Django ORM для взаимодействия с базами данных и администрирования платформы

## Запуск проекта в dev-режиме

1. Установите и активируйте виртуальное окружение.
2. Установите зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```

3. В папке с файлом manage.py выполните команду:
```bash
python yatube\manage.py runserver
```

## Создание нового приложения в проекте

```bash
python manage.py startapp <название_проекта>
```

## Запуск Django Python shell
```bash
python yatube\manage.py shell
```

## Отладка проекта
Сохранение зависимостей (списка библиотек):

```bash
pip freeze > requirements.txt
```

## Работа с БД
Миграции проводятся в два этапа:

1. Запускается команда makemigrations:
```bash
python yatube\manage.py makemigrations
```
2. Затем запускается команда migrate:
```bash
python yatube\manage.py migrate
```

### Автор
_Alex Romantsov_
