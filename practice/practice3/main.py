#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Практическая работа 3: Работа с библиотекой FastAPI

Серверная часть для анализа данных Nashville Housing

Цель: отделить функционал проекта от отображения и реализовать серверную часть на FastAPI.
"""

import os
import sqlite3
import uvicorn
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

app = FastAPI(
    title="Nashville Housing API",
    description="REST API для анализа данных недвижимости в Нэшвилле",
    version="1.0.0"
)

# CORS для поддержки фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Пути к файлам
PRACTICE1_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "practice1")
DB_PATH = os.path.join(PRACTICE1_DIR, "nashville_relational.db")
REPORT_PATH = os.path.join(PRACTICE1_DIR, "report.md")

# ============================================================================
# МОДЕЛИ ДАННЫХ (Pydantic)
# ============================================================================

class Parcel(BaseModel):
    ParcelID: str
    LandUse: Optional[str] = None
    Acreage: Optional[float] = None
    TaxDistrict: Optional[str] = None

class Address(BaseModel):
    ParcelID: str
    PropertyAddress: Optional[str] = None
    OwnerAddress: Optional[str] = None

class Property(BaseModel):
    ParcelID: str
    LandValue: Optional[float] = None
    BuildingValue: Optional[float] = None
    TotalValue: Optional[float] = None
    YearBuilt: Optional[int] = None
    Bedrooms: Optional[int] = None
    FullBath: Optional[int] = None
    HalfBath: Optional[int] = None

class Owner(BaseModel):
    OwnerID: int
    OwnerName: str

class Sale(BaseModel):
    ParcelID: str
    OwnerID: Optional[int] = None
    SaleDate: Optional[str] = None
    SalePrice: Optional[float] = None
    SoldAsVacant: Optional[str] = None
    LegalReference: Optional[str] = None

class DatabaseStats(BaseModel):
    parcels: int
    addresses: int
    properties: int
    owners: int
    sales: int
    total_records: int

class QueryResult(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    row_count: int

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def get_db_connection():
    """Создание соединения с базой данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query: str) -> List[Dict[str, Any]]:
    """Выполнение SQL-запроса"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

# ============================================================================
# КОРНЕВАЯ СТРАНИЦА И ДОКУМЕНТАЦИЯ
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Корневая страница с документацией API"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nashville Housing API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            h2 { color: #555; margin-top: 30px; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
            .endpoint h3 { margin-top: 0; color: #007bff; }
            .method { display: inline-block; padding: 3px 10px; margin-right: 10px; border-radius: 4px; font-weight: bold; }
            .GET { background: #28a745; color: white; }
            .POST { background: #007bff; color: white; }
            code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>🏠 Nashville Housing API</h1>
        <p>REST API для анализа данных недвижимости в Нэшвилле, штат Теннесси</p>

        <h2>Документация API</h2>

        <div class="endpoint">
            <h3>📊 Общая информация</h3>
            <p>Получение статистики базы данных</p>
            <p><span class="method GET">GET</span> <code>/stats</code></p>
        </div>

        <div class="endpoint">
            <h3>📁 Таблицы данных</h3>
            <p>Получение всех записей из таблиц</p>
            <p><span class="method GET">GET</span> <code>/parcels</code> - Все участки</p>
            <p><span class="method GET">GET</span> <code>/addresses</code> - Все адреса</p>
            <p><span class="method GET">GET</span> <code>/properties</code> - Все характеристики недвижимости</p>
            <p><span class="method GET">GET</span> <code>/owners</code> - Все владельцы</p>
            <p><span class="method GET">GET</span> <code>/sales</code> - Все продажи</p>
        </div>

        <div class="endpoint">
            <h3>🔍 Детальная информация</h3>
            <p>Получение информации по конкретному ID</p>
            <p><span class="method GET">GET</span> <code>/parcels/{parcel_id}</code> - Участок по ID</p>
            <p><span class="method GET">GET</span> <code>/sales/parcel/{parcel_id}</code> - Продажи участка</p>
        </div>

        <div class="endpoint">
            <h3>📈 SQL-запросы</h3>
            <p>Выполнение предопределённых SQL-запросов</p>
            <p><span class="method GET">GET</span> <code>/queries/query1</code> - JOIN по двум таблицам</p>
            <p><span class="method GET">GET</span> <code>/queries/query2</code> - JOIN по трём таблицам</p>
            <p><span class="method GET">GET</span> <code>/queries/query3</code> - Детали по объекту</p>
            <p><span class="method GET">GET</span> <code>/queries/query4</code> - Группировка по типу</p>
        </div>

        <div class="endpoint">
            <h3>🤖️ Машинное обучение</h3>
            <p>API для обучения и прогнозирования</p>
            <p><span class="method GET">GET</span> <code>/ml/data</code> - Данные для обучения</p>
            <p><span class="method GET">GET</span> <code>/ml/stats</code> - Статистика датасета</p>
        </div>

        <div class="endpoint">
            <h3>📄 Файлы</h3>
            <p>Скачать файлы проекта</p>
            <p><span class="method GET">GET</span> <code>/files/report</code> - Отчёт (report.md)</p>
            <p><span class="method GET">GET</span> <code>/files/database</code> - База данных (.db)</p>
        </div>

        <h2>Дополнительные ресурсы</h2>
        <ul>
            <li><a href="/docs">Интерактивная документация Swagger</a></li>
            <li><a href="/redoc">Документация ReDoc</a></li>
        </ul>
    </body>
    </html>
    """

