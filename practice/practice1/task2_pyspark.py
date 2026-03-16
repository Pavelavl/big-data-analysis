#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Задача 2: Работа с фреймворком PySpark
Практическая работа №1

Данные: Nashville Housing (из Лабораторной работы 1)
"""

import os
import sys

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Импорт PySpark
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import (
        col, count, avg, min as spark_min, max as spark_max, sum as spark_sum,
        round as spark_round, desc, asc, lit, stddev, when, countDistinct
    )
    from pyspark.sql.types import (
        IntegerType, StringType, DoubleType, TimestampType, DateType
    )
except ImportError as e:
    print(f"Ошибка: PySpark не установлен. Выполните: pip install pyspark")
    print(f"Детали: {e}")
    sys.exit(1)

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LAB1_DIR = os.path.join(BASE_DIR, "labs", "lab1")
CSV_PATH = os.path.join(LAB1_DIR, "Nashville Housing.csv")

print("=" * 60)
print("ЗАДАЧА 2: РАБОТА С PYSPARK")
print("=" * 60)

# ============================================================================
# 1. Создание SparkSession
# ============================================================================

print("\n1. Инициализация SparkSession...")

spark = SparkSession.builder \
    .appName("NashvilleHousingAnalysis") \
    .config("spark.sql.warehouse.dir", os.path.join(os.path.dirname(__file__), "spark-warehouse")) \
    .getOrCreate()

print("  SparkSession создан")

# ============================================================================
# 2. Загрузка данных из CSV
# ============================================================================

print("\n2. Загрузка данных из CSV...")

# Загрузка исходного CSV
df = spark.read.csv(
    CSV_PATH,
    header=True,
    inferSchema=True,
    encoding="UTF-8"
)

print(f"  Загружено строк: {df.count():,}")
print(f"  Столбцов: {len(df.columns)}")

# ----------------------------------------------------------------------------
# 3. Проверка типов данных и значений
# ----------------------------------------------------------------------------

print("\n3. Проверка типов данных:")

df.printSchema()

print("\nПример данных:")
df.show(5, truncate=False)

print("\nСтатистика по числовым столбцам:")
df.describe().show()

# ----------------------------------------------------------------------------
# 4. Создание DataFrame для таблиц (аналог реляционной структуры)
# ----------------------------------------------------------------------------

print("\n4. Создание DataFrame для реляционной структуры...")

# Отбор и переименование столбцов для каждой "таблицы"

# parcels - участки
parcels_df = df.select(
    col("ParcelID").alias("parcel_id"),
    col("LandUse").alias("land_use"),
    col("Acreage").alias("acreage"),
    col("TaxDistrict").alias("tax_district")
).dropDuplicates(["parcel_id"])

print(f"  parcels_df: {parcels_df.count():,} записей")

# addresses - адреса
addresses_df = df.select(
    col("ParcelID").alias("parcel_id"),
    col("PropertyAddress").alias("property_address"),
    col("OwnerAddress").alias("owner_address")
).dropDuplicates(["parcel_id", "property_address", "owner_address"])

print(f"  addresses_df: {addresses_df.count():,} записей")

# properties - характеристики недвижимости
properties_df = df.select(
    col("ParcelID").alias("parcel_id"),
    col("LandValue").alias("land_value"),
    col("BuildingValue").alias("building_value"),
    col("TotalValue").alias("total_value"),
    col("YearBuilt").alias("year_built"),
    col("Bedrooms").alias("bedrooms"),
    col("FullBath").alias("full_bath"),
    col("HalfBath").alias("half_bath")
).dropDuplicates(["parcel_id"])

print(f"  properties_df: {properties_df.count():,} записей")

# owners - владельцы
owners_df = df.select(
    col("OwnerName").alias("owner_name")
).filter(col("OwnerName").isNotNull()).dropDuplicates(["owner_name"])

# Добавляем owner_id
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

window = Window.orderBy("owner_name")
owners_df = owners_df.withColumn("owner_id", row_number().over(window))

owners_df = owners_df.select(
    col("owner_id").cast(IntegerType()),
    col("owner_name")
)

print(f"  owners_df: {owners_df.count():,} записей")

# sales - продажи
# Создаем отображение owner_name -> owner_id
owners_map = owners_df.select("owner_name", "owner_id").collect()
owners_dict = {row["owner_name"]: row["owner_id"] for row in owners_map}

from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

get_owner_id = udf(lambda name: owners_dict.get(name) if name else None, IntegerType())

sales_df = df.select(
    col("ParcelID").alias("parcel_id"),
    col("OwnerName").alias("owner_name"),
    col("SaleDate").alias("sale_date"),
    col("SalePrice").alias("sale_price"),
    col("SoldAsVacant").alias("sold_as_vacant"),
    col("LegalReference").alias("legal_reference")
).filter(col("sale_price").isNotNull())

sales_df = sales_df.withColumn("owner_id", get_owner_id(col("owner_name")))

print(f"  sales_df: {sales_df.count():,} записей")

# Кеширование для ускорения запросов
parcels_df.cache()
addresses_df.cache()
properties_df.cache()
owners_df.cache()
sales_df.cache()

# ============================================================================
# 5. SQL-запросы с PySpark (по заданию - запросы 1-4)
# ============================================================================

print("\n" + "=" * 60)
print("SPARK SQL ЗАПРОСЫ К БАЗЕ ДАННЫХ")
print("=" * 60)

# Регистрация временных представлений для SQL
parcels_df.createOrReplaceTempView("parcels")
addresses_df.createOrReplaceTempView("addresses")
properties_df.createOrReplaceTempView("properties")
owners_df.createOrReplaceTempView("owners")
sales_df.createOrReplaceTempView("sales")

# Сохраняем результаты для вывода в файл
results_output = []

def execute_spark_query(query_num, description, spark_df):
    """Выполнение Spark DataFrame операции и вывод результатов"""
    print(f"\n{'=' * 60}")
    print(f"ЗАПРОС {query_num}: {description}")
    print(f"{'=' * 60}")

    count = spark_df.count()
    print(f"Всего записей: {count:,}")
    print("\nРезультат (первые 15 записей):")
    spark_df.show(15, truncate=False)

    # Сохраняем результат
    rows = spark_df.collect()
    columns = spark_df.columns

    results_output.append({
        "query_num": query_num,
        "description": description,
        "count": count,
        "columns": columns,
        "sample_results": rows[:10]
    })

    return spark_df

# ----------------------------------------------------------------------------
# Запрос 1: SELECT с JOIN по двум таблицам с сортировкой и агрегацией
# ----------------------------------------------------------------------------

query1 = parcels_df.join(
    sales_df,
    parcels_df["parcel_id"] == sales_df["parcel_id"],
    "left"
).filter(sales_df["sale_price"].isNotNull()) \
 .groupBy(
    parcels_df["parcel_id"],
    parcels_df["land_use"],
    parcels_df["tax_district"]
 ).agg(
    count("sale_price").alias("total_sales"),
    spark_round(avg("sale_price"), 2).alias("avg_sale_price"),
    spark_round(spark_min("sale_price"), 2).alias("min_sale_price"),
    spark_round(spark_max("sale_price"), 2).alias("max_sale_price"),
    spark_round(spark_sum("sale_price"), 2).alias("total_sales_value")
 ).orderBy(col("total_sales_value").desc()) \
 .limit(20)

execute_spark_query(1, "JOIN по двум таблицам (parcels + sales) с сортировкой и агрегацией", query1)

# ----------------------------------------------------------------------------
# Запрос 2: SELECT с JOIN по трем таблицам с сортировкой и агрегацией
# ----------------------------------------------------------------------------

query2 = parcels_df.join(
    properties_df,
    parcels_df["parcel_id"] == properties_df["parcel_id"],
    "inner"
).join(
    sales_df,
    parcels_df["parcel_id"] == sales_df["parcel_id"],
    "inner"
).filter((sales_df["sale_price"] > 0) & (properties_df["total_value"] > 0)) \
 .groupBy(
    parcels_df["parcel_id"],
    properties_df["year_built"],
    parcels_df["land_use"]
 ).agg(
    count("sale_price").alias("sales_count"),
    spark_round(avg("sale_price"), 2).alias("avg_sale_price"),
    spark_round(avg("total_value"), 2).alias("avg_total_value"),
    spark_round(avg("sale_price") / avg("total_value") * 100, 2).alias("price_to_value_ratio")
 ).orderBy(col("avg_sale_price").desc()) \
 .limit(15)

execute_spark_query(2, "JOIN по трем таблицам (parcels + properties + sales) с сортировкой и агрегацией", query2)

# ----------------------------------------------------------------------------
# Запрос 3: Запрос по одному объекту по всем таблицам с JOIN и агрегацией
# ----------------------------------------------------------------------------

target_parcel = "119 05 0 186.00"

query3 = parcels_df.filter(parcels_df["parcel_id"] == target_parcel) \
 .join(
    addresses_df,
    parcels_df["parcel_id"] == addresses_df["parcel_id"],
    "left"
 ).join(
    properties_df,
    parcels_df["parcel_id"] == properties_df["parcel_id"],
    "left"
 ).join(
    sales_df,
    parcels_df["parcel_id"] == sales_df["parcel_id"],
    "left"
 ).join(
    owners_df,
    sales_df["owner_id"] == owners_df["owner_id"],
    "left"
 ).groupBy(
    parcels_df["parcel_id"],
    parcels_df["land_use"],
    parcels_df["acreage"],
    parcels_df["tax_district"],
    addresses_df["property_address"],
    addresses_df["owner_address"],
    properties_df["land_value"],
    properties_df["building_value"],
    properties_df["total_value"],
    properties_df["year_built"],
    properties_df["bedrooms"],
    properties_df["full_bath"],
    properties_df["half_bath"],
    owners_df["owner_name"]
 ).agg(
    count("sale_price").alias("total_sales"),
    spark_round(avg("sale_price"), 2).alias("avg_sale_price"),
    spark_min("sale_date").alias("first_sale_date"),
    spark_max("sale_date").alias("last_sale_date"),
    spark_round(spark_sum("sale_price"), 2).alias("total_sales_amount")
 )

execute_spark_query(3, f"Запрос по объекту {target_parcel} по всем таблицам с JOIN и агрегацией", query3)

# ----------------------------------------------------------------------------
# Запрос 4: Подсчет количества строк по совмещенным данным в 2 таблицах
# ----------------------------------------------------------------------------

query4 = parcels_df.join(
    addresses_df,
    parcels_df["parcel_id"] == addresses_df["parcel_id"],
    "left"
).join(
    sales_df,
    parcels_df["parcel_id"] == sales_df["parcel_id"],
    "left"
).groupBy(
    parcels_df["land_use"]
).agg(
    countDistinct(parcels_df["parcel_id"]).alias("unique_parcels"),
    countDistinct(addresses_df["parcel_id"]).alias("unique_addresses"),
    count("sale_price").alias("total_sales"),
    spark_round(avg("sale_price"), 2).alias("avg_sale_price")
).orderBy(col("unique_parcels").desc())

execute_spark_query(4, "Подсчет количества строк по совмещенным данным (parcels + addresses + sales)", query4)

# ============================================================================
# 6. Сохранение результатов в файл
# ============================================================================

results_file = os.path.join(os.path.dirname(__file__), "report.md")

with open(results_file, '"a"', encoding='"utf-8"') as f:
    f.write("
    f.write("РЕЗУЛЬТАТЫ PYSPARK ЗАПРОСОВ - ЗАДАЧА 2
    f.write("=" * 80 + "

")
")

")
    f.write("=" * 80 + "\n")
    f.write("РЕЗУЛЬТАТЫ PYSPARK ЗАПРОСОВ - ЗАДАЧА 2\n")
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

print(f"Результаты сохранены: {results_file}")

# ============================================================================
# 7. Закрытие SparkSession
# ============================================================================

print("\n" + "=" * 60)
print("ЗАДАЧА 2 ВЫПОЛНЕНА УСПЕШНО")
print("=" * 60)

spark.stop()

print("SparkSession закрыт")
