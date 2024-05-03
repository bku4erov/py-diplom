# Дипломный проект профессии «Python-разработчик: расширенный курс»

## Backend-приложение для автоматизации закупок

### В рамках выполнения дипломной работы:
* изучен пример репозитория, взятый за основу
* выполнен ряд небольших изменений (СУБД SqlLite заменена на СУБД PostreSQL, настройки приложения вынесены в переменные окружения и т.д.)
* реализована продвинутная часть задания, в том числе:
   - реализован экспорт товаров
   - реализована админка заказов (проставление статуса заказа и уведомление клиента) (через REST API и через интерфейс админки Django)
   - выделены медленные методы в отдельные асинхронные функции (email, импорт, экспорт) через задачи Celery
   - создан docker-compose файла для приложения

Разработаны тесты, которыми покрыт основной функционал приложения.

Для демонстрации работы приложения доработан проект описания и тестирования REST API в Postman

Документация REST API в Postman доступна по следующей ссылке:

https://web.postman.co/workspace/85e82d55-d4e7-4e46-968e-3e76e79dd279/documentation/34578218-33690870-3589-448f-b1ca-e695a1e7d8bb

 Проект описания и тестирования REST API в Postman экспортирован в JSON-файл "netology-pd-diplom.postman_collection.json" данного репозитория, а также доступен по следующей ссылке:

https://web.postman.co/workspace/85e82d55-d4e7-4e46-968e-3e76e79dd279


### Инструкция для сборки docker-образа:

#### 1. Клонировать данный git-репозиторий:

```
git clone git@github.com:bku4erov/py-diplom.git
```

#### 2. Настроить следующие переменные окружения, необходимые для корректной работы приложения:

POSTGRES_DB - имя базы данных (БД)

POSTGRES_USER - имя пользователя БД

POSTGRES_PASSWORD - пароль пользователя БД


EMAIL_HOST - адрес SMTP-сервера электронной почты

EMAIL_USER - электронная почта

EMAIL_PASSWORD - пароль (для приложения) электронной почты 

EMAIL_PORT - порт SMTP-сервера электронной почты


DJANGO_SETTINGS_MODULE - путь к файлу настроек Django


Пример содержимого файла .env:
```
POSTGRES_DB=netology_py_diplom
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

EMAIL_HOST=smtp.mail.ru
EMAIL_USER=somemail@mail.ru
EMAIL_PASSWORD=somemailpasswordforapplication
EMAIL_PORT=465

DJANGO_SETTINGS_MODULE=netology_pd_diplom.settings
```

#### 3. Запустить docker-compose приложение (из корневой директории репозитория):
```
docker compose -f "docker-compose.yaml" up -d --build 
```

#### 4. После успешного запуска приложения (всех его контейнеров) приложение будет доступно на порту 8000 локального хоста.

Кроме того, будет доступен celery flower для контроля задач celery на порту 5555 локального хоста.

Адреса для доступа к приложению по умолчанию:

http://127.0.0.1:8000/api/v1/ - REST API

http://127.0.0.1:8000/admin/ - Django admin

http://127.0.0.1:5555/ - мониторинг задач Celery


## Задание на диплом по разработке Backend-приложения для автоматизации закупок

### Цель дипломного проекта

Создадите и настроите проект по автоматизации закупок в розничной сети, проработаете модели данных, импорт товаров, API views.

Вам нужно:

* разработать backend для сервиса заказа товаров,
* усовершенствовать навыки работы с Django ORM через проработку моделей товаров и связанных сущностей,
* реализовать импорт и экспорт товаров,
* внедрить систему управления заказами,
* оптимизировать методы с использованием асинхронности,
* освоить работу со сторонними библиотеками и фреймворками,
* подготовить документацию к проекту,
* использовать AI инструменты для решения задач.

-----

## Чеклист готовности к работе над проектом

