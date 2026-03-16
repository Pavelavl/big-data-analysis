#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Практическая работа 4: Работа с библиотеками AutoML
Клиентская часть с визуализацией и сравнением

Цель: изучить фреймворк AutoML и сравнить с настройкой вручную.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import numpy as np
from typing import Dict, List
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

st.set_page_config(
    page_title="Nashville Housing AutoML",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def get_data():
    """Получение данных для ML из API"""
    try:
        response = requests.get(f"{API_URL}/ml/data", timeout=30)
        if response.status_code == 200:
            return pd.DataFrame(response.json()['data'])
        return None
    except Exception as e:
        st.error(f"Ошибка получения данных: {str(e)}")
        return None

def get_stats():
    """Получение статистики датасета из API"""
    try:
        response = requests.get(f"{API_URL}/ml/stats", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Ошибка получения статистики: {str(e)}")
        return None

def train_manual_model(features: list, target: str, test_size: float, n_estimators: int):
    """Обучение модели вручную через API"""
    payload = {
        "target": target,
        "features": features,
        "test_size": test_size,
        "n_estimators": n_estimators,
        "random_state": 42
    }

    try:
        with st.spinner("Обучение модели вручную..."):
            response = requests.post(f"{API_URL}/ml/train/manual", json=payload, timeout=300)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
                return None
    except Exception as e:
        st.error(f"Ошибка обучения: {str(e)}")
        return None

def train_automl_model(features: list, target: str, test_size: float, metric: str, time_limit: int):
    """Обучение модели с AutoML (PyCaret) через API"""
    payload = {
        "target": target,
        "features": features,
        "test_size": test_size,
        "metric": metric,
        "time_limit": time_limit,
        "n_folds": 5
    }

    try:
        with st.spinner("Обучение AutoML модели..."):
            response = requests.post(f"{API_URL}/ml/train/automl", json=payload, timeout=600)
            if response.status_code == 200:
                result = response.json()
                if 'error' in result:
                    st.error(f"Ошибка AutoML: {result.get('message', result.get('error'))}")
                    return None
                return result
            else:
                st.error(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
                return None
    except requests.Timeout:
        st.warning("Обучение AutoML заняло больше времени. Попробуйте увеличить time_limit.")
        return None
    except Exception as e:
        st.error(f"Ошибка AutoML: {str(e)}")
        return None

def get_comparison():
    """Получение сравнения моделей из API"""
    try:
        response = requests.get(f"{API_URL}/ml/compare", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Ошибка получения сравнения: {str(e)}")
        return None

def get_visualizations():
    """Получение данных для визуализации из API"""
    try:
        response = requests.get(f"{API_URL}/ml/visualizations", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Ошибка получения визуализаций: {str(e)}")
        return None

# ============================================================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================================================

st.sidebar.title("🤖️ AutoML Dashboard")
st.sidebar.markdown("---")

# Навигация
page = st.sidebar.radio(
    "Выберите раздел:",
    ["📊 Данные и статистика", "⚙️ Настройка обучения", "🔬 Обучение моделей", "📈 Результаты", "📋 Сравнение"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Информация")

# Отображение статуса сервера
try:
    response = requests.get(f"{API_URL}/stats", timeout=10)
    if response.status_code == 200:
        stats = response.json()
        st.sidebar.metric("Записей в БД", f"{stats['total_records']:,}")
        st.sidebar.info(f"""
**Структура БД:**
- parcels: {stats['parcels']:,}
- addresses: {stats['addresses']:,}
- properties: {stats['properties']:,}
- owners: {stats['owners']:,}
- sales: {stats['sales']:,}
        """)
except:
    st.sidebar.error("❌ Сервер не доступен")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 API Links")
st.sidebar.markdown("""
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
""")

# ============================================================================
# СТРАНИЦА 1: ДАННЫЕ И СТАТИСТИКА
# ============================================================================

if page == "📊 Данные и статистика":
    st.header("📊 Данные и статистика")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Данные для обучения")

        if st.button("🔄 Обновить данные", use_container_width=True):
            st.rerun()

        df = get_data()

        if df is not None:
            st.success(f"✅ Загружено {len(df):,} записей")
            st.dataframe(df.head(20), use_container_width=True)

    with col2:
        st.subheader("Статистика датасета")

        stats = get_stats()

        if stats:
            st.metric("Всего образцов", stats['total_samples'])
            st.metric("Признаков", len(stats['columns']))
            st.metric("Целевая переменная", stats['target'])

            st.markdown("---")
            st.subheader("Статистика по признакам")

            for col_name, col_stats in stats.get('descriptive_stats', {}).items():
                with st.expander(f"📈 {col_name}"):
                    st.json(col_stats)

            if 'correlations' in stats:
                st.markdown("---")
                st.subheader("Корреляционная матрица")

                corr_df = pd.DataFrame(stats['correlations'])
                fig = px.imshow(
                    corr_df,
                    text_auto=True,
                    color_continuous_scale='RdBu',
                    title='Корреляции'
                )
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# СТРАНИЦА 2: НАСТРОЙКА ОБУЧЕНИЯ
# ============================================================================

elif page == "⚙️ Настройка обучения":
    st.header("⚙️ Настройка обучения")
    st.markdown("---")

    # Получение доступных признаков
    data = get_data()
    if data is not None:
        available_features = [col for col in data.columns if col != 'target']
    else:
        available_features = []

    st.subheader("Выбор признаков")
    st.write("Выберите признаки для обучения моделей:")

    # Выбор целевой переменной
    if 'target' in data.columns if data is not None else False:
        target = st.selectbox(
            "Целевая переменная:",
            ['target'],
            index=0
        )
    else:
        st.error("❌ Сначала загрузите данные")
        target = 'target'

    # Выбор признаков
    selected_features = st.multiselect(
        "Признаки:",
        available_features,
        default=['LandValue', 'BuildingValue', 'TotalValue', 'YearBuilt', 'Bedrooms', 'FullBath']
    )

    if not selected_features:
        st.warning("⚠️ Выберите хотя бы один признак")

    st.markdown("---")
    st.subheader("Параметры обучения")

    col1, col2 = st.columns(2)

    with col1:
        test_size = st.slider("Размер тестовой выборки (%):", 10, 40, 20) / 100
        random_state = st.number_input("Random State:", value=42, min_value=1, max_value=1000)

    with col2:
        n_estimators = st.number_input("N Estimators (Manual ML):", value=100, min_value=10, max_value=1000, step=10)

    st.markdown("---")
    st.subheader("Параметры AutoML (PyCaret)")

    col1, col2 = st.columns(2)

    with col1:
        metric = st.selectbox(
            "Метрика качества:",
            ['r2', 'mae', 'mse', 'rmse'],
            index=0
        )
        time_limit = st.slider("Время обучения (секунды):", 60, 600, 300)

    with col2:
        n_folds = st.slider("Количество фолдов (CV):", 3, 10, 5)

    # Сохранение настроек в session state
    st.session_state.update({
        'target': target,
        'features': selected_features,
        'test_size': test_size,
        'random_state': random_state,
        'n_estimators': n_estimators,
        'metric': metric,
        'time_limit': time_limit,
        'n_folds': n_folds
    })

    st.info("""
💡 **Подсказки:**
- **R² (R-squared)** - чем ближе к 1, тем лучше модель
- **MAE (Mean Absolute Error)** - средняя абсолютная ошибка
- **MSE (Mean Squared Error)** - среднеквадратичная ошибка
- **RMSE** - корень из MSE, в тех же единицах что и целевая переменная
    """)

# ============================================================================
# СТРАНИЦА 3: ОБУЧЕНИЕ МОДЕЛЕЙ
# ============================================================================

elif page == "🔬 Обучение моделей":
    st.header("🔬 Обучение моделей")
    st.markdown("---")

    # Проверка настроек
    if 'features' not in st.session_state or not st.session_state['features']:
        st.warning("⚠️ Сначала настройте параметры обучения")
        st.stop()

    # Отображение настроек
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Настройки")
        st.json({
            "Целевая переменная": st.session_state.get('target'),
            "Признаки": st.session_state.get('features'),
            "Размер тестовой выборки": f"{st.session_state.get('test_size') * 100:.0f}%",
            "N Estimators": st.session_state.get('n_estimators'),
            "Метрика": st.session_state.get('metric'),
            "Время обучения": f"{st.session_state.get('time_limit')} сек",
            "Фолды CV": st.session_state.get('n_folds')
        })

    with col2:
        st.subheader("Выбор метода обучения")
        method = st.radio(
            "Метод обучения:",
            ["Manual ML (RandomForest)", "AutoML (PyCaret)"],
            label_visibility="collapsed"
        )

    st.markdown("---")

    if method == "Manual ML (RandomForest)":
        st.subheader("⚙️ Manual ML - RandomForestRegressor")

        st.info("""
        **О методе:**
        - Random Forest - ансамбль решающих деревьев
        - 100 деревьев по умолчанию
        - Обучается на всей обучающей выборке
        - Устойчив к переобучению
        """)

        if st.button("🔧 Обучить Manual модель", type="primary", use_container_width=True):
            result = train_manual_model(
                features=st.session_state['features'],
                target=st.session_state['target'],
                test_size=st.session_state['test_size'],
                n_estimators=st.session_state['n_estimators']
            )

            if result:
                st.session_state['manual_result'] = result
                st.success(f"✅ Модель обучена за {result['training_time']:.2f} сек")
                st.info(f"R² Score: {result['score']:.4f}")

    else:
        st.subheader("🤖️ AutoML - PyCaret")

        st.info("""
        **О PyCaret:**
        - Автоматический выбор лучшей моделей
        - Сравнение нескольких алгоритмов
        - Автоматическая настройка гиперпараметров
        - Поддерживает: Linear Regression, Ridge, Lasso, ElasticNet, KNN, Decision Tree, Random Forest, XGBoost, LightGBM и др.
        """)

        st.warning("⚠️ AutoML требует больше времени для обучения")

        if st.button("🚀 Запустить AutoML", type="primary", use_container_width=True):
            result = train_automl_model(
                features=st.session_state['features'],
                target=st.session_state['target'],
                test_size=st.session_state['test_size'],
                metric=st.session_state['metric'],
                time_limit=st.session_state['time_limit']
            )

            if result:
                st.session_state['automl_result'] = result
                st.success(f"✅ AutoML завершен за {result['training_time']:.2f} сек")
                st.info(f"Лучшая модель: {result['algorithm']} с R² = {result['score']:.4f}")

# ============================================================================
# СТРАНИЦА 4: РЕЗУЛЬТАТЫ
# ============================================================================

elif page == "📈 Результаты":
    st.header("📈 Результаты обучения")
    st.markdown("---")

    if 'manual_result' in st.session_state:
        st.subheader("⚙️ Manual ML Результаты")

        result = st.session_state['manual_result']

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Алгоритм", result['algorithm'])
            st.metric("R² Score", f"{result['score']:.4f}")

        with col2:
            st.metric("Время обучения", f"{result['training_time']:.2f} сек")
            st.metric("Train Size", f"{result['train_size']:,}")

        st.markdown("---")
        st.subheader("Метрики качества")

        metrics = result['metrics']
        metrics_df = pd.DataFrame({
            'Метрика': ['Train MSE', 'Test MSE', 'Train MAE', 'Test MAE', 'Train R²', 'Test R²'],
            'Значение': [
                f"{metrics['train_mse']:,.2f}",
                f"{metrics['test_mse']:,.2f}",
                f"{metrics['train_mae']:,.2f}",
                f"{metrics['test_mae']:,.2f}",
                f"{metrics['train_r2']:.4f}",
                f"{metrics['test_r2']:.4f}"
            ]
        })
        st.dataframe(metrics_df, use_container_width=True)

        # Важность признаков
        if 'feature_importance' in result:
            st.markdown("---")
            st.subheader("Важность признаков")

            feature_imp = pd.DataFrame([
                {'Признак': k, 'Важность': v}
                for k, v in result['feature_importance'].items()
            ]).sort_values('Важность', ascending=True)

            fig = px.bar(
                feature_imp,
                x='Важность',
                y='Признак',
                orientation='h',
                title='Важность признаков (Manual ML)'
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.success(f"✅ Модель сохранена: {result['model_path']}")

    else:
        st.warning("⚠️ Сначала обучите Manual модель")

    st.markdown("---")

    if 'automl_result' in st.session_state:
        st.subheader("🤖️ AutoML Результаты")

        result = st.session_state['automl_result']

        if 'all_models' in result:
            models_df = pd.DataFrame(result['all_models'])

            # Фильтрация лучших моделей по R²
            models_df = models_df.sort_values('R²', ascending=False)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Лучший алгоритм", result['algorithm'])
                st.metric("R² Score", f"{result['score']:.4f}")

            with col2:
                st.metric("Время обучения", f"{result['training_time']:.2f} сек")
                st.metric("Train Size", f"{result['train_size']:,}")

            with col3:
                st.metric("Test Size", f"{result['test_size']:,}")
                st.write()  # spacer

            st.markdown("---")
            st.subheader("Сравнение моделей AutoML")

            # Отображение таблицы моделей
            display_cols = ['Name', 'MAE', 'MSE', 'RMSE', 'R²', 'RMSLE']
            display_cols = [col for col in display_cols if col in models_df.columns]

            st.dataframe(
                models_df[display_cols].head(15),
                use_container_width=True
            )

            # График сравнения R²
            if 'R²' in models_df.columns:
                fig = px.bar(
                    models_df.head(10),
                    x='Name',
                    y='R²',
                    title='R² Score моделей AutoML',
                    color='R²',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Важность признаков
            if 'feature_importance' in result:
                st.markdown("---")
                st.subheader("Важность признаков (AutoML)")

                feature_imp = pd.DataFrame([
                    {'Признак': k, 'Важность': v}
                    for k, v in result['feature_importance'].items()
                ]).sort_values('Важность', ascending=True)

                fig = px.bar(
                    feature_imp,
                    x='Важность',
                    y='Признак',
                    orientation='h',
                    title='Важность признаков (AutoML)'
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.success(f"✅ Модель сохранена: {result['model_path']}")
    else:
        st.warning("⚠️ Сначала запустите AutoML обучение")

# ============================================================================
# СТРАНИЦА 5: СРАВНЕНИЕ
# ============================================================================

elif page == "📋 Сравнение":
    st.header("📋 Сравнение Manual ML и AutoML")
    st.markdown("---")

    comparison = get_comparison()

    if comparison:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚙️ Manual ML")
            st.metric("Алгоритм", comparison['manual_model']['algorithm'])
            st.metric("R² Score", f"{comparison['manual_model']['score']:.4f}")
            st.metric("Время (сек)", f"{comparison['manual_model']['training_time']:.2f}")

        with col2:
            st.subheader("🤖️ AutoML")
            st.metric("Алгоритм", comparison['automl_model']['algorithm'])
            st.metric("R² Score", f"{comparison['automl_model']['score']:.4f}")
            st.metric("Время (сек)", f"{comparison['automl_model']['training_time']:.2f}")

        st.markdown("---")
        st.subheader("📊 Сравнительная таблица")

        comparison_df = pd.DataFrame({
            'Метрика': ['R²', 'Время обучения (сек)'],
            'Manual ML': [
                comparison['manual_model']['score'],
                comparison['manual_model']['training_time']
            ],
            'AutoML': [
                comparison['automl_model']['score'],
                comparison['automl_model']['training_time']
            ]
        })

        st.dataframe(comparison_df, use_container_width=True)

        # График сравнения R²
        st.markdown("---")
        st.subheader("📈 Визуализация сравнения")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Manual ML',
            x=['R²', 'Время (сек)'],
            y=[comparison['manual_model']['score'], comparison['manual_model']['training_time']],
            marker_color='#17a2b8'
        ))
        fig.add_trace(go.Bar(
            name='AutoML',
            x=['R²', 'Время (сек)'],
            y=[comparison['automl_model']['score'], comparison['automl_model']['training_time']],
            marker_color='#ffc107'
        ))

        fig.update_layout(
            title='Сравнение Manual ML vs AutoML',
            barmode='group',
            yaxis_title='Значение',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Важность признаков (сравнение)
        if comparison['manual_model']['feature_importance'] and comparison['automl_model']['feature_importance']:
            st.markdown("---")
            st.subheader("🎯 Сравнение важности признаков")

            manual_features = list(comparison['manual_model']['feature_importance'].keys())
            automl_features = list(comparison['automl_model']['feature_importance'].keys())
            all_features = sorted(set(manual_features + automl_features))

            comparison_data = []
            for feature in all_features:
                manual_imp = comparison['manual_model']['feature_importance'].get(feature, 0)
                automl_imp = comparison['automl_model']['feature_importance'].get(feature, 0)
                comparison_data.append({
                    'Признак': feature,
                    'Manual ML': manual_imp,
                    'AutoML': automl_imp
                })

            comparison_df = pd.DataFrame(comparison_data)
            comparison_df['Разница'] = comparison_df['AutoML'] - comparison_df['Manual ML']

            st.dataframe(comparison_df, use_container_width=True)

        st.markdown("---")

        winner = comparison['winner']
        if winner == "automl":
            st.success(f"🏆 Побеждает **AutoML** (PyCaret) с улучшением на {comparison['improvement']:.2f}%")
        elif winner == "manual":
            st.success(f"🏆 Побеждает **Manual ML** с результатом: {comparison['manual_model']['algorithm']}")
        else:
            st.info("⚖️ Результаты сопоставимы")

        # Рекомендации
        st.markdown("---")
        st.subheader("💡 Рекомендации")

        if winner == "automl":
            st.info("""
            **AutoML показал лучший результат!**
            - Автоматический подбор модели даёт лучшие результаты
            - Рекомендуется использовать AutoML для новых датасетов
            - После анализа можно выбрать лучшие модели для продакшена
            """)
        else:
            st.info("""
            **Manual ML показал схожие результаты!**
            - Для этого датасета RandomForest работает хорошо
            - Для сложных датасетов AutoML может дать лучший результат
            - Рассмотрите другие алгоритмы через AutoML для сравнения
            """)
    else:
        st.warning("⚠️ Обучите оба типа моделей для сравнения")

# ============================================================================
# ФУТЕР
# ============================================================================

st.sidebar.markdown("---")
st.markdown("### 👨‍💻 Автор")
st.markdown("Практическая работа №4 по дисциплине \"Анализ больших данных\"")
