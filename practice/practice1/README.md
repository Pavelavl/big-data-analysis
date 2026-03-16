# Практическая работа №1
## Работа с РСУБД. PostgreSQL / SQLite3 + Python. pySpark фреймворк

**Данные:** Nashville Housing (из Лабораторной работы 1)

## Задача 1: Создание базы данных и работа с реляционными СУБД

### Структура базы данных

База данных содержит следующие таблицы с связями:

- **parcels** - Участки земли (Primary Key: ParcelID)
- **addresses** - Адреса (Primary Key: AddressID, Foreign Key: ParcelID)
- **properties** - Характеристики недвижимости (Foreign Key: ParcelID)
- **owners** - Владельцы (Primary Key: OwnerID)
- **sales** - Информация о продажах (Foreign Key: ParcelID, Foreign Key: OwnerID)

### Связи между таблицами

```
parcels (1) ---- (1) properties
   |
   +---- (1) ---- (N) addresses
   |
   +---- (1) ---- (N) sales ---- (N) owners
```

## Задача 2: Работа с pySpark

Те же запросы, что и в Задаче 1, но с использованием фреймворка PySpark.

**Примечание:** Для работы PySpark требуется Java 8, 11 или 17 с настроенной переменной JAVA_HOME.
Если Java не установлен, используйте task2_pandas.py (pandas-версия).

## Требования к установке

```bash
# Для SQLite (встроен в Python)
pip install pandas

# Для PostgreSQL (опционально)
pip install psycopg2-binary sqlalchemy

# Для PySpark (опционально, требует Java)
pip install pyspark
```

## Запуск

### Задача 1 (SQLite3 + Python)
```bash
cd practice/practice1
python task1_sqlite.py
```

### Задача 2 (pandas-версия, без Java)
```bash
cd practice/practice1
python task2_pandas.py
```

### Задача 2 (PySpark, требует Java)
```bash
cd practice/practice1
python task2_pyspark.py
```

## SQL-запросы

1. SELECT с JOIN по двум таблицам с сортировкой и агрегацией
2. SELECT с JOIN по трем таблицам с сортировкой и агрегацией
3. Запрос по одному объекту по всем таблицам с JOIN и агрегацией
4. Запрос для подсчета количества строк по совмещенным данным в 2 таблицах
5. Три сложных SELECT на выбор:
   - Анализ цен по налоговому округу и типу использования
   - Владельцы с наибольшим количеством продаж
   - Анализ постройки по десятилетиям (с CTE)

## Отчет

Результаты выполнения:
- `task1_sqlite.py` - Решение Задачи 1 (SQLite3 + Python)
- `task2_pandas.py` - Решение Задачи 2 (pandas-версия)
- `task2_pyspark.py` - Решение Задачи 2 (PySpark-версия)
- `report.md` - Общий отчет с результатами обоих задач
- `nashville_relational.db` - Реляционная база данных SQLite
- `nashville_relational_dump.sql` - Дамп базы данных