# ============================================================================
# API ENDPOINTS: СТАТИСТИКА
# ============================================================================

@app.get("/stats", response_model=DatabaseStats)
async def get_database_stats():
    """Получение статистики базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {
        "parcels": cursor.execute("SELECT COUNT(*) FROM parcels").fetchone()[0],
        "addresses": cursor.execute("SELECT COUNT(*) FROM addresses").fetchone()[0],
        "properties": cursor.execute("SELECT COUNT(*) FROM properties").fetchone()[0],
        "owners": cursor.execute("SELECT COUNT(*) FROM owners").fetchone()[0],
        "sales": cursor.execute("SELECT COUNT(*) FROM sales").fetchone()[0],
    }
    stats["total_records"] = sum(stats.values())

    conn.close()
    return stats

# ============================================================================
# API ENDPOINTS: ТАБЛИЦЫ ДАННЫХ
# ============================================================================

@app.get("/parcels", response_model=List[Parcel])
async def get_parcels(
    limit: int = Query(100, description="Лимит записей", le=1000),
    offset: int = Query(0, description="Смещение", ge=0),
    land_use: Optional[str] = Query(None, description="Фильтр по типу использования")
):
    """Получение всех участков"""
    query = "SELECT * FROM parcels"
    params = []

    if land_use:
        query += " WHERE LandUse = ?"
        params.append(land_use)

    query += " ORDER BY ParcelID LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]

@app.get("/parcels/{parcel_id}", response_model=Parcel)
async def get_parcel(parcel_id: str):
    """Получение участка по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parcels WHERE ParcelID = ?", (parcel_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="Участок не найден")

    return dict(result)

@app.get("/addresses", response_model=List[Address])
async def get_addresses(
    limit: int = Query(100, description="Лимит записей", le=1000),
    offset: int = Query(0, description="Смещение", ge=0)
):
    """Получение всех адресов"""
    query = "SELECT * FROM addresses ORDER BY ParcelID LIMIT ? OFFSET ?"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, [limit, offset])
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]

@app.get("/properties", response_model=List[Property])
async def get_properties(
    limit: int = Query(100, description="Лимит записей", le=1000),
    offset: int = Query(0, description="Смещение", ge=0),
    min_year: Optional[int] = Query(None, description="Минимальный год постройки")
):
    """Получение всех характеристик недвижимости"""
    query = "SELECT * FROM properties"
    params = []

    if min_year:
        query += " WHERE YearBuilt >= ?"
        params.append(min_year)

    query += " ORDER BY ParcelID LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]

@app.get("/owners", response_model=List[Owner])
async def get_owners(
    limit: int = Query(100, description="Лимит записей", le=1000),
    offset: int = Query(0, description="Смещение", ge=0),
    name_filter: Optional[str] = Query(None, description="Фильтр по имени владельца")
):
    """Получение всех владельцев"""
    query = "SELECT * FROM owners"
    params = []

    if name_filter:
        query += " WHERE OwnerName LIKE ?"
        params.append(f"%{name_filter}%")

    query += " ORDER BY OwnerName LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]

@app.get("/sales", response_model=List[Sale])
async def get_sales(
    limit: int = Query(100, description="Лимит записей", le=1000),
    offset: int = Query(0, description="Смещение", ge=0),
    min_price: Optional[float] = Query(None, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, description="Максимальная цена")
):
    """Получение всех продаж"""
    query = "SELECT * FROM sales"
    params = []

    conditions = []
    if min_price is not None:
        conditions.append("SalePrice >= ?")
        params.append(min_price)
    if max_price is not None:
        conditions.append("SalePrice <= ?")
        params.append(max_price)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY SalePrice DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]

@app.get("/sales/parcel/{parcel_id}", response_model=List[Sale])
async def get_sales_by_parcel(parcel_id: str):
    """Получение всех продаж для конкретного участка"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sales WHERE ParcelID = ? ORDER BY SaleDate",
        (parcel_id,)
    )
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]

# ============================================================================
# API ENDPOINTS: SQL-ЗАПРОСЫ
# ============================================================================

@app.get("/queries/query1", response_model=QueryResult)
async def query1():
    """JOIN по двум таблицам с сортировкой и агрегацией"""
    query = """
    SELECT p.ParcelID, p.LandUse, p.TaxDistrict,
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
    results = execute_query(query)
    return QueryResult(query=query, results=results, row_count=len(results))

