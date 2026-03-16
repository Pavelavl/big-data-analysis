#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Практическая работа 2: Веб-проект для анализа данных
Библиотека Streamlit

Приложение для визуализации результатов Практической работы 1:
- Создание реляционной базы данных
- EDA и SQL-запросы
- Обучение простой ML-модели
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

st.set_page_config(
    page_title="Nashville Housing Analysis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Пути к файлам
PRACTICE1_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "practice1")
DB_PATH = os.path.join(PRACTICE1_DIR, "nashville_relational.db")
REPORT_PATH = os.path.join(PRACTICE1_DIR, "report.md")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# ============================================================================
# Вспомогательные функции
# ============================================================================

@st.cache_resource
def load_database():
    """Загрузка базы данных SQLite"""
    conn = sqlite3.connect(DB_PATH)
    return conn

@st.cache_data
def load_table(conn, table_name):
    """Загрузка таблицы из базы данных"""
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    return df

def get_statistics(df, numeric_columns):
    """Получить статистику по числовым столбцам"""
    stats = df[numeric_columns].agg([
        ('count', 'count'),
        ('mean', 'mean'),
        ('median', 'median'),
        ('min', 'min'),
        ('max', 'max'),
        ('std', 'std')
    ]).transpose()
    stats.columns = ['Количество', 'Среднее', 'Медиана', 'Мин', 'Макс', 'Стд. откл.']
    return stats.round(2)

# ============================================================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================================================

st.sidebar.title("🏠 Nashville Housing")
st.sidebar.markdown("---")

