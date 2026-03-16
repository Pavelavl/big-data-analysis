#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Задача 1: Создание базы данных и работа с реляционными СУБД (SQLite3)
Практическая работа №1

Данные: Nashville Housing (из Лабораторной работы 1)
"""

import sqlite3
import csv
import os
import sys

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LAB1_DIR = os.path.join(BASE_DIR, "labs", "lab1")
CSV_PATH = os.path.join(LAB1_DIR, "Nashville Housing.csv")
DB_PATH = os.path.join(os.path.dirname(__file__), "nashville_relational.db")

print("=" * 60)
print("ЗАДАЧА 1: СОЗДАНИЕ БАЗЫ ДАННЫХ И РАБОТА С РСУБД")
print("=" * 60)

# ============================================================================
# 1. Создание реляционной базы данных с несколькими таблицами
# ============================================================================

print("\n1. Создание реляционной структуры базы данных...")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"  Удалена старая БД: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Таблица 1: Участки (parcels)
cursor.execute("""
    CREATE TABLE parcels (
        ParcelID TEXT PRIMARY KEY,
        LandUse TEXT,
        Acreage REAL,
        TaxDistrict TEXT
    )
""")

# Таблица 2: Адреса (addresses)
cursor.execute("""
    CREATE TABLE addresses (
        AddressID INTEGER PRIMARY KEY AUTOINCREMENT,
        ParcelID TEXT,
        PropertyAddress TEXT,
        OwnerAddress TEXT,
        FOREIGN KEY (ParcelID) REFERENCES parcels(ParcelID)
    )
""")

# Таблица 3: Характеристики недвижимости (properties)
cursor.execute("""
    CREATE TABLE properties (
        PropertyID INTEGER PRIMARY KEY AUTOINCREMENT,
        ParcelID TEXT,
        LandValue REAL,
        BuildingValue REAL,
        TotalValue REAL,
        YearBuilt INTEGER,
        Bedrooms INTEGER,
        FullBath INTEGER,
        HalfBath INTEGER,
        FOREIGN KEY (ParcelID) REFERENCES parcels(ParcelID)
    )
""")

# Таблица 4: Владельцы (owners)
cursor.execute("""
    CREATE TABLE owners (
        OwnerID INTEGER PRIMARY KEY AUTOINCREMENT,
        OwnerName TEXT
    )
""")

# Таблица 5: Продажи (sales)
cursor.execute("""
    CREATE TABLE sales (
        SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
        ParcelID TEXT,
        OwnerID INTEGER,
        SaleDate TEXT,
        SalePrice REAL,
        SoldAsVacant TEXT,
        LegalReference TEXT,
        FOREIGN KEY (ParcelID) REFERENCES parcels(ParcelID),
        FOREIGN KEY (OwnerID) REFERENCES owners(OwnerID)
    )