@app.get("/queries/query2", response_model=QueryResult)
async def query2():
    """JOIN по трём таблицам с сортировкой и агрегацией"""
    query = """
    SELECT p.ParcelID, prop.YearBuilt, p.LandUse,
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
    results = execute_query(query)
    return QueryResult(query=query, results=results, row_count=len(results))

@app.get("/queries/query3", response_model=QueryResult)
async def query3():
    """Запрос по одному объекту по всем таблицам с JOIN и агрегацией"""
    query = """
    SELECT p.ParcelID, p.LandUse, p.Acreage, p.TaxDistrict,
           a.PropertyAddress, a.OwnerAddress,
           prop.LandValue, prop.BuildingValue, prop.TotalValue,
           prop.YearBuilt, prop.Bedrooms, prop.FullBath, prop.HalfBath,
           o.OwnerName, COUNT(s.SaleID) as TotalSales,
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
    results = execute_query(query)
    return QueryResult(query=query, results=results, row_count=len(results))

@app.get("/queries/query4", response_model=QueryResult)
async def query4():
    """Подсчет количества строк по совмещенным данным"""
    query = """
    SELECT p.LandUse,
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
    results = execute_query(query)
    return QueryResult(query=query, results=results, row_count=len(results))

# ============================================================================
# API ENDPOINTS: МАШИННОЕ ОБУЧЕНИЕ
# ============================================================================

@app.get("/ml/data")
async def get_ml_data():
    """Данные для машинного обучения"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Объединение sales и properties
    query = """
    SELECT s.ParcelID, s.SalePrice,
           p.LandValue, p.BuildingValue, p.TotalValue,
           p.YearBuilt, p.Bedrooms, p.FullBath, p.HalfBath
    FROM sales s
    JOIN properties p ON s.ParcelID = p.ParcelID
    WHERE s.SalePrice IS NOT NULL
      AND s.SalePrice > 0
      AND p.LandValue IS NOT NULL
      AND p.TotalValue IS NOT NULL
    ORDER BY RANDOM()
    LIMIT 10000
    """

    cursor.execute(query)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()

    # Конвертация в словари
    results = [dict(zip(columns, row)) for row in rows]

    return {
        "columns": columns,
        "data": results,
        "count": len(results)
    }

@app.get("/ml/stats")
async def get_ml_stats():
    """Статистика датасета для машинного обучения"""
    df = pd.read_sql_query("""
        SELECT s.SalePrice,
               p.LandValue, p.BuildingValue, p.TotalValue,
               p.YearBuilt, p.Bedrooms, p.FullBath, p.HalfBath
        FROM sales s
        JOIN properties p ON s.ParcelID = p.ParcelID
        WHERE s.SalePrice IS NOT NULL
          AND s.SalePrice > 0
    """, get_db_connection())

    # Очистка данных
    df = df.dropna()

    stats = {
        "total_samples": len(df),
        "features": {
            "SalePrice": {
                "min": float(df["SalePrice"].min()),
                "max": float(df["SalePrice"].max()),
                "mean": float(df["SalePrice"].mean()),
                "median": float(df["SalePrice"].median()),
                "std": float(df["SalePrice"].std())
            },
            "TotalValue": {
                "min": float(df["TotalValue"].min()),
                "max": float(df["TotalValue"].max()),
                "mean": float(df["TotalValue"].mean()),
                "median": float(df["TotalValue"].median()),
                "std": float(df["TotalValue"].std())
            },
            "YearBuilt": {
                "min": int(df["YearBuilt"].min()),
                "max": int(df["YearBuilt"].max()),
                "mean": float(df["YearBuilt"].mean()),
                "median": float(df["YearBuilt"].median()),
                "std": float(df["YearBuilt"].std())
            }
        },
        "correlations": df[["SalePrice", "TotalValue", "YearBuilt", "Bedrooms"]].corr().to_dict()
    }

    return stats

# ============================================================================
# API ENDPOINTS: ФАЙЛЫ
# ============================================================================

@app.get("/files/report")
async def get_report():
    """Скачать отчёт"""
    if not os.path.exists(REPORT_PATH):
        raise HTTPException(status_code=404, detail="Файл отчёта не найден")

    return FileResponse(
        REPORT_PATH,
        media_type="text/markdown",
        filename="report.md"
    )

@app.get("/files/database")
async def get_database():
    """Скачать базу данных"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="База данных не найдена")

    return FileResponse(
        DB_PATH,
        media_type="application/x-sqlite3",
        filename="nashville_relational.db"
    )

# ============================================================================
# ЗАПУСК СЕРВЕРА
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Nashville Housing API - FastAPI Server")
    print("=" * 60)
    print(f"\nDatabase: {DB_PATH}")
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"ReDoc Documentation: http://localhost:8000/redoc")
    print("\nStarting server...")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