1. Изучить материалы лекции подготовки к дипломной работе.
2. Подготовить компьютер или виртуальную машину с ОС Linux или MacOS (не рекомендуем использовать Windows).
3. Установить IDE с поддержкой Python: Pycharm, VS Code или др.
4. Установить версию Python 3.10 или более позднюю.
5. Установить AI-плагин из списка:
- [Machinet](https://www.machinet.net/),
- [Codeium](https://codeium.com/),
- [Tabnine](https://www.tabnine.com/),
- [Amazon Сodewhisperer](https://aws.amazon.com/ru/codewhisperer/),
- [Mutable.AI](https://mutable.ai/pricing/),
- [Google Duet-AI](https://cloud.google.com/duet-ai/docs/developers/use-in-ide).

-----

## Инструкция к работе над проектом

### Общее описание приложения

Приложение предназначено для автоматизации закупок в розничной сети через REST API.

**Внимание! Все взаимодействие с приложением ведется через API запросы. 
Реализация фронтенд-приложения возможна только по желанию обучающегося**

**Пользователи сервиса:**

1. Клиент (покупатель):

- делает ежедневные закупки по каталогу, в котором представлены товары от нескольких поставщиков,
- в одном заказе можно указать товары от разных поставщиков,
- пользователь может авторизироваться, регистрироваться и восстанавливать пароль через API.
    
2. Поставщик:

- через API информирует сервис об обновлении прайса,
- может включать и отключать приём заказов,
- может получать список оформленных заказов (с товарами из его прайса).

### Задача

Необходимо разработать backend-часть сервиса заказа товаров для розничных сетей на Django Rest Framework.

**Базовая часть:**
* разработка сервиса под готовую спецификацию (API),
* возможность добавления настраиваемых полей (характеристик) товаров,
* импорт товаров,
* отправка накладной на email администратора (для исполнения заказа),
* отправка заказа на email клиента (подтверждение приёма заказа).

**Продвинутая часть (необязательная к выполнению, не влияет на получение зачёта):**
* экспорт товаров,
* админка заказов (проставление статуса заказа и уведомление клиента),
* выделение медленных методов в отдельные асинхронные функции (email, импорт, экспорт).

_Обратите внимание!_

В репозитории приведён готовый пример с базовой частью проекта. Вы можете работать с проектом, выбрав один из двух вариантов:
- разработать свою версию, исходя из текстового описания базовой части проекта,
- взять за основу пример из репозитория, изучить его и выполнить продвинутую часть задания.

Вы можете интерпретировать текстовое описание проекта по-своему. Работа над дипломом - это в первую очередь творческий процесс. Главное - отсутствие плагиата (не сдавать работы других студентов).

### Исходные данные для проекта
 
1. Общее описание сервиса
1. [Спецификация (API) - 1 шт.](./reference/screens.md)
1. [Файлы yaml для импорта товаров - 1 шт.](./data/shop1.yaml)
1. [Базовый пример API Сервиса для магазина](./reference//netology_pd_diplom/) 

## Этапы разработки

Разработку backend рекомендуется разделить на следующие этапы.

**Базовая часть:**
1. [Создание и настройка проекта.](./reference/step-1.md)
2. [Проработка моделей данных.](./reference/step-2.md)
3. [Реализация импорта товаров.](./reference/step-3.md)
4. [Реализация API views.](./reference/step-4.md)
5. [Полностью готовый backend.](./reference/step-5.md)

**Продвинутая часть** (выполняется по желанию, если базовая часть полностью готова):

6. [Реализация forms и views админки склада.](./reference/step-6-adv.md)
7. [Вынос медленных методов в задачи Celery.](./reference/step-7-adv.md)
8. Создание docker-compose файла для приложения.


Разработку следует вести с использованием git (github/gitlab/bitbucket) с регулярными коммитами в репозиторий, доступный вашему дипломному руководителю. Старайтесь делать коммиты как можно чаще.

### Этап 1. Создание и настройка проекта

**Критерии достижения**

1. Вы имеете актуальный код данного репозитория на рабочем компьютере.
2. У вас создан Django-проект, и он запускается без ошибок.

Для получения подробностей по данному этапу
[перейдите по ссылке](./reference/step-1.md).

### Этап 2. Проработка моделей данных

**Критерии достижения**

1. Созданы модели и их дополнительные методы.

Для получения подробностей по данному этапу
[перейдите по ссылке](./reference/step-2.md).

### Этап 3. Реализация импорта товаров

**Критерии достижения**

1. Созданы функции загрузки товаров из приложенных файлов в модели Django.
2. Загружены товары из всех файлов для импорта.

Для получения подробностей по данному этапу
[перейдите по ссылке](./reference/step-3.md).

### Этап 4. Реализация APIViews

**Критерии достижения**

1. Реализованы API Views для основных [страниц](./reference/screens.md) сервиса (без админки):
   - Авторизация
   - Регистрация
   - Получение списка товаров
   - Получение спецификации по отдельному товару в базе данных
   - Работа с корзиной (добавление, удаление товаров)
   - Добавление/удаление адреса доставки
   - Подтверждение заказа
   - Отправка email c подтверждением
   - Получение  списка заказов
   - Получение деталей заказа
   - Редактирование статуса заказа

Для получения подробностей по данному этапу
[перейдите по ссылке](./reference/step-4.md).

### Этап 5. Полностью готовый backend

**Критерии достижения**

1. Полностью работающие API Endpoint'ы
2. Корректно отрабатывает следующий сценарий:
   - пользователь может авторизироваться,
   - есть возможность отправки данных для регистрации и получения email с подтверждением регистрации,
   - пользователь может добавлять в корзину товары от разных магазинов,
   - пользователь может подтверждать заказ с вводом адреса доставки,
   - пользователь получает email с подтверждением после ввода адреса доставки,
   - пользователь может переходить на страницу «‎Заказы» и открывать созданный заказ.

Для получения подробностей по данному этапу
[перейдите по ссылке](./reference/step-5.md).

## Полезные материалы

1. [Информация о сервисе](./reference/service.md)
2. [Спецификация API](./reference/api.md)
3. [Описание страниц сервиса](./reference/screens.md)

---

## Продвинутая часть (выполняется по желанию, не влияет на получение зачёта)

Обязательное условие: базовая часть проекта полностью готова.

### Этап 6. Реализация API views админки склада

**Критерии достижения**

1. Реализованы API views для [страниц админки](./reference/screens.md) сервиса.

Для получения подробностей по данному этапу
[перейдите по ссылке](reference/step-6-adv.md).

### Этап 7. Вынос медленных методов в задачи Celery

**Критерии достижения**

1. Создано Celery-приложение c методами:
   - send_email,
   - do_import.
2. Создан view для запуска Celery-задачи do_import из админки.

Для получения подробностей по данному этапу
[перейдите по ссылке](reference/step-7-adv.md).  

### Этап 8. Создание docker-compose файла для приложения
1. Создать docker-compose файл для сборки приложения.
2. Предоставить инструкцию для сборки docker-образа.

_Важно: не нарушайте дедлайн сдачи, возникающие вопросы задавайте в чате с дипломным руководителем._

-----

## Правила приёма дипломной работы

1. Проект разместить в GitHub. Ссылка на дипломную работу должна оставаться неизменной, чтобы дипломный руководитель мог видеть ваш прогресс.
2. Сдавать финальный вариант дипломной работы в личном кабинете Нетологии.

-----

## Критерии оценки

Зачёт по дипломной работе можно получить, если работа соответствует критериям:

* работоспособный проект в репозитории с документацией по запуску,
* выполненная базовая часть проекта,
* наличие собственных комментариев к коду,
* использование сторонних библиотек и фреймворков.
