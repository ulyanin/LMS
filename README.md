[![Build Status](https://travis-ci.org/ulyanin/LMS.svg?branch=master)](https://travis-ci.org/ulyanin/LMS) [![codecov](https://codecov.io/gh/ulyanin/LMS/branch/master/graph/badge.svg)](https://codecov.io/gh/ulyanin/LMS)


# LMS

Требования: [TZ.md](TZ.md)

## Первый запуск

### docker-compose
Сначала запускаем нужные образы
```(bash)
# docker-compose up
```

### Проверяем web сервер
```(bash)
curl "localhost:8000/ping"
```
```
{"status": "ok"}        
```

### Заполнение таблиц

Когда Docker запущен, можно заполнить создать и заполнить таблицы коммандами:
```(bash)
virtualenv venv
source venv/bin/activate
pip install -r lms/infra/db/manage_tables/requirements.txt
python lms/infra/db/manage_tables/execute_script.py --script lms/infra/db/manage_tables/sql_scripts/create_tables.sql
python lms/infra/db/manage_tables/execute_script.py --script lms/infra/db/manage_tables/sql_scripts/fill_tables.sql

```

Проверить таблицы можно через psql.

Из контейнера:
```(bash)
sudo docker exec -it lms_postgres_1 bash
psql -U admin -d lms_db
```
Локальный:
```(bash)
psql -U admin -d lms_db -h localhost
```
Проверка:
```(postgresql)
select * from users;
```
Должна получиться непустая таблица

> ### hint
> Если вы хотите удалять таблицы, чтобы потом их пересоздать, воспользуйтесь drop_tables.sql:
> ```(bash)
> python lms/infra/db/manage_tables/execute_script.py --script lms/infra/db/manage_tables/sql_scripts/drop_tables.sql
> ```

### Итог
Теперь у нас есть заполненные таблицы, содержащие некоторое количество пользователей и преподавателей.

## API

**NEW**

Доступна также web версия, которую можно запустить в вашем POSTMAN:
https://documenter.getpostman.com/view/11436602/SzmmUEmp?version=latest

### Регистрация (2.2)

Практически для всех действий нужна авторизация, поэтому прежде всего необходимо зарегистрировать пользователя.

Зарегистрируем первого, третьего и седьмого (преподаватель):
```(bash)
curl "localhost:8000/register/" -X POST --data '{"verification_code": "47d0e78d-2236-48ec-95db-dc50321fe3cc", "email": "u1@mail.ru", "password": "pass"}' -s -v | jq .
curl "localhost:8000/register/" -X POST --data '{"verification_code": "8e3adc33-7ba9-4035-943f-dbac996c4c42", "email": "u3@mail.ru", "password": "pass"}' -s -v | jq .
curl "localhost:8000/register/" -X POST --data '{"verification_code": "d3a9f835-6767-4bf2-b535-198c9ab56194", "email": "prep7@mail.ru", "password": "pass"}' -s -v | jq .
```

### Логин, авторизация (2.1)

Авторизация осуществляется через cookie, которые присылаются пользователю в специальном header'е во время логина.

Далее для удобства можете использовать удобный http клиент, который за вас сохранит куки, например, Postman

Логин под первого юзера:
```(bash)
curl "localhost:8000/login/" -X POST --data '{"email": "u1@mail.ru", "password": "pass"}' -s -v | jq .
```
Аналогично можно под любого, для которого уже задали e-mail и пароль

### Просмотр профилей (2.4)
Любой клиент может посмотреть профили пользователей:

```(bash)
curl "localhost:8000/user/info/?user_id=1"  -s | jq .
curl "localhost:8000/user/info/?user_id=3"  -s | jq .
curl "localhost:8000/user/info/?user_id=7"  -s | jq .
```

Однако, `'education_form'` -- основа обучения -- будет доступна только залогиненному пользователю и только по его user_id:
```(bash)
curl "localhost:8000/user/info/?user_id=1" -H 'Cookie: user_id="2|1:0|10:1579058987|7:user_id|4:MQ==|61e11a966bbca819dc88d23355138006e9e219a9669ef2ab632dd724ff0eed7c"; expires=Fri, 14 Feb 2020 03:29:47 GMT; Path=/"' -s | jq .
{
  "status": "ok",
  "info": {
    "education_form": "budget",
    "group_name": "595",
    "entry_year": 2015,
    "degree": "bachelor",
    "user_id": 1,
    "role": "student",
    "email": "u1@mail.ru",
    "name": "user1",
  }
}
```
 
### Редактирование профиля (2.3)
Пользователь с кукой может отредактировать
в своем профиле поля согласно 2.3, например, номер телефона:
```(bash)
curl "localhost:8000/user/info/" -X POST --data '{"update": {"telephone": "+79990001122"}}' -H 'Cookie: __YOUR_COOKIE__'
```

### Просмотр списка одногрупников (2.5)
```(bash)
curl "localhost:8000/user/classmates/"  -H 'Cookie: __YOUR_COOKIE__'

{
  "status": "ok",
  "classmates": [
    {
      "user_id": 2,
      "name": "user2"
    },
    {
      "user_id": 3,
      "name": "user3"
    }
  ]
}
```

### Просмотр списка курсов (2.6)

```(bash)
curl "localhost:8000/user/courses/"  -H 'Cookie: ...' -s | jq .
{
  "status": "ok",
  "courses": [
    {
      "course_id": 1,
      "name": "CV"
    },
    {
      "course_id": 2,
      "name": "ALGO"
    }
  ]
}
```

### Просмотр курса (2.7)
```(bash)
curl --location --request GET 'localhost:8000/course/info?course_id=1' -H 'Cookie: ...' -s | jq .
```
```(bash)
{
    "status": "ok",
    "info": {
        "course_id": 1,
        "name": "CV",
        "description": "computer vision",
        "professors": [
            {
                "user_id": 6,
                "name": "professor6",
                "email": null
            },
            {
                "user_id": 7,
                "name": "professor7",
                "email": null
            }
        ],
        "editors": [
            {
                "email": null,
                "name": "user4",
                "user_id": 4
            }
        ],
        "materials": [
            {
                "name": "CV_seminar1",
                "course_id": 1,
                "description": "jupiter_notebook from seminar1",
                "add_time": "2020-05-17"
            },
            {
                "name": "CV_seminar2",
                "course_id": 1,
                "description": "jupiter_notebook from seminar2",
                "add_time": "2020-05-17"
            }
        ],
        "assignees": [
            {
                "name": "cv_task1",
                "course_id": [
                    1
                ],
                "description": "CV task1",
                "start_time": "2020-01-01 00:00:00",
                "end_time": "2020-07-01 00:00:00"
            }
        ]
    }
}
```

### Управление материалами курса (2.8)
Пока не реализовано, только напрямую через БД

### Управление доверенными лицами (2.9)
Пока не реализовано, только напрямую через БД

#### Управление домашними заданиями курса (2.10)
Пока не реализовано, только напрямую через БД

#### Загрузка решения домашнего задания (2.11)
```(bash)
curl --location --request POST 'localhost:8000/assignee/submit/?assignee_name=cv_task1' --data-raw '{
	"solution": "Super mega solution"
}'
```
```(json)
{
    "status": "ok",
    "result": {
        "submission_time": "2020-05-18 02:00:42.885974"
    }
}
```

#### Просмотр решений домашнего задания (2.12)
```(bash)
curl --location --request GET 'localhost:8000/course/assignees?assignee_name=cv_task1&course_id=1' -H 'Cookie: ...' -s | jq .
```
```(json)
{
    "result": "ok",
    "assignees": {
        "595": [
            {
                "user_id": 1,
                "group_name": "595",
                "email": "u1@mail.ru",
                "name": "user1",
                "submition": {
                    "submit_time": "2020-05-17 22:25:46.291134"
                }
            },
            {
                "user_id": 2,
                "group_name": "595",
                "email": null,
                "name": "user2",
                "submition": {
                    "submit_time": "2020-05-18 00:00:00"
                }
            },
            {
                "user_id": 3,
                "group_name": "595",
                "email": "u3@mail.ru",
                "name": "user3",
                "submition": null
            }
        ],
        "596": [
            {
                "user_id": 4,
                "group_name": "596",
                "email": null,
                "name": "user4",
                "submition": null
            },
            {
                "user_id": 5,
                "group_name": "596",
                "email": null,
                "name": "user5",
                "submition": null
            }
        ]
    }
}
```

## DEV
> #### hint
> Для быстроты разработки, секцию web в docker-compose следует закомментить, 
> далее собираем в venv:
>
> `pip install -r requirements.txt`
>
> `python3 setup.py install`
>
> Теперь можно запускать так:
> 
> `python3 lms/client.py `
>
> Или использовать Pycharm для запуска

Собираем докер образы:

```(bash)
docker-compose up
```

Подключиться к DB:
```(bash)
psql -h localhost  -U admin -d lms_db
```

Чтобы создать/заполнить базы:
```(bash)
python lms/infra/db/manage_tables/execute_script.py --script lms/infra/db/manage_tables/sql_scripts/create_tables.sql
python lms/infra/db/manage_tables/execute_script.py --script lms/infra/db/manage_tables/sql_scripts/fill_tables.sql
```

Готово
