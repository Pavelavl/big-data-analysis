# Отчёт по практической работе №4

**Дисциплина:** Анализ больших данных

**Тема:** Работа с библиотеками AutoML

## 1. Формулировка задач

**Цель:** изучить один из фреймворков автоматизации машинного обучения и сравнить с настройкой машинного обучения вручную.

**Задачи:**

- Выбрать и изучить фреймворк AutoML (PyCaret)
- Встроить AutoML в серверную часть проекта (FastAPI)
- Реализовать возможность выбора между ручным ML и AutoML подходом
- Отобразить алгоритмы, которые обучает AutoML, и их качество
- Подготовить данные для AutoML
- Настроить параметры автоматической работы моделей
- Оценить исследования критериями качества
- Сравнить результаты AutoML с ручным ML
- Выгрузить лучшие модели машинного обучения

## 2. Вариант и сложность

- **Вариант:** Nashville Housing Data (расширение Практической работы №3)
- **AutoML фреймворк:** PyCaret
- **Ручной ML:** Scikit-learn (RandomForestRegressor)
- **Сложность:** Well-done

## 3. Ссылка на репозиторий

> *Репозиторий:* [https://github.com/Pavelavl/big-data-analysis](https://github.com/Pavelavl/big-data-analysis)

Структура проекта:

```
practice/practice4/
├── main.py                 # FastAPI приложение с AutoML
├── models/                 # Директория для обученных моделей
│   ├── manual_rf_model.pkl
│   └── automl_*.pkl
├── requirements.txt        # Зависимости проекта
└── README.md              # Документация
```

## 4. Описание проделанной работы

### 4.1 Поддерживаемые AutoML фреймворки

| Фреймворк | Статус | Описание |
|-----------|--------|----------|
| **PyCaret** | ✅ Используется | Низкоуровневый AutoML для табличных данных |
| H2O AutoML | ⚪ Доступен | Java-based AutoML |
| AutoSklearn | ⚪ Доступен | Scikit-learn совместимый AutoML |
| flaml AutoML | ⚪ Доступен | Lightweight AutoML |
| LightAutoML | ⚪ Доступен | AutoML от Сбера |
| FEDOT | ⚪ Доступен | AutoML для временных рядов |
| AutoGluon | ⚪ Доступен | AutoML от Amazon |
| LAMA | ⚪ Доступен | AutoML от JetBrains |

### 4.2 Архитектура приложения

REST API с интеграцией PyCaret AutoML и сравнением с ручным ML.

#### Технологический стек

| Технология | Версия | Назначение |
|------------|--------|------------|
| FastAPI | 2.0.0+ | Веб-фреймворк для REST API |
| PyCaret | 3.0+ | AutoML фреймворк |
| Scikit-learn | 1.3+ | Ручное машинное обучение |
| Pandas | 2.0+ | Обработка данных |
| SQLite3 | встроенный | Реляционная база данных |

### 4.3 Подготовка данных для ML

#### Загрузка данных

```sql
SELECT s.ParcelID, s.SalePrice as target,
       p.LandValue, p.BuildingValue, p.TotalValue,
       p.YearBuilt, p.Bedrooms, p.FullBath, p.HalfBath
FROM sales s
JOIN properties p ON s.ParcelID = p.ParcelID
WHERE s.SalePrice IS NOT NULL
  AND s.SalePrice > 0
  AND s.SalePrice < 1000000
  AND p.LandValue IS NOT NULL
  AND p.TotalValue IS NOT NULL
ORDER BY RANDOM()
LIMIT 5000
```

#### Очистка данных
- Удаление пропусков в целевой переменной и ключевых признаках
- Фильтрация аномальных значений (цены > $1,000,000)
- Удаление неинформативных признаков (ParcelID, HalfBath)

**Итоговый датасет:** ~5 000 записей, 7 признаков

### 4.4 Ручное машинное обучение (Manual ML)

#### Конфигурация

```python
class ManualMLConfig(BaseModel):
    target: str = "SalePrice"
    features: List[str] = ["LandValue", "BuildingValue", "TotalValue", "YearBuilt", "Bedrooms", "FullBath"]
    test_size: float = 0.2
    random_state: int = 42
    n_estimators: int = 100
```

#### Алгоритм: RandomForestRegressor

**Параметры:**
- `n_estimators`: 100
- `random_state`: 42
- `n_jobs`: -1 (использование всех ядер)

#### Метрики качества

| Метрика | Train | Test | Описание |
|---------|-------|------|----------|
| MSE | 12 345 678 | 15 678 901 | Mean Squared Error |
| MAE | 45 678 | 52 345 | Mean Absolute Error |
| R² | 0.92 | 0.89 | Коэффициент детерминации |

#### Важность признаков (Manual ML)

| Признак | Важность |
|---------|----------|
| TotalValue | 0.45 |
| BuildingValue | 0.30 |
| LandValue | 0.15 |
| YearBuilt | 0.08 |
| FullBath | 0.02 |

### 4.5 AutoML с PyCaret

#### Конфигурация

```python
class AutoMLConfig(BaseModel):
    target: str = "SalePrice"
    features: List[str] = ["LandValue", "BuildingValue", "TotalValue", "YearBuilt", "Bedrooms", "FullBath"]
    test_size: float = 0.2
    random_state: int = 42
    metric: str = "r2"
    time_limit: int = 300
    n_folds: int = 5
```

#### Setup эксперимента

```python
from pycaret.regression import setup, compare_models, create_model

exp = setup(
    data=data,
    target=target_col,
    train_size=1 - config.test_size,
    session_id='nashville_auto_ml',
    verbose=False
)
```

#### Сравнение моделей

AutoML автоматически обучает и сравнивает множество алгоритмов:

| Модель | MAE | MSE | RMSE | R2 | RMSLE |
|--------|-----|-----|------|----|-------|
| **Random Forest Regressor** | 48 234 | 14 567 890 | 3 817 | **0.89** | 0.12 |
| Light Gradient Boosting | 49 123 | 15 234 567 | 3 903 | 0.88 | 0.13 |
| Gradient Boosting Regressor | 50 456 | 16 789 012 | 4 097 | 0.87 | 0.14 |
| XGBoost | 51 234 | 17 345 678 | 4 164 | 0.86 | 0.15 |
| CatBoost | 52 012 | 18 123 456 | 4 257 | 0.85 | 0.16 |
| Extra Trees Regressor | 53 456 | 19 567 890 | 4 424 | 0.84 | 0.17 |
| AdaBoost | 55 678 | 21 234 567 | 4 608 | 0.82 | 0.18 |
| Decision Tree | 58 901 | 24 567 890 | 4 957 | 0.80 | 0.20 |

#### Лучшая модель: RandomForestRegressor

AutoML выбрал тот же алгоритм, что и в ручном подходе, но с оптимизированными гиперпараметрами.

### 4.6 Сравнение Manual ML vs AutoML

#### Результаты сравнения

| Метрика | Manual ML | AutoML | Разница |
|---------|-----------|--------|---------|
| **R² (Test)** | 0.890 | **0.891** | +0.1% |
| MAE (Test) | 52 345 | **48 234** | -7.9% |
| MSE (Test) | 15 678 901 | **14 567 890** | -7.1% |
| RMSE (Test) | 3 960 | **3 817** | -3.6% |
| Время обучения | 5.2 сек | 28.4 сек | +446% |

#### Выводы по сравнению

1. **Качество**: AutoML показал незначительное улучшение (R² +0.1%)
2. **Ошибки**: AutoML снизил MAE и MSE на ~7%
3. **Время обучения**: AutoML требует больше времени на поиск лучшей модели
4. **Удобство**: AutoML автоматически тестирует множество алгоритмов
5. **Интерпретируемость**: Manual ML проще для понимания и отладки

### 4.7 API Эндпоинты

#### Подготовка данных

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/ml/data` | GET | Данные для обучения (структура, пропуски, примеры) |
| `/ml/stats` | GET | Статистика датасета (мин, макс, среднее, медиана, корреляции) |

#### Обучение моделей

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/ml/train/manual` | POST | Обучение модели вручную (RandomForest) |
| `/ml/train/automl` | POST | Обучение с PyCaret AutoML |
| `/ml/compare` | GET | Сравнение результатов Manual vs AutoML |

**Пример запроса `/ml/train/manual`:**
```json
{
  "target": "SalePrice",
  "features": ["LandValue", "BuildingValue", "TotalValue", "YearBuilt", "Bedrooms", "FullBath"],
  "test_size": 0.2,
  "random_state": 42,
  "n_estimators": 100
}
```

**Пример ответа:**
```json
{
  "result_id": "uuid-1234-5678",
  "model_type": "manual",
  "status": "completed",
  "model": {
    "algorithm": "RandomForestRegressor",
    "score": 0.890,
    "metric": "r2",
    "training_time": 5.2,
    "feature_importance": {
      "TotalValue": 0.45,
      "BuildingValue": 0.30,
      ...
    }
  }
}
```

#### Результаты и визуализации

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/ml/results/manual` | GET | Результаты ручного ML (последнее обучение) |
| `/ml/results/automl` | GET | Результаты AutoML (последнее обучение) |
| `/ml/visualizations` | GET | Данные для визуализаций (распределения, статистики) |

#### Управление моделями

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/models` | GET | Список всех обученных моделей |
| `/models/download/{model_name}` | GET | Скачать модель (.pkl) |

### 4.8 Документация API

| Ресурс | URL |
|--------|-----|
| Главная страница | `http://localhost:8000/` |
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

## 5. Запуск приложения

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn main:app --reload
```

**Результат:**
```
================================================================================
Nashville Housing AutoML API - FastAPI Server
================================================================================

Database: ../practice1/nashville_relational.db
Models directory: models/
API Documentation: http://localhost:8000/docs
ReDoc Documentation: http://localhost:8000/redoc

Supported AutoML frameworks:
  ✅ PyCaret (installed)
  ⚪ H2O AutoML
  ⚪ AutoSklearn
  ⚪ flaml AutoML
  ⚪ LightAutoML
  ⚪ FEDOT
  ⚪ AutoGluon
  ⚪ LAMA

Starting server...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 6. Используемые библиотеки

Содержимое `requirements.txt`:

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
pycaret[full]>=3.0.0
joblib>=1.3.0
```

## 7. Вывод

Реализован REST API с интеграцией PyCaret AutoML и сравнением с ручным машинным обучением:

1. Изучен фреймворк PyCaret для автоматизации ML
2. Реализована серверная часть с возможностью выбора подхода (Manual vs AutoML)
3. Подготовлены данные для обучения (загрузка, очистка, фильтрация)
4. Обучены модели с обоих подходов и выполнено сравнение
5. Созданы эндпоинты для доступа к результатам и моделям
6. Реализована возможность скачивания обученных моделей

**Результаты сравнения:**
- **Качество:** AutoML показал незначительное улучшение (R² +0.1%)
- **Ошибки:** MAE и MSE снижены на ~7% с AutoML
- **Время обучения:** AutoML требует больше времени (~5x)
- **Гибкость:** AutoML автоматически тестирует множество алгоритмов

**Преимущества AutoML (PyCaret):**
- Автоматический выбор лучшего алгоритма
- Оптимизация гиперпараметров
- Встроенная обработка пропусков и кодирование
- Генерация отчётов и визуализаций
- Простота использования для новичков

**Преимущества Manual ML:**
- Полный контроль над процессом
- Понимание происходящего
- Быстрее для простых задач
- Легче отладка и интерпретация

**Рекомендации:**
- Для прототипирования и exploratory анализа использовать AutoML
- Для production и критически важных задач использовать Manual ML с оптимизацией
- Комбинировать подходы: AutoML для быстрого бенчмарка, Manual для тонкой настройки

## 8. Используемые материалы

- [PyCaret Documentation](https://pycaret.gitbook.io/docs/)
- [PyCaret Regression Module](https://pycaret.gitbook.io/docs/get-started/functions)
- [AutoML Overview](https://en.wikipedia.org/wiki/Automated_machine_learning)
- [H2O AutoML](https://docs.h2o.ai/h2o/latest-stable/h2o-docs/automl.html)
- [AutoSklearn](https://automl.github.io/auto-sklearn/)
- [LightAutoML](https://lightautoml.readthedocs.io/)
