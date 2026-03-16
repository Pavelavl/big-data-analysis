# Отчёт по практической работе №3

**Дисциплина:** Анализ больших данных

**Тема:** Работа с библиотекой FastAPI

## 1. Формулировка задач

**Цель:** отделить функционал проекта от отображения и реализовать серверную часть на FastAPI.

**Задачи:**

- Разработать REST API на базе FastAPI
- Реализовать эндпоинты для доступа к данным из реляционной базы
- Создать API для работы с моделями машинного обучения
- Обеспечить CORS поддержку для фронтенда
- Сгенерировать интерактивную документацию (Swagger, ReDoc)
- Реализовать скачивание файлов проекта (отчёт, база данных)

## 2. Вариант и сложность

- **Вариант:** Nashville Housing Data (серверная часть для Практической работы №1)
- **Библиотека:** FastAPI 1.0.0
- **Сложность:** Medium

## 3. Ссылка на репозиторий

> *Репозиторий:* [https://github.com/Pavelavl/big-data-analysis](https://github.com/Pavelavl/big-data-analysis)

Структура проекта:

```
practice/practice3/
├── main.py                 # FastAPI приложение
├── requirements.txt        # Зависимости проекта
└── README.md              # Документация
```

## 4. Описание проделанной работы

### 4.1 Архитектура приложения

REST API реализован с использованием FastAPI — современного веб-фреймворка для создания API на Python.

#### Технологический стек

| Технология | Версия | Назначение |
|------------|--------|------------|
| FastAPI | 1.0.0+ | Веб-фреймворк для создания REST API |
| Uvicorn | 0.24.0+ | ASGI-сервер для запуска приложения |
| Pydantic | 2.0+ | Валидация данных |
| SQLite3 | встроенный | Реляционная база данных |
| Pandas | 2.0+ | Обработка данных |

### 4.2 Эндпоинты API

#### Корневая страница и документация

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/` | GET | Корневая страница с HTML-документацией |
| `/docs` | GET | Интерактивная документация Swagger UI |
| `/redoc` | GET | Документация ReDoc |

#### Эндпоинты статистики

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/stats` | GET | Статистика базы данных (количество записей в каждой таблице) |

**Пример ответа:**
```json
{
  "parcels": 48559,
  "addresses": 50638,
  "properties": 22432,
  "owners": 19713,
  "sales": 56477,
  "total_records": 197819
}
```

#### Эндпоинты таблиц данных

| Эндпоинт | Метод | Параметры | Описание |
|----------|-------|-----------|----------|
| `/parcels` | GET | limit, offset, land_use | Получение всех участков |
| `/parcels/{parcel_id}` | GET | - | Участок по ID |
| `/addresses` | GET | limit, offset | Получение всех адресов |
| `/properties` | GET | limit, offset, min_year | Характеристики недвижимости |
| `/owners` | GET | limit, offset, name_filter | Все владельцы |
| `/sales` | GET | limit, offset, min_price, max_price | Все продажи |
| `/sales/parcel/{parcel_id}` | GET | - | Продажи конкретного участка |

**Пример запроса:**
```bash
GET /parcels?limit=10&offset=0&land_use=SINGLE%20FAMILY
```

**Пример ответа:**
```json
[
  {
    "ParcelID": "119 05 0 186.00",
    "LandUse": "SINGLE FAMILY",
    "Acreage": 0.34,
    "TaxDistrict": "URBAN SERVICES DISTRICT"
  }
]
```

#### Эндпоинты SQL-запросов

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/queries/query1` | GET | JOIN по двум таблицам с сортировкой и агрегацией |
| `/queries/query2` | GET | JOIN по трём таблицам |
| `/queries/query3` | GET | Детали по конкретному объекту |
| `/queries/query4` | GET | Группировка по типу использования |

**Пример ответа `/queries/query1`:**
```json
{
  "query": "SELECT p.ParcelID, p.LandUse, ...",
  "results": [...],
  "row_count": 20
}
```

#### Эндпоинты машинного обучения

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/ml/data` | GET | Данные для обучения (10 000 записей) |
| `/ml/stats` | GET | Статистика датасета для ML |

**Пример ответа `/ml/stats`:**
```json
{
  "total_samples": 22432,
  "features": ["SalePrice", "LandValue", "BuildingValue", "TotalValue", "YearBuilt", "Bedrooms", "FullBath", "HalfBath"],
  "correlations": {
    "SalePrice": {"TotalValue": 0.85, "YearBuilt": 0.45, ...}
  }
}
```

#### Эндпоинты файлов

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/files/report` | GET | Скачать отчёт (report.md) |
| `/files/database` | GET | Скачать базу данных (.db) |

### 4.3 Модели данных (Pydantic)

#### Модель Parcel
```python
class Parcel(BaseModel):
    ParcelID: str
    LandUse: Optional[str] = None
    Acreage: Optional[float] = None
    TaxDistrict: Optional[str] = None
```

#### Модель DatabaseStats
```python
class DatabaseStats(BaseModel):
    parcels: int
    addresses: int
    properties: int
    owners: int
    sales: int
    total_records: int
```

#### Модель QueryResult
```python
class QueryResult(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    row_count: int
```

### 4.4 CORS Middleware

Для поддержки фронтенда добавлен CORS middleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.5 Документация API

#### Swagger UI

Доступна по адресу: `http://localhost:8000/docs`

**Возможности:**
- Интерактивное тестирование всех эндпоинтов
- Автоматическая генерация схем запросов/ответов
- Поддержка авторизации (если требуется)
- Цветовая кодировка методов (GET — зелёный, POST — синий)

#### ReDoc

Доступна по адресу: `http://localhost:8000/redoc`

**Возможности:**
- Трёхколоночный дизайн для лучшей читаемости
- Подробное описание всех эндпоинтов
- Примеры запросов и ответов
- Возможность поиска

### 4.6 Структура кода

```python
# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================
app = FastAPI(...)

# ============================================================================
# МОДЕЛИ ДАННЫХ (Pydantic)
# ============================================================================
class Parcel(BaseModel): ...
class Address(BaseModel): ...

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================
def get_db_connection(): ...
def execute_query(query: str): ...

# ============================================================================
# API ENDPOINTS
# ============================================================================
@app.get("/stats") ...
@app.get("/parcels") ...

# ============================================================================
# ЗАПУСК СЕРВЕРА
# ============================================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

## 5. Запуск приложения

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn main:app --reload
```

**Результат:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Доступные ресурсы:**
- API: `http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 6. Используемые библиотеки

Содержимое `requirements.txt`:

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
```

## 7. Вывод

Реализована серверная часть REST API на базе FastAPI для работы с данными Nashville Housing:

1. Создан REST API с 15+ эндпоинтами
2. Реализована автоматическая документация (Swagger UI, ReDoc)
3. Обеспечена работа с реляционной базой данных SQLite3
4. Реализована валидация данных через Pydantic модели
5. Добавлена поддержка CORS для фронтенда
6. Созданы эндпоинты для работы с ML-данными
7. Реализована возможность скачивания файлов проекта

**Преимущества FastAPI:**
- Высокая производительность (на базе Starlette и Pydantic)
- Автоматическая генерация документации
- Поддержка асинхронного кода
- Встроенная валидация данных
- Легкая интеграция с другими библиотеками
- Типизация кода (type hints)

**Архитектурные решения:**
- Разделение concerns: слой API, слой данных, слой бизнес-логики
- Использование Pydantic для валидации входных/выходных данных
- Паттерн Dependency Injection (для подключения к БД)
- RESTful дизайн эндпоинтов
- Отделение бизнес-логики от слоя отображения

## 8. Используемые материалы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [REST API Design Best Practices](https://restfulapi.net/)
- [OpenAPI Specification](https://swagger.io/specification/)
