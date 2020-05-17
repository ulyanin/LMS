# LMS

LMS (англ. _learning management system_) — [система управления обучением].

[система управления обучением]: https://ru.wikipedia.org/wiki/%D0%A1%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0_%D1%83%D0%BF%D1%80%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F_%D0%BE%D0%B1%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5%D0%BC

### §1. Административная часть

Эта часть без публичного интерфейса. Иными словами, для простоты мы будем считать, что сценарии использования системы администратором подразумевают прямое подключение к базе данных и редактирование имеющихся таблиц соответствующим образом.

#### §1.1. Создание учебной группы

Администратор может создать учебную группу, указав следующие данные:

- Имя группы
- Имя факультета
- Номер курса

#### §1.2. Создание учебного курса

Администратор может создать учебный курс, указав его название и текстовое описание.

##### §1.2.1. Запись группы на курс

Администратор может добавить учебную группу, которая проходит данный курс.

##### §1.2.2. Добавление преподавателя курса

Администратор может добавить преподавателя курса.

#### §1.3. Предварительная регистрация

Администратор может добавить предопределенного пользователя (студента или преподавателя) в систему, указав следующие обязательные данные:

- ФИО
- Только для студентов:
  - Учебная группа
  - Год поступления
  - Степень
  - Форма обучения
  - Основа обучения

Подразумевается следующее:
- Учебная группа у каждого студента ровно одна.
- Степени: бакалавр, специалист, магистр.
- Формы обучения: очная, заочная, вечерняя.
- Основа обучения: контрактная, бюджетная.

Для каждого пользователя также случайным образом генерируется верификационный код, позволяющий данному пользователю в дальнейшем зарегистрироваться в системе.

### §2. Публичное API

#### §2.1. Аутентификация

Пользователь может войти в систему по своему e-mail и паролю.

#### §2.2. Регистрация

Пользователь может зарегистрироваться в системе по коду регистрации, полученного от администратора. При регистрации пользователь указывает свой e-mail и пароль. Пароль должен быть достаточно безопасным.

#### §2.3. Просмотр и редактирование профиля

Пользователь может просмотреть и отредактировать свой профиль, в котором может содержаться следующая информация:

- Личная информация:
  - ФИО (не редактируемо)
  - E-mail (не редактируемо)
  - Телефон
  - Родной город
  - Информация о себе в текстовой форме
- Ссылки на профили в социальных сетях:
  - VK
  - Facebook
  - LinkedIn
  - Instagram
- Информация о получаемом образовании (не редактируемо, см. §1.3)

Пользователь также может сменить свой пароль, если знает старый.

#### §2.4. Просмотр профилей

Помимо своего личного профиля, пользователь также может просматривать профили других пользователей системы (если есть на него ссылка или идентификатор пользователя). Однако, основу обучения видеть другие пользователи не могут.

#### §2.5. Просмотр списка одногруппников

Студент может просматривать список своих одногруппников.

#### §2.6. Просмотр списка курсов

Пользователь может просматривать список своих курсов. Список курсов, на которые записан студент, определяется согласно его учебной группе. Список курсов, которые ведет преподаватель, определяется на основе информации §1.2.2.

#### §2.7. Просмотр курса

Пользователь может посмотреть информацию про любой курс:

- Название
- Описание
- Список ведущих курс преподавателей
- Список доверенных лиц
- Материалы курса
- Доступные домашние задания

#### §2.8. Управление материалами курса

Преподаватель курса и доверенные лица могут добавлять, модифицировать и удалять материалы курса.

Для простоты будем считать, что материал по курсу состоит из:
- Имени материала
- Текстового содержимого
- Даты добавления

#### §2.9. Управление доверенными лицами

Преподаватель может выбрать (как добавить, так и удалить) студентов, имеющих доступ к управлению материалами его курса, из списка слушающих курс студентов.

Доверенные лица («старосты») могут добавлять, модифицировать и удалять материалы курса наравне с преподавателем.

Доверенные лица не могут:
- управлять домашними заданиями и скачивать посылки других студентов
- добавлять других доверенных лиц

#### §2.10. Управление домашними заданиями курса

Преподаватель курса может добавить, модифицировать и удалить домашнее задание курса.

Домашнее задание состоит из:
- Названия
- Интервала времени сдачи
- Текстового описания задания

Предполагается, что студенты не видят домашнего задания до наступления времени сдачи и не могут сдать задание после его истечения.

#### §2.11. Загрузка решения домашнего задания

Студент, записанный на курс, может загрузить решение домашнего задания в течение интервала времени сдачи. Новая посылка решения отменяет предыдущую посылку. Для простоты будем считать, что решение задачи является обычным текстом.

#### §2.12. Просмотр решений домашнего задания

Преподаватель курса для каждого домашнего задания может просматривать список студентов, записанных на курс, сгруппированный по учебным группам, при этом для каждого студента известно, что он либо не отправлял решения, либо что он отправил решение в некоторое время. Также можно посмотреть текст отдельного решения.