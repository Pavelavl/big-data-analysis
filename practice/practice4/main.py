#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Практическая работа 4: Работа с библиотеками AutoML
Серверная часть с интеграцией PyCaret AutoML

Цель: изучить фреймворк автоматизации машинного обучения и сравнить с настройкой вручную.
"""

import os
import sqlite3
import uvicorn
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from fastapi.middleware.cors import CORSMiddleware
import uuid

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

app = FastAPI(
    title="Nashville Housing AutoML API",
    description="API с AutoML (PyCaret) и сравнением с ручным ML",
    version="2.0.0"
)

# CORS
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
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# ============================================================================
# МОДЕЛИ ДАННЫХ (Pydantic)
# ============================================================================

class AutoMLConfig(BaseModel):
    target: str = "SalePrice"
    features: List[str] = ["LandValue", "BuildingValue", "TotalValue", "YearBuilt", "Bedrooms", "FullBath"]
    test_size: float = 0.2
    random_state: int = 42
    metric: str = "r2"
    time_limit: int = 300
    n_folds: int = 5

class ManualMLConfig(BaseModel):
    target: str = "SalePrice"
    features: List[str] = ["LandValue", "BuildingValue", "TotalValue", "YearBuilt", "Bedrooms", "FullBath"]
    test_size: float = 0.2
    random_state: int = 42
    n_estimators: int = 100

class ModelInfo(BaseModel):
    model_type: str  # "manual" or "automl"
    algorithm: str
    score: float
    metric: str
    training_time: float
    feature_importance: Dict[str, float]

class ComparisonResult(BaseModel):
    manual_model: ModelInfo
    automl_model: ModelInfo
    improvement: float
    winner: str

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def get_db_connection():
    """Создание соединения с базой данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_ml_data():
    """Загрузка и подготовка данных для ML"""
    conn = get_db_connection()

    query = """
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
      AND p.YearBuilt IS NOT NULL
    ORDER BY RANDOM()
    LIMIT 5000
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Очистка данных
    df = df.dropna(subset=['target', 'LandValue', 'TotalValue', 'YearBuilt'])
    df = df.dropna()

    # Удаление ParcelID (не признак)
    df = df.drop(columns=['ParcelID', 'HalfBath'])

    return df

# ============================================================================
# РУЧНОЕ МАШИННОЕ ОБУЧЕНИЕ (Manual ML)
# ============================================================================

def train_manual_model(config: ManualMLConfig, data: pd.DataFrame) -> Dict[str, Any]:
    """Обучение модели RandomForest вручную"""
    import time

    start_time = time.time()

    # Подготовка данных
    X = data[config.features]
    y = data[config.target]

    # Разделение данных
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config.test_size,
        random_state=config.random_state
    )

    # Обучение модели
    model = RandomForestRegressor(
        n_estimators=config.n_estimators,
        random_state=config.random_state,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Предсказания
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    # Метрики
    metrics = {
        'train_mse': mean_squared_error(y_train, y_train_pred),
        'test_mse': mean_squared_error(y_test, y_test_pred),
        'train_mae': mean_absolute_error(y_train, y_train_pred),
        'test_mae': mean_absolute_error(y_test, y_test_pred),
        'train_r2': r2_score(y_train, y_train_pred),
        'test_r2': r2_score(y_test, y_test_pred)
    }

    # Важность признаков
    feature_importance = dict(zip(config.features, model.feature_importances_))
    feature_importance = {k: float(v) for k, v in feature_importance.items()}

    training_time = time.time() - start_time

    # Сохранение модели
    model_path = os.path.join(MODELS_DIR, "manual_rf_model.pkl")
    joblib.dump(model, model_path)

    return {
        'algorithm': 'RandomForestRegressor',
        'score': float(metrics['test_r2']),
        'metric': config.metric,
        'metrics': metrics,
        'training_time': training_time,
        'feature_importance': feature_importance,
        'model_path': model_path,
        'train_size': len(X_train),
        'test_size': len(X_test)
    }

# ============================================================================
# AUTOML С PYCARET
# ============================================================================

def train_automl_model(config: AutoMLConfig, data: pd.DataFrame) -> Dict[str, Any]:
    """Обучение модели с использованием PyCaret AutoML"""
    import time
    try:
        from pycaret.regression import setup, compare_models, pull, create_model, plot_model
        pycaret_available = True
    except ImportError:
        pycaret_available = False
        return {
            'error': 'PyCaret не установлен',
            'message': 'Установите PyCaret: pip install pycaret[full]'
        }

    if not pycaret_available:
        return {'error': 'PyCaret not available'}

    start_time = time.time()

    # Setup данных для PyCaret
    target_col = config.target

    # Настройка эксперимента
    exp = setup(
        data=data,
        target=target_col,
        train_size=1 - config.test_size,
        session_id='nashville_auto_ml',
        verbose=False
    )

    # Сравнение моделей
    best_model = compare_models(
        fold=config.n_folds,
        sort=config.metric,
        n_select=3,
        verbose=False
    )

    if best_model.empty:
        return {
            'error': 'Не удалось обучить модели',
            'message': 'Нет данных после фильтрации'
        }

    # Получение информации о лучшей модели
    best_model_info = best_model.iloc[0]

    # Создание финальной модели
    final_model = create_model(best_model_info['Name'], verbose=False)

    # Метрики
    metrics = {
        'MAE': float(best_model_info['MAE']),
        'MSE': float(best_model_info['MSE']),
        'RMSE': float(best_model_info['RMSE']),
        'R2': float(best_model_info['R2']),
        'RMSLE': float(best_model_info.get('RMSLE', 0))
    }

    # Важность признаков
    try:
        feature_importance = final_model.get_feature_importance()
        feature_importance = dict(zip(feature_importance['Feature'], feature_importance['Value']))
    except:
        feature_importance = {}

    training_time = time.time() - start_time

    # Сохранение модели
    model_name = f"automl_{best_model_info['Name']}_model.pkl"
    model_path = os.path.join(MODELS_DIR, model_name)
    joblib.dump(final_model, model_path)

    return {
        'algorithm': best_model_info['Name'],
        'score': float(best_model_info['R2']),
        'metric': config.metric,
        'metrics': metrics,
        'training_time': training_time,
        'feature_importance': feature_importance,
        'model_path': model_path,
        'all_models': best_model.to_dict('records'),
        'train_size': len(data) - int(len(data) * config.test_size),
        'test_size': int(len(data) * config.test_size)
    }

# ============================================================================
# КОРНЕВАЯ СТРАНИЦА
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Корневая страница с документацией"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nashville Housing AutoML API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            h2 { color: #555; margin-top: 30px; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            .section { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .endpoint { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #28a745; }
            .method { display: inline-block; padding: 3px 10px; margin-right: 10px; border-radius: 4px; font-weight: bold; font-size: 12px; }
            .GET { background: #007bff; color: white; }
            .POST { background: #28a745; color: white; }
            code { background: #e9ecef; padding: 2px 8px; border-radius: 4px; font-family: monospace; font-size: 13px; }
            .automl-badge { background: #ffc107; color: #333; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
            .manual-badge { background: #17a2b8; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖️ Nashville Housing AutoML API</h1>
            <p>REST API с интеграцией PyCaret AutoML и сравнением с ручным ML</p>

            <div class="section">
                <h2>📊 Подготовка данных</h2>
                <p>Загрузка и подготовка данных из базы данных Nashville Housing</p>
                <p><span class="method GET">GET</span> <code>/ml/data</code> - Данные для обучения</p>
                <p><span class="method GET">GET</span> <code>/ml/stats</code> - Статистика датасета</p>
            </div>

            <div class="section">
                <h2>⚙️ Обучение моделей</h2>
                <p>Выбор между ручным ML и AutoML подходом</p>
                <p><span class="method POST">POST</span> <code>/ml/train/manual</code> - Обучение модели вручную <span class="manual-badge">Manual ML</span></p>
                <p><span class="method POST">POST</span> <code>/ml/train/automl</code> - Обучение с PyCaret <span class="automl-badge">AutoML</span></p>
                <p><span class="method GET">GET</span> <code>/ml/compare</code> - Сравнение результатов</p>
            </div>

            <div class="section">
                <h2>📈 Визуализация и результаты</h2>
                <p>Получение результатов обучения и визуализации</p>
                <p><span class="method GET">GET</span> <code>/ml/results/manual</code> - Результаты ручного ML</p>
                <p><span class="method GET">GET</span> <code>/ml/results/automl</code> - Результаты AutoML</p>
                <p><span class="method GET">GET</span> <code>/ml/visualizations</code> - Графики и визуализации</p>
            </div>

            <div class="section">
                <h2>📁 Управление моделями</h2>
                <p>Скачивание и управление обученными моделями</p>
                <p><span class="method GET">GET</span> <code>/models</code> - Список всех моделей</p>
                <p><span class="method GET">GET</span> <code>/models/download/{model_name}</code> - Скачать модель</p>
            </div>

            <h2>📖 Дополнительные ресурсы</h2>
            <ul>
                <li><a href="/docs">Swagger UI (интерактивная документация)</a></li>
                <li><a href="/redoc">ReDoc документация</a></li>
            </ul>

            <div style="margin-top: 30px; padding: 20px; background: #d1ecf1; border-radius: 8px;">
                <h3 style="color: #333; margin-top: 0;">💡 Поддерживаемые AutoML фреймворки</h3>
                <ul style="color: #333; line-height: 1.8;">
                    <li><strong>PyCaret</strong> - Используется в этом проекте</li>
                    <li>H2O AutoML</li>
                    <li>AutoSklearn</li>
                    <li>flaml AutoML</li>
                    <li>LightAutoML</li>
                    <li>FEDOT</li>
                    <li>AutoGluon</li>
                    <li>LAMA</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

# ============================================================================
# API ENDPOINTS: ДАННЫЕ
# ============================================================================

@app.get("/ml/data")
async def get_ml_data():
    """Получение данных для ML"""
    df = load_ml_data()

    # Статистика по столбцам
    stats = {
        "total_samples": len(df),
        "features": list(df.columns),
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "sample": df.head(10).to_dict('records')
    }

    return stats

@app.get("/ml/stats")
async def get_ml_stats():
    """Статистика датасета для ML"""
    df = load_ml_data()

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    stats = {
        "total_samples": len(df),
        "columns": list(df.columns),
        "target": "target",
        "descriptive_stats": {}
    }

    for col in numeric_cols:
        stats["descriptive_stats"][col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": float(df[col].mean()),
            "median": float(df[col].median()),
            "std": float(df[col].std()),
            "q25": float(df[col].quantile(0.25)),
            "q75": float(df[col].quantile(0.75))
        }

    # Корреляции
    if len(numeric_cols) >= 2:
        stats["correlations"] = df[numeric_cols].corr().to_dict()

    return stats

# ============================================================================
# API ENDPOINTS: ОБУЧЕНИЕ
# ============================================================================

@app.post("/ml/train/manual")
async def train_manual(config: ManualMLConfig):
    """Обучение модели вручную"""
    data = load_ml_data()

    # Проверка наличия признаков
    available_features = [f for f in config.features if f in data.columns]
    if not available_features:
        raise HTTPException(status_code=400, detail="Ни один признак не найден в данных")

    config.features = available_features

    result = train_manual_model(config, data)

    # Сохранение результата
    result_id = str(uuid.uuid4())
    result_path = os.path.join(MODELS_DIR, f"manual_result_{result_id}.json")

    with open(result_path, 'w') as f:
        json.dump(result, f)

    return {
        "result_id": result_id,
        "model_type": "manual",
        "status": "completed",
        "model": result
    }

@app.post("/ml/train/automl")
async def train_automl(config: AutoMLConfig):
    """Обучение модели с PyCaret AutoML"""
    data = load_ml_data()

    # Проверка PyCaret
    try:
        import pycaret
    except ImportError:
        raise HTTPException(
            status_code=400,
            detail="PyCaret не установлен. Установите: pip install pycaret[full]"
        )

    # Проверка наличия целевой переменной
    if config.target not in data.columns:
        raise HTTPException(status_code=400, detail=f"Целевая переменная {config.target} не найдена")

    result = train_automl_model(config, data)

    if 'error' in result:
        raise HTTPException(status_code=400, detail=result.get('message', result.get('error')))

    # Сохранение результата
    result_id = str(uuid.uuid4())
    result_path = os.path.join(MODELS_DIR, f"automl_result_{result_id}.json")

    with open(result_path, 'w') as f:
        json.dump(result, f)

    return {
        "result_id": result_id,
        "model_type": "automl",
        "framework": "PyCaret",
        "status": "completed",
        "model": result
    }

@app.get("/ml/compare")
async def compare_models():
    """Сравнение ручного ML и AutoML результатов"""
    # Чтение сохранённых результатов
    results = []

    for filename in os.listdir(MODELS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(MODELS_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    result = json.load(f)
                    result['filename'] = filename
                    results.append(result)
            except:
                pass

    # Поиск результатов обоих типов
    manual_result = next((r for r in results if r.get('model_type') == 'manual'), None)
    automl_result = next((r for r in results if r.get('model_type') == 'automl'), None)

    if not manual_result or not automl_result:
        raise HTTPException(
            status_code=404,
            detail="Не найдены результаты обучения обоих типов. Сначала обучите модели."
        )

    # Сравнение
    manual_score = manual_result['model']['score']
    automl_score = automl_result['model']['score']
    improvement = ((automl_score - manual_score) / manual_score) * 100
    winner = "automl" if automl_score > manual_score else "manual"

    return ComparisonResult(
        manual_model=ModelInfo(
            model_type="manual",
            algorithm=manual_result['model']['algorithm'],
            score=manual_score,
            metric=manual_result['model']['metric'],
            training_time=manual_result['model']['training_time'],
            feature_importance=manual_result['model']['feature_importance']
        ),
        automl_model=ModelInfo(
            model_type="automl",
            algorithm=automl_result['model']['algorithm'],
            score=automl_score,
            metric=automl_result['model']['metric'],
            training_time=automl_result['model']['training_time'],
            feature_importance=automl_result['model']['feature_importance']
        ),
        improvement=round(improvement, 2),
        winner=winner
    )

# ============================================================================
# API ENDPOINTS: РЕЗУЛЬТАТЫ И ВИЗУАЛИЗАЦИИ
# ============================================================================

@app.get("/ml/results/manual")
async def get_manual_results():
    """Результаты ручного ML"""
    # Поиск последнего ручного результата
    results = []
    for filename in sorted(os.listdir(MODELS_DIR), reverse=True):
        if filename.startswith('manual_result') and filename.endswith('.json'):
            with open(os.path.join(MODELS_DIR, filename), 'r') as f:
                result = json.load(f)
                results.append(result)
            break

    if not results:
        raise HTTPException(status_code=404, detail="Результат ручного ML не найден")

    return results[0]['model']

@app.get("/ml/results/automl")
async def get_automl_results():
    """Результаты AutoML"""
    # Поиск последнего AutoML результата
    results = []
    for filename in sorted(os.listdir(MODELS_DIR), reverse=True):
        if filename.startswith('automl_result') and filename.endswith('.json'):
            with open(os.path.join(MODELS_DIR, filename), 'r') as f:
                result = json.load(f)
                results.append(result)
            break

    if not results:
        raise HTTPException(status_code=404, detail="Результат AutoML не найден")

    return results[0]['model']

@app.get("/ml/visualizations")
async def get_visualizations():
    """Получение данных для визуализаций"""
    data = load_ml_data()

    # Подготовка данных для визуализации
    visualizations = {
        "target_distribution": {
            "labels": data['target'].value_counts(bins=10).index.tolist(),
            "values": data['target'].value_counts(bins=10).values.tolist()
        },
        "feature_distributions": {}
    }

    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        visualizations["feature_distributions"][col] = {
            "values": data[col].tolist()
            "stats": {
                "min": float(data[col].min()),
                "max": float(data[col].max()),
                "mean": float(data[col].mean()),
                "median": float(data[col].median())
            }
        }

    return visualizations

# ============================================================================
# API ENDPOINTS: УПРАВЛЕНИЕ МОДЕЛЯМИ
# ============================================================================

@app.get("/models")
async def list_models():
    """Список всех обученных моделей"""
    models = []

    for filename in os.listdir(MODELS_DIR):
        if filename.endswith('.pkl') or filename.endswith('.json'):
            filepath = os.path.join(MODELS_DIR, filename)
            models.append({
                "name": filename,
                "type": "model" if filename.endswith('.pkl') else "result",
                "size": os.path.getsize(filepath),
                "modified": os.path.getmtime(filepath)
            })

    return {"models": sorted(models, key=lambda x: x['modified'], reverse=True)}

@app.get("/models/download/{model_name}")
async def download_model(model_name: str):
    """Скачать модель"""
    model_path = os.path.join(MODELS_DIR, model_name)

    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Модель не найдена")

    return FileResponse(
        model_path,
        filename=model_name
    )

# ============================================================================
# ЗАПУСК СЕРВЕРА
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Nashville Housing AutoML API - FastAPI Server")
    print("=" * 60)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Models directory: {MODELS_DIR}")
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"ReDoc Documentation: http://localhost:8000/redoc")
    print("\nSupported AutoML frameworks:")
    print("  ✅ PyCaret (installed)")
    print("  ⚪ H2O AutoML")
    print("  ⚪ AutoSklearn")
    print("  ⚪ flaml AutoML")
    print("  ⚪ LightAutoML")
    print("  ⚪ FEDOT")
    print("  ⚪ AutoGluon")
    print("  ⚪ LAMA")
    print("\nStarting server...")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