""")

print("  Таблицы созданы: parcels, addresses, properties, owners, sales")

# ============================================================================
# 2. Загрузка данных из CSV в реляционную структуру
# ============================================================================

print("\n2. Загрузка данных из CSV...")

# Словари для отслеживания уникальных значений
owners_cache = {}  # owner_name -> owner_id
property_cache = {}  # parcel_id -> property_id

with open(CSV_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for idx, row in enumerate(reader):
        parcel_id = row.get("ParcelID", "").strip()
        land_use = row.get("LandUse", "").strip()
        acreage_str = row.get("Acreage", "").strip()
        tax_district = row.get("TaxDistrict", "").strip()
        property_address = row.get("PropertyAddress", "").strip()
        owner_address = row.get("OwnerAddress", "").strip()
        land_value_str = row.get("LandValue", "").strip()
        building_value_str = row.get("BuildingValue", "").strip()
        total_value_str = row.get("TotalValue", "").strip()
        year_built_str = row.get("YearBuilt", "").strip()
        bedrooms_str = row.get("Bedrooms", "").strip()
        full_bath_str = row.get("FullBath", "").strip()
        half_bath_str = row.get("HalfBath", "").strip()
        owner_name = row.get("OwnerName", "").strip()
        sale_date = row.get("SaleDate", "").strip()
        sale_price_str = row.get("SalePrice", "").strip()
        sold_as_vacant = row.get("SoldAsVacant", "").strip()
        legal_reference = row.get("LegalReference", "").strip()

        # Парсинг числовых значений (функция для очистки числовых строк)
        def parse_float(value_str):
            if not value_str:
                return None
            # Удаляем $ , и пробелы
            cleaned = value_str.replace('$', '').replace(',', '').replace(' ', '').strip()
            if not cleaned:
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None

        acreage = parse_float(acreage_str)
        land_value = parse_float(land_value_str)
        building_value = parse_float(building_value_str)
        total_value = parse_float(total_value_str)
        year_built = int(float(year_built_str)) if year_built_str and parse_float(year_built_str) is not None else None
        bedrooms = int(float(bedrooms_str)) if bedrooms_str and parse_float(bedrooms_str) is not None else None
        full_bath = int(float(full_bath_str)) if full_bath_str and parse_float(full_bath_str) is not None else None
        half_bath = int(float(half_bath_str)) if half_bath_str and parse_float(half_bath_str) is not None else None
        sale_price = parse_float(sale_price_str)

        # Вставка/получение владельца
        owner_id = None
        if owner_name:
            if owner_name not in owners_cache:
                cursor.execute("INSERT INTO owners (OwnerName) VALUES (?)", (owner_name,))
                owner_id = cursor.lastrowid
                owners_cache[owner_name] = owner_id
            else:
                owner_id = owners_cache[owner_name]

        # Вставка участка (если еще не существует)
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO parcels (ParcelID, LandUse, Acreage, TaxDistrict)
                VALUES (?, ?, ?, ?)
            """, (parcel_id, land_use, acreage, tax_district))
        except sqlite3.IntegrityError:
            pass  # Участок уже существует

        # Вставка адресов
        if property_address or owner_address:
            cursor.execute("""
                INSERT INTO addresses (ParcelID, PropertyAddress, OwnerAddress)
                VALUES (?, ?, ?)
            """, (parcel_id, property_address, owner_address))

        # Вставка характеристик (если есть данные)
        if land_value or building_value or total_value:
            if parcel_id not in property_cache:
                cursor.execute("""
                    INSERT INTO properties (ParcelID, LandValue, BuildingValue, TotalValue,
                                          YearBuilt, Bedrooms, FullBath, HalfBath)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (parcel_id, land_value, building_value, total_value,
                      year_built, bedrooms, full_bath, half_bath))
                property_cache[parcel_id] = cursor.lastrowid

        # Вставка продажи
        if sale_date:
            cursor.execute("""
                INSERT INTO sales (ParcelID, OwnerID, SaleDate, SalePrice, SoldAsVacant, LegalReference)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (parcel_id, owner_id, sale_date, sale_price, sold_as_vacant, legal_reference))

        if (idx + 1) % 10000 == 0:
            print(f"  Обработано записей: {idx + 1}")

conn.commit()
print("  Загрузка завершена")

# ============================================================================
# 3. Статистика базы данных
# ============================================================================

print("\n3. Статистика базы данных:")

tables = ["parcels", "addresses", "properties", "owners", "sales"]
for table in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {count:,} записей")

# ============================================================================
# 4. SQL-запросы (по заданию)
# ============================================================================

print("\n" + "=" * 60)
print("SQL-ЗАПРОСЫ К БАЗЕ ДАННЫХ")
print("=" * 60)

# Сохраняем результаты в файл
results_output = []

def execute_query(query_num, description, sql_query):
    """Выполнение SQL-запроса и вывод результатов"""
    print(f"\n{'=' * 60}")
    print(f"ЗАПРОС {query_num}: {description}")
    print(f"{'=' * 60}")
    print(f"SQL:\n{sql_query}\n")

    cursor.execute(sql_query)
    results = cursor.fetchall()

    # Получаем названия столбцов
    columns = [description[0] for description in cursor.description]
    print("Результат:")
    print(" | ".join(columns))
    print("-" * 80)

    for row in results[:10]:  # Показываем первые 10 записей
        print(" | ".join(str(x) if x is not None else "NULL" for x in row))

    if len(results) > 10:
        print(f"... и еще {len(results) - 10} записей")

    print(f"\nВсего записей: {len(results)}")

    # Сохраняем результат
    results_output.append({
        "query_num": query_num,
        "description": description,
        "sql": sql_query,
        "count": len(results),
        "columns": columns,
        "sample_results": results[:5]
    })

    return results

# ----------------------------------------------------------------------------
# Запрос 1: SELECT с JOIN по двум таблицам с сортировкой и агрегацией
# ----------------------------------------------------------------------------

query1 = """
SELECT
    p.ParcelID,
    p.LandUse,
    p.TaxDistrict,
    COUNT(s.SaleID) as TotalSales,
    ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
    ROUND(MIN(s.SalePrice), 2) as MinSalePrice,
    ROUND(MAX(s.SalePrice), 2) as MaxSalePrice,
    ROUND(SUM(s.SalePrice), 2) as TotalSalesValue
FROM parcels p
LEFT JOIN sales s ON p.ParcelID = s.ParcelID
WHERE s.SalePrice IS NOT NULL
GROUP BY p.ParcelID, p.LandUse, p.TaxDistrict
ORDER BY TotalSalesValue DESC
LIMIT 20;
"""

