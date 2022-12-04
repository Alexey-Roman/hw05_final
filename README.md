# Yatube - Социальная сеть блогеров
### Описание
Это супер социальная сеть для блогеров)
### Технологии
Python 3.7
Django 2.2.19
### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
```bash
pip install -r requirements.txt
``` 
- В папке с файлом manage.py выполните команду:
```bash
python yatube\manage.py runserver
```

### Создать новое приложение в проекте
* python manage.py startapp название_проекта


### Запуск Django Python shell
```bash
python yatube\manage.py shell
```

### Отладка проекта
1. Сохранение зависимостей(списка библиотек):
    ```bash
    pip freeze > requirements.txt
    ```

### Работа с БД
#### Миграции проводятся в два этапа:
1. Первым делом запускается команда `makemigrations`, Django проверяет модели и таблицы в БД, анализирует их на соответствие друг другу, подготавливает скрипты миграций и сообщает, какие миграции необходимо применить; однако никаких изменений в БД в этот момент не вносится.
2. Затем запускается команда `migrate`, и в этот момент все изменения вносятся в БД.
```bash
python yatube\manage.py makemigrations
```
```bash
python yatube\manage.py migrate
```

### Авторы
_Alex Romantsov_