# Навигация
page = st.sidebar.radio(
    "Выберите раздел:",
    ["📋 Описание проекта", "📊 EDA Результаты", "🤖️ Обучение модели", "📈 SQL Запросы"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Информация")
st.sidebar.info("""
**База данных:** Nashville Housing

**Количество записей:** 56,477

**Количество таблиц:** 5

**Период данных:** 2013-2016
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### Таблицы БД")
conn = load_database()
tables_info = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name",
    conn
)
for table in tables_info['name']:
    if st.sidebar.button(f"📊 {table}", key=f"table_{table}"):
        st.session_state['selected_table'] = table

# ============================================================================
# СТРАНИЦА 1: ОПИСАНИЕ ПРОЕКТА
# ============================================================================

if page == "📋 Описание проекта":
    st.header("📋 Описание проекта")
    st.markdown("---")

    # Карточки с информацией
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Всего записей",
            "56,477",
            help="Количество записей в базе данных"
        )

    with col2:
        st.metric(
            "Количество таблиц",
            "5",
            help="Реляционная структура с 5 таблицами"
        )

    with col3:
        st.metric(
            "Период данных",
            "2013-2016",
            help="Период сбора данных"
        )

    st.markdown("---")

    # Описание проекта
    st.markdown("""
    ### 📌 О проекте

    Данный веб-сервис предоставляет интерфейс для просмотра результатов исследования данных недвижимости в Нэшвилле, штат Теннесси.

    **Цель исследования:**
    - Создать реляционную базу данных из CSV-файла
    - Провести исследовательский анализ данных (EDA)
    - Выполнить сложные SQL-запросы с JOIN операциями
    - Обучить модель машинного обучения для прогнозирования цен

    **Используемые технологии:**
    - `Python` - Язык программирования
    - `SQLite3` - Реляционная база данных
    - `Pandas` - Обработка данных
    - `Streamlit` - Веб-фреймворк
    - `Scikit-learn` - Машинное обучение
    """)

    # Структура базы данных
    st.markdown("---")
    st.markdown("### 🗄️ Структура базы данных")

    st.markdown("""
    База данных состоит из 5 связанных таблиц:

    | Таблица | Описание | Записей |
    |----------|----------|----------|
    | `parcels` | Участки земли | 48,559 |
    | `addresses` | Адреса | 50,638 |
    | `properties` | Характеристики недвижимости | 22,432 |
    | `owners` | Владельцы | 19,713 |
    | `sales` | Информация о продажах | 56,477 |

    **Связи:**
    - `parcels` (1) ── (1) `properties`
    - `parcels` (1) ── (N) `addresses`
    - `parcels` (1) ── (N) `sales` ── (N) `owners`
    """)

    # Файлы проекта
    st.markdown("---")
    st.markdown("### 📁 Файлы проекта")

    files_info = [
        ("nashville_relational.db", "Реляционная база данных SQLite", "13 МБ"),
        ("nashville_relational_dump.sql", "Дамп базы данных", "19 МБ"),
        ("task1_sqlite.py", "Скрипт создания БД и SQL-запросы", "20 КБ"),
        ("task2_pandas.py", "Анализ через pandas", "12 КБ"),
        ("report.md", "Отчёт с результатами запросов", "17 КБ"),
    ]

    for filename, description, size in files_info:
        st.markdown(f"- **{filename}** - {description} ({size})")

# ============================================================================
# СТРАНИЦА 2: EDA РЕЗУЛЬТАТЫ
# ============================================================================

elif page == "📊 EDA Результаты":
    st.header("📊 EDA Результаты")
    st.markdown("---")

    # Выбор таблицы для анализа
    if 'selected_table' not in st.session_state:
        st.session_state['selected_table'] = 'sales'

    selected_table = st.selectbox(
        "Выберите таблицу для анализа:",
        ['sales', 'parcels', 'properties', 'addresses', 'owners'],
        index=['sales', 'parcels', 'properties', 'addresses', 'owners'].index(st.session_state['selected_table'])
    )
    st.session_state['selected_table'] = selected_table

    # Загрузка данных
    df = load_table(conn, selected_table)

    # Основная информация
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📊 Таблица: {selected_table}")
        st.write(f"Записей: {len(df):,}")

    with col2:
        st.subheader("Столбцы")
        st.write(", ".join(df.columns))

    st.markdown("---")

    # Таблица данных
    st.subheader("Данные")
    display_rows = st.slider("Количество отображаемых строк:", 10, 100, 20)
    st.dataframe(df.head(display_rows), use_container_width=True)

    # Статистика
    st.markdown("---")
    st.subheader("Статистика")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        stats = get_statistics(df, numeric_cols)
        st.dataframe(stats, use_container_width=True)

    # Категориальные переменные
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    if categorical_cols:
        st.markdown("---")
        st.subheader("Категориальные переменные")

        for col in categorical_cols[:4]:  # Показываем первые 4
            st.markdown(f"**{col}**")
            value_counts = df[col].value_counts().head(10)
            st.bar_chart(value_counts)

# ============================================================================
# СТРАНИЦА 3: ОБУЧЕНИЕ МОДЕЛИ
# ============================================================================

elif page == "🤖️ Обучение модели":
    st.header("🤖️ Обучение модели машинного обучения")
    st.markdown("---")

    st.markdown("""
    ### 📌 Описание

    В этом разделе мы обучаем модель машинного обучения для прогнозирования цен продажи недвижимости.

    **Целевая переменная:** `SalePrice` - цена продажи недвижимости
    **Признаки:** Характеристики недвижимости (LandValue, BuildingValue, TotalValue, YearBuilt, Bedrooms, Bathrooms)
    """)

    # Загрузка данных для обучения
    sales_df = load_table(conn, "sales")
    properties_df = load_table(conn, "properties")

    # Объединение данных
    df = sales_df.merge(properties_df, on='ParcelID', how='inner')

    # Очистка данных
    df = df.dropna(subset=['SalePrice', 'LandValue', 'BuildingValue', 'TotalValue'])
    df = df[df['SalePrice'] > 0]

    st.info(f"После очистки: {len(df):,} записей")

    # Выбор признаков
    feature_cols = st.multiselect(
        "Выберите признаки для обучения:",
        ['LandValue', 'BuildingValue', 'TotalValue', 'YearBuilt', 'Bedrooms', 'FullBath', 'HalfBath'],
        default=['LandValue', 'BuildingValue', 'TotalValue', 'YearBuilt', 'Bedrooms', 'FullBath']
    )

    if not feature_cols:
        st.warning("Выберите хотя бы один признак для обучения")
        st.stop()

    X = df[feature_cols]
    y = df['SalePrice']

    # Разделение на train/test
    test_size = st.slider("Размер тестовой выборки:", 10, 40, 20) / 100
    random_state = st.number_input("Random State:", value=42)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    col1, col2 = st.columns(2)
    col1.metric("Обучающая выборка", f"{len(X_train):,}")
    col2.metric("Тестовая выборка", f"{len(X_test):,}")

    # Обучение модели
    st.markdown("---")

    if st.button("🔧 Обучить модель", type="primary"):
        with st.spinner("Обучение модели..."):
            model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            model.fit(X_train, y_train)

            # Сохранение модели
            joblib.dump(model, MODEL_PATH)

            st.success("✅ Модель обучена и сохранена!")

            # Предсказания
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            # Метрики
            train_mse = mean_squared_error(y_train, y_train_pred)
            test_mse = mean_squared_error(y_test, y_test_pred)
            train_mae = mean_absolute_error(y_train, y_train_pred)
            test_mae = mean_absolute_error(y_test, y_test_pred)
            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)

            # Отображение метрик
            st.markdown("---")
            st.subheader("📊 Метрики качества модели")

            metrics_df = pd.DataFrame({
                'Метрика': ['MSE', 'MAE', 'R²'],
                'Обучающая выборка': [train_mse, train_mae, train_r2],
                'Тестовая выборка': [test_mse, test_mae, test_r2]
            })

            st.dataframe(metrics_df, use_container_width=True)

            # График предсказаний
            st.markdown("---")
            st.subheader("📈 Предсказания vs Фактические значения")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=y_test, y=y_test_pred,
                mode='markers',
                name='Предсказания',
                marker=dict(color='blue', size=5)
            ))
            fig.add_trace(go.Scatter(
                x=[y_test.min(), y_test.max()],
                y=[y_test.min(), y_test.max()],
                mode='lines',
                name='Идеальная линия',
                line=dict(color='red', dash='dash')
            ))

            fig.update_layout(
                xaxis_title='Фактические значения',
                yaxis_title='Предсказанные значения',
                title='Предсказания vs Фактические значения',
                width=800,
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)

            # График важности признаков
            st.markdown("---")
            st.subheader("🎯 Важность признаков")

            feature_importance = pd.DataFrame({
                'Признак': feature_cols,
                'Важность': model.feature_importances_
            }).sort_values('Важность', ascending=True)

            fig_importance = px.bar(
                feature_importance,
                x='Важность',
                y='Признак',
                orientation='h',
                title='Важность признаков'
            )
            st.plotly_chart(fig_importance, use_container_width=True)

# ============================================================================
# СТРАНИЦА 4: SQL ЗАПРОСЫ
# ============================================================================

elif page == "📈 SQL Запросы":
    st.header("📈 SQL Запросы")
    st.markdown("---")

    st.markdown("""
    ### 📌 SQL-запросы к базе данных

    Ниже представлены результаты сложных SQL-запросов к реляционной базе данных Nashville Housing.
    """)

    # Определение запросов
    queries = [
        {
            "name": "Запрос 1: JOIN по двум таблицам",
            "description": "Агрегация по parcel_id с сортировкой по общей сумме продаж",
            "sql": """
            SELECT p.ParcelID, p.LandUse, p.TaxDistrict,
                   COUNT(s.SaleID) as TotalSales,
                   ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
                   ROUND(SUM(s.SalePrice), 2) as TotalSalesValue
            FROM parcels p
            LEFT JOIN sales s ON p.ParcelID = s.ParcelID
            WHERE s.SalePrice IS NOT NULL
            GROUP BY p.ParcelID, p.LandUse, p.TaxDistrict
            ORDER BY TotalSalesValue DESC
            LIMIT 20;
            """
        },
        {
            "name": "Запрос 2: JOIN по трем таблицам",
            "description": "Анализ цены по сравнению с оценочной стоимостью",
            "sql": """
            SELECT p.ParcelID, prop.YearBuilt, p.LandUse,
                   COUNT(s.SaleID) as SalesCount,
                   ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
                   ROUND(AVG(prop.TotalValue), 2) as AvgTotalValue
            FROM parcels p
            JOIN properties prop ON p.ParcelID = prop.ParcelID
            JOIN sales s ON p.ParcelID = s.ParcelID
            WHERE s.SalePrice > 0 AND prop.TotalValue > 0
            GROUP BY p.ParcelID, prop.YearBuilt, p.LandUse
            ORDER BY AvgSalePrice DESC
            LIMIT 15;
            """
        },
        {
            "name": "Запрос 3: Детали по объекту",
            "description": "Полная информация по конкретному участку (119 05 0 186.00)",
            "sql": """
            SELECT p.ParcelID, p.LandUse, p.Acreage, p.TaxDistrict,
                   a.PropertyAddress, a.OwnerAddress,
                   prop.LandValue, prop.BuildingValue, prop.TotalValue,
                   prop.YearBuilt, prop.Bedrooms, prop.FullBath, prop.HalfBath,
                   o.OwnerName, COUNT(s.SaleID) as TotalSales,
                   ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
                   ROUND(SUM(s.SalePrice), 2) as TotalSalesAmount
            FROM parcels p
            LEFT JOIN addresses a ON p.ParcelID = a.ParcelID
            LEFT JOIN properties prop ON p.ParcelID = prop.ParcelID
            LEFT JOIN sales s ON p.ParcelID = s.ParcelID
            LEFT JOIN owners o ON s.OwnerID = o.OwnerID
            WHERE p.ParcelID = '119 05 0 186.00'
            GROUP BY p.ParcelID, p.LandUse, p.Acreage, p.TaxDistrict,
                     a.PropertyAddress, a.OwnerAddress, prop.LandValue,
                     prop.BuildingValue, prop.TotalValue, prop.YearBuilt,
                     prop.Bedrooms, prop.FullBath, prop.HalfBath, o.OwnerName;
            """
        },
        {
            "name": "Запрос 4: Группировка по типу использования",
            "description": "Статистика по типам недвижимости",
            "sql": """
            SELECT p.LandUse,
                   COUNT(DISTINCT p.ParcelID) as UniqueParcels,
                   COUNT(s.SaleID) as TotalSales,
                   ROUND(AVG(s.SalePrice), 2) as AvgSalePrice
            FROM parcels p
            LEFT JOIN addresses a ON p.ParcelID = a.ParcelID
            LEFT JOIN sales s ON p.ParcelID = s.ParcelID
            GROUP BY p.LandUse
            ORDER BY UniqueParcels DESC;
            """
        }
    ]

    # Выбор запроса
    query_idx = st.selectbox(
        "Выберите запрос для выполнения:",
        range(len(queries)),
        format_func=lambda x: queries[x]["name"]
    )

    selected_query = queries[query_idx]

    # Отображение описания и SQL
    st.markdown(f"### 📋 {selected_query['name']}")
    st.markdown(f"**Описание:** {selected_query['description']}")
    st.markdown("---")
    st.markdown("**SQL запрос:**")
    st.code(selected_query['sql'], language='sql')

    # Выполнение запроса
    st.markdown("---")
    if st.button("🔍 Выполнить запрос", key=f"execute_{query_idx}"):
        try:
            result_df = pd.read_sql_query(selected_query['sql'], conn)
            st.success(f"✅ Запрос выполнен! Найдено {len(result_df)} записей.")
            st.dataframe(result_df, use_container_width=True)

            # График, если есть числовые данные
            numeric_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                fig = px.scatter(
                    result_df,
                    x=numeric_cols[0],
                    y=numeric_cols[1],
                    title=f"{numeric_cols[1]} vs {numeric_cols[0]}",
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Ошибка выполнения запроса: {str(e)}")

# Закрытие соединения с БД
conn.close()