execute_query(1, "JOIN по двум таблицам (parcels + sales) с сортировкой и агрегацией", query1)

# ----------------------------------------------------------------------------
# Запрос 2: SELECT с JOIN по трем таблицам с сортировкой и агрегацией
# ----------------------------------------------------------------------------

query2 = """
SELECT
    p.ParcelID,
    prop.YearBuilt,
    p.LandUse,
    COUNT(s.SaleID) as SalesCount,
    ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
    ROUND(AVG(prop.TotalValue), 2) as AvgTotalValue,
    ROUND(AVG(s.SalePrice) / AVG(prop.TotalValue) * 100, 2) as PriceToValueRatio
FROM parcels p
JOIN properties prop ON p.ParcelID = prop.ParcelID
JOIN sales s ON p.ParcelID = s.ParcelID
WHERE s.SalePrice > 0 AND prop.TotalValue > 0
GROUP BY p.ParcelID, prop.YearBuilt, p.LandUse
HAVING SalesCount > 0
ORDER BY AvgSalePrice DESC
LIMIT 15;
"""

execute_query(2, "JOIN по трем таблицам (parcels + properties + sales) с сортировкой и агрегацией", query2)

# ----------------------------------------------------------------------------
# Запрос 3: Запрос по одному объекту по всем таблицам с JOIN и агрегацией
# ----------------------------------------------------------------------------

query3 = """
SELECT
    p.ParcelID,
    p.LandUse,
    p.Acreage,
    p.TaxDistrict,
    a.PropertyAddress,
    a.OwnerAddress,
    prop.LandValue,
    prop.BuildingValue,
    prop.TotalValue,
    prop.YearBuilt,
    prop.Bedrooms,
    prop.FullBath,
    prop.HalfBath,
    o.OwnerName,
    COUNT(s.SaleID) as TotalSales,
    ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
    MIN(s.SaleDate) as FirstSaleDate,
    MAX(s.SaleDate) as LastSaleDate,
    ROUND(SUM(s.SalePrice), 2) as TotalSalesAmount
FROM parcels p
LEFT JOIN addresses a ON p.ParcelID = a.ParcelID
LEFT JOIN properties prop ON p.ParcelID = prop.ParcelID
LEFT JOIN sales s ON p.ParcelID = s.ParcelID
LEFT JOIN owners o ON s.OwnerID = o.OwnerID
WHERE p.ParcelID = '119 05 0 186.00'
GROUP BY p.ParcelID, p.LandUse, p.Acreage, p.TaxDistrict, a.PropertyAddress,
         a.OwnerAddress, prop.LandValue, prop.BuildingValue, prop.TotalValue,
         prop.YearBuilt, prop.Bedrooms, prop.FullBath, prop.HalfBath, o.OwnerName;
"""

execute_query(3, "Запрос по одному объекту по всем таблицам с JOIN и агрегацией", query3)

# ----------------------------------------------------------------------------
# Запрос 4: Подсчет количества строк по совмещенным данным в 2 таблицах
# ----------------------------------------------------------------------------

query4 = """
SELECT
    p.LandUse,
    COUNT(DISTINCT p.ParcelID) as UniqueParcels,
    COUNT(DISTINCT a.AddressID) as UniqueAddresses,
    COUNT(s.SaleID) as TotalSales,
    ROUND(AVG(s.SalePrice), 2) as AvgSalePrice
FROM parcels p
LEFT JOIN addresses a ON p.ParcelID = a.ParcelID
LEFT JOIN sales s ON p.ParcelID = s.ParcelID
GROUP BY p.LandUse
ORDER BY UniqueParcels DESC;
"""

execute_query(4, "Подсчет количества строк по совмещенным данным (parcels + addresses + sales)", query4)

# ----------------------------------------------------------------------------
# Запрос 5.1: Сложный SELECT - Анализ цен по типу использования и налоговому округу
# ----------------------------------------------------------------------------

query5_1 = """
SELECT
    p.TaxDistrict,
    p.LandUse,
    COUNT(s.SaleID) as SalesCount,
    ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
    ROUND(MIN(s.SalePrice), 2) as MinSalePrice,
    ROUND(MAX(s.SalePrice), 2) as MaxSalePrice,
    ROUND(SUM(s.SalePrice), 2) as TotalValue,
    ROUND(SQRT(AVG(s.SalePrice * s.SalePrice) - AVG(s.SalePrice) * AVG(s.SalePrice)), 2) as StdDev
FROM parcels p
JOIN sales s ON p.ParcelID = s.ParcelID
WHERE s.SalePrice > 0
GROUP BY p.TaxDistrict, p.LandUse
HAVING SalesCount >= 10
ORDER BY AvgSalePrice DESC;
"""

