# Bookmark API 🔖

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

**Bookmark API** — небольшое приложение для хранения полезных ссылок. Можно сохранить учебный материал, добавить тег и быстро найти нужную запись. Интерфейс работает с JSON API через `fetch`, без перезагрузки страницы.

## Возможности

- 🔖 Добавление ссылок с названием и тегом
- 🔎 Фильтрация по тегу
- 🗑️ Удаление записей
- Проверка URL и защита от дубликатов
- Сохранение коллекции в SQLite

## Стек

- Python 3.12, Flask 3.1
- SQLite через встроенный модуль `sqlite3`
- HTML/CSS, JavaScript
- Gunicorn, Docker / Docker Compose

## Как это работает

- Flask обрабатывает запросы и возвращает JSON
- SQLite хранит записи; запросы выполняются напрямую, без ORM
- JavaScript отправляет запросы через `fetch` и обновляет список
- `create_app` создаёт приложение и позволяет передать отдельную базу для тестов

Значения передаются в SQL через параметры. Уникальность ссылки проверяется ограничением базы, а текст в интерфейсе выводится через `textContent`.

## Быстрый старт

### 1. Локальный запуск

В каталоге проекта выполните:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Откройте [http://127.0.0.1:5000/](http://127.0.0.1:5000/). Файл `bookmarks.sqlite3` создаётся автоматически. Другой путь к базе можно задать через переменную окружения `DATABASE_PATH`.

### 2. Запуск через Docker Compose

```bash
docker compose up --build
```

Приложение будет доступно по тому же адресу. База сохраняется в Docker volume. Для остановки нажмите `Ctrl+C`.

Сервис рассчитан на личное локальное использование: авторизации и разделения записей между пользователями пока нет. Порт в Compose открыт только на localhost.

## Основные запросы API

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/api/bookmarks` | Все закладки, новые сверху |
| `GET` | `/api/bookmarks?tag=python` | Закладки с указанным тегом |
| `POST` | `/api/bookmarks` | Добавить закладку |
| `DELETE` | `/api/bookmarks/1` | Удалить закладку по ID |

Пример добавления:

```bash
curl -i http://127.0.0.1:5000/api/bookmarks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Python docs","url":"https://docs.python.org/3/","tag":"python"}'
```

При создании возвращается `201`, при удалении — `204`. Неправильные данные дают `400`, отсутствующая запись — `404`, повторная ссылка — `409`.

Название ограничено 150 символами, ссылка — 2000, тег — 40. Поддерживаются HTTP(S)-ссылки. Теги при сохранении приводятся к нижнему регистру.

## Структура проекта

```text
├── app.py                   # приложение, API и SQL-запросы
├── templates/
│   └── index.html           # страница коллекции
├── static/
│   └── app.js               # запросы к API и обновление интерфейса
├── test_app.py              # тесты API
├── requirements.txt
├── Dockerfile
└── compose.yaml
```

## Разработка

```bash
python -m unittest -v
```

Тесты используют временную SQLite-базу. Проверяются добавление, фильтрация, удаление, дубликаты, валидация и сохранение данных после пересоздания приложения.
