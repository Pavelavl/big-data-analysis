#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Задача 2: Работа с данными (pandas-версия как альтернатива PySpark)
Практическая работа №1

Данные: Nashville Housing (из Лабораторной работы 1)

Примечание: Для работы PySpark требуется Java и переменная JAVA_HOME.
Эта версия использует pandas для демонстрации тех же операций.
"""

import os
import sys

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LAB1_DIR = os.path.join(BASE_DIR, "labs", "lab1")
CSV_PATH = os.path.join(LAB1_DIR, "Nashville Housing.csv")

print("=" * 60)
print("ЗАДАЧА 2: РАБОТА С ДАННЫМИ (PANDAS-ВЕРСИЯ)")
print("=" * 60)
print("\nПримечание: Для PySpark требуется Java с JAVA_HOME.")
print("Эта версия использует pandas для тех же операций.\n")

# ============================================================================
# 1. Загрузка данных из CSV
# ============================================================================

print("1. Загрузка данных из CSV...")

# Загрузка исходного CSV
df = pd.read_csv(CSV_PATH, encoding="utf-8")

print(f"  Загружено строк: {len(df):,}")
print(f"  Столбцов: {len(df.columns)}")

# ----------------------------------------------------------------------------
# 2. Проверка типов данных и значений
# ----------------------------------------------------------------------------

print("\n2. Проверка типов данных:")
print(df.dtypes)

print("\nПример данных:")
print(df.head())

print("\nСтатистика по числовым столбцам:")
print(df.describe())

# ----------------------------------------------------------------------------
# 3. Создание DataFrame для таблиц (аналог реляционной структуры)
# ----------------------------------------------------------------------------

print("\n3. Создание DataFrame для реляционной структуры...")

# parcels - участки
parcels_df = df[[
    "ParcelID", "LandUse", "Acreage", "TaxDistrict"
]].drop_duplicates(subset=["ParcelID"]).copy()
parcels_df.columns = ["parcel_id", "land_use", "acreage", "tax_district"]

print(f"  parcels_df: {len(parcels_df):,} записей")

# addresses - адреса
addresses_df = df[[
    "ParcelID", "PropertyAddress", "OwnerAddress"
]].drop_duplicates(subset=["ParcelID", "PropertyAddress", "OwnerAddress"]).copy()
addresses_df.columns = ["parcel_id", "property_address", "owner_address"]

print(f"  addresses_df: {len(addresses_df):,} записей")

# properties - характеристики недвижимости
properties_df = df[[
    "ParcelID", "LandValue", "BuildingValue", "TotalValue",
    "YearBuilt", "Bedrooms", "FullBath", "HalfBath"
]].drop_duplicates(subset=["ParcelID"]).copy()
properties_df.columns = [
    "parcel_id", "land_value", "building_value", "total_value",
    "year_built", "bedrooms", "full_bath", "half_bath"
]

print(f"  properties_df: {len(properties_df):,} записей")

# owners - владельцы
owners_df = df[[
    "OwnerName"
]].dropna(subset=["OwnerName"]).drop_duplicates(subset=["OwnerName"]).copy()
owners_df.columns = ["owner_name"]
owners_df = owners_df.reset_index(drop=True)
owners_df["owner_id"] = owners_df.index + 1

print(f"  owners_df: {len(owners_df):,} записей")

# sales - продажи
sales_df = df[[
    "ParcelID", "OwnerName", "SaleDate", "SalePrice",
    "SoldAsVacant", "LegalReference"
]].copy()
sales_df.columns = [
    "parcel_id", "owner_name", "sale_date", "sale_price",
    "sold_as_vacant", "legal_reference"
]
# Очистка цен от валютных символов
sales_df["sale_price"] = sales_df["sale_price"].astype(str).str.replace(
    r'[$,\s]', '', regex=True
).replace('', None).astype(float)

# Объединение с owner_id
sales_df = sales_df.merge(
    owners_df[["owner_name", "owner_id"]],
    on="owner_name",
    how="left"
)
# Drop owner_name to avoid column conflicts in later merges
sales_df = sales_df.drop(columns=["owner_name"])
sales_df = sales_df.dropna(subset=["sale_price"])

print(f"  sales_df: {len(sales_df):,} записей")

# ============================================================================
# 4. SQL-запросы с pandas (по заданию - запросы 1-4)
# ============================================================================

print("\n" + "=" * 60)
print("SQL-ЗАПРОСЫ (РЕАЛИЗАЦИЯ ЧЕРЕЗ PANDAS)")
print("=" * 60)

# Сохраняем результаты для вывода в файл
results_output = []

def execute_pandas_query(query_num, description, result_df):
    """Выполнение pandas операции и вывод результатов"""
    print(f"\n{'=' * 60}")
    print(f"ЗАПРОС {query_num}: {description}")
    print(f"{'=' * 60}")

    count = len(result_df)
    print(f"Всего записей: {count:,}")
    print("\nРезультат (первые 15 записей):")
    print(result_df.head(15).to_string(index=False))

    # Сохраняем результат
    results_output.append({
        "query_num": query_num,
        "description": description,
        "count": count,
        "columns": list(result_df.columns),
        "sample_results": result_df.head(10).values.tolist()
    })

    return result_df

# ----------------------------------------------------------------------------
# Запрос 1: SELECT с JOIN по двум таблицам с сортировкой и агрегацией
# ----------------------------------------------------------------------------

query1 = parcels_df.merge(
    sales_df,
    left_on="parcel_id",
    right_on="parcel_id",
    how="left"
).dropna(subset=["sale_price"])

query1 = query1.groupby(
    ["parcel_id", "land_use", "tax_district"]
).agg(
    total_sales=("sale_price", "count"),
    avg_sale_price=("sale_price", "mean"),
    min_sale_price=("sale_price", "min"),
    max_sale_price=("sale_price", "max"),
    total_sales_value=("sale_price", "sum")
).reset_index()

query1 = query1.sort_values("total_sales_value", ascending=False).head(20)

execute_pandas_query(1, "JOIN по двум таблицам (parcels + sales) с сортировкой и агрегацией", query1)

# ----------------------------------------------------------------------------
# Запрос 2: SELECT с JOIN по трем таблицам с сортировкой и агрегацией
# ----------------------------------------------------------------------------

query2 = parcels_df.merge(
    properties_df,
    on="parcel_id",
    how="inner"
).merge(
    sales_df,
    on="parcel_id",
    how="inner"
)

query2 = query2[
    (query2["sale_price"] > 0) & (query2["total_value"] > 0)
].copy()

query2["price_to_value_ratio"] = (
    query2["sale_price"] / query2["total_value"] * 100
)

query2 = query2.groupby(
    ["parcel_id", "year_built", "land_use"]
).agg(
    sales_count=("sale_price", "count"),
    avg_sale_price=("sale_price", "mean"),
    avg_total_value=("total_value", "mean"),
    price_to_value_ratio=("price_to_value_ratio", "mean")
).reset_index()

query2 = query2.sort_values("avg_sale_price", ascending=False).head(15)

execute_pandas_query(2, "JOIN по трем таблицам (parcels + properties + sales) с сортировкой и агрегацией", query2)

# ----------------------------------------------------------------------------
# Запрос 3: Запрос по одному объекту по всем таблицам с JOIN и агрегацией
# ----------------------------------------------------------------------------

target_parcel = "119 05 0 186.00"

query3 = parcels_df[parcels_df["parcel_id"] == target_parcel].merge(
    addresses_df,
    on="parcel_id",
    how="left"
).merge(
    properties_df,
    on="parcel_id",
    how="left"
).merge(
    sales_df,
    on="parcel_id",
    how="left"
).merge(
    owners_df,
    on="owner_id",
    how="left"
)

query3 = query3.groupby([
    "parcel_id", "land_use", "acreage", "tax_district",
    "property_address", "owner_address", "land_value",
    "building_value", "total_value", "year_built",
    "bedrooms", "full_bath", "half_bath", "owner_name"
]).agg(
    total_sales=("sale_price", "count"),
    avg_sale_price=("sale_price", "mean"),
    first_sale_date=("sale_date", "min"),
    last_sale_date=("sale_date", "max"),
    total_sales_amount=("sale_price", "sum")
).reset_index()

execute_pandas_query(3, f"Запрос по объекту {target_parcel} по всем таблицам с JOIN и агрегацией", query3)

# ----------------------------------------------------------------------------
# Запрос 4: Подсчет количества строк по совмещенным данным в 2 таблицах
# ----------------------------------------------------------------------------

query4 = parcels_df.merge(
    addresses_df,
    on="parcel_id",
    how="left"
).merge(
    sales_df,
    on="parcel_id",
    how="left"
)

query4 = query4.groupby("land_use").agg(
    unique_parcels=("parcel_id", "nunique"),
    unique_addresses=("parcel_id", lambda x: len(set(x))),
    total_sales=("sale_price", "count"),
    avg_sale_price=("sale_price", "mean")
).reset_index()

query4 = query4.sort_values("unique_parcels", ascending=False)

execute_pandas_query(4, "Подсчет количества строк по совмещенным данным (parcels + addresses + sales)", query4)

# ============================================================================
# 5. Сохранение результатов в файл (append mode)
# ============================================================================

results_file = os.path.join(os.path.dirname(__file__), "report.md")

with open(results_file, 'a', encoding='utf-8') as f:
    f.write("\n\n")
    f.write("=" * 80 + "\n")
    f.write("РЕЗУЛЬТАТЫ PANDAS ЗАПРОСОВ - ЗАДАЧА 2 (PANDAS-ВЕРСИЯ)\n")
    f.write("=" * 80 + "\n\n")

    for result in results_output:
        f.write(f"{'=' * 80}\n")
        f.write(f"ЗАПРОС {result['query_num']}: {result['description']}\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(f"Столбцы: {', '.join(result['columns'])}\n")
        f.write(f"Всего записей: {result['count']:,}\n\n")
        f.write(f"Пример результатов (первые 10):\n")
        f.write("-" * 80 + "\n")

        for row in result['sample_results']:
            f.write(" | ".join(str(x) if x is not None else "NULL" for x in row) + "\n")

        f.write("\n\n")

print(f"Результаты добавлены в: {results_file}")

print("\n" + "=" * 60)
print("ЗАДАЧА 2 ВЫПОЛНЕНА УСПЕШНО (PANDAS-ВЕРСИЯ)")
print("=" * 60)
print("\nДля запуска PySpark-версии:")
print("1. Установите Java (8, 11 или 17)")
print("2. Настройте переменную JAVA_HOME")
print("3. Запустите: python task2_pyspark.py")