execute_query(5.1, "Анализ цен по налоговому округу и типу использования", query5_1)

# ----------------------------------------------------------------------------
# Запрос 5.2: Сложный SELECT - Владельцы с наибольшим количеством продаж
# ----------------------------------------------------------------------------

query5_2 = """
SELECT
    o.OwnerName,
    COUNT(s.SaleID) as PropertiesSold,
    COUNT(DISTINCT s.ParcelID) as UniqueParcels,
    ROUND(SUM(s.SalePrice), 2) as TotalSalesValue,
    ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
    ROUND(MIN(s.SalePrice), 2) as MinSalePrice,
    ROUND(MAX(s.SalePrice), 2) as MaxSalePrice
FROM owners o
JOIN sales s ON o.OwnerID = s.OwnerID
WHERE s.SalePrice > 0
GROUP BY o.OwnerName, o.OwnerID
HAVING PropertiesSold >= 2
ORDER BY TotalSalesValue DESC
LIMIT 20;
"""

execute_query(5.2, "Владельцы с наибольшим количеством продаж", query5_2)

# ----------------------------------------------------------------------------
# Запрос 5.3: Сложный SELECT - Анализ года постройки и стоимости
# ----------------------------------------------------------------------------

query5_3 = """
WITH DecadeCategories AS (
    SELECT
        prop.ParcelID,
        prop.YearBuilt,
        CASE
            WHEN prop.YearBuilt < 1900 THEN 'Before 1900'
            WHEN prop.YearBuilt < 1920 THEN '1900-1919'
            WHEN prop.YearBuilt < 1940 THEN '1920-1939'
            WHEN prop.YearBuilt < 1960 THEN '1940-1959'
            WHEN prop.YearBuilt < 1980 THEN '1960-1979'
            WHEN prop.YearBuilt < 2000 THEN '1980-1999'
            ELSE '2000+'
        END as Decade,
        prop.TotalValue,
        prop.Bedrooms
    FROM properties prop
    WHERE prop.YearBuilt IS NOT NULL AND prop.TotalValue IS NOT NULL
)
SELECT
    Decade,
    COUNT(*) as PropertiesCount,
    ROUND(AVG(TotalValue), 2) as AvgTotalValue,
    ROUND(AVG(Bedrooms), 2) as AvgBedrooms,
    ROUND(MIN(TotalValue), 2) as MinTotalValue,
    ROUND(MAX(TotalValue), 2) as MaxTotalValue
FROM DecadeCategories
GROUP BY Decade
ORDER BY Decade;
"""

execute_query(5.3, "Анализ постройки по десятилетиям (с CTE)", query5_3)

# ============================================================================
# 5. Экспорт дампа базы данных
# ============================================================================

print("\n" + "=" * 60)
print("ЭКСПОРТ ДАМПА БАЗЫ ДАННЫХ")
print("=" * 60)

dump_path = os.path.join(os.path.dirname(__file__), "nashville_relational_dump.sql")

# Создание дампа с использованием .dump команды SQLite
with open(dump_path, 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write('%s\n' % line)

print(f"Дамп сохранен: {dump_path}")

# ============================================================================
# 6. Сохранение результатов в файл
# ============================================================================

results_file = os.path.join(os.path.dirname(__file__), "report.md")

with open(results_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("РЕЗУЛЬТАТЫ SQL-ЗАПРОСОВ - ЗАДАЧА 1\n")
    f.write("=" * 80 + "\n\n")

    for result in results_output:
        f.write(f"{'=' * 80}\n")
        f.write(f"ЗАПРОС {result['query_num']}: {result['description']}\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(f"SQL:\n{result['sql']}\n\n")
        f.write(f"Столбцы: {', '.join(result['columns'])}\n")
        f.write(f"Всего записей: {result['count']}\n\n")
        f.write(f"Пример результатов (первые 5):\n")
        f.write("-" * 80 + "\n")

        for row in result['sample_results']:
            f.write(" | ".join(str(x) if x is not None else "NULL" for x in row) + "\n")

        f.write("\n\n")

print(f"Результаты сохранены: {results_file}")

# ============================================================================
# 7. Закрытие соединения
# ============================================================================

conn.close()

print("\n" + "=" * 60)
print("ЗАДАЧА 1 ВЫПОЛНЕНА УСПЕШНО")
print("=" * 60)
print(f"База данных: {DB_PATH}")
print(f"Дамп: {dump_path}")
print(f"Результаты: {results_file}")
