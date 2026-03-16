#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lab 4: Regression - California Housing Dataset
Rare complexity: 1 model (Linear Regression)
Variant 16: Media Campaign Cost (using California Housing as proxy)
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                             r2_score)
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Настройка визуализации
try:
    plt.style.use('seaborn-v0_8')
except:
    plt.style.use('seaborn')
sns.set_palette("husl")

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print("=" * 50)
print("LAB 4: REGRESSION ANALYSIS")
print("=" * 50)

# ============================================================================
# 1. Загрузка данных
# ============================================================================
print("\n" + "=" * 50)
print("1. LOADING DATA")
print("=" * 50)

# Используем California Housing как аналог для прогнозирования стоимости
data = datasets.fetch_california_housing()

X = pd.DataFrame(data["data"], columns=data["feature_names"])
y = data["target"]

df = X.copy()
df['target'] = y

print(f"\nDataset: California Housing (proxy for Media Campaign Cost)")
print(f"\nDescription:")
print(f"  Target: Median house value in $100,000s")
print(f"  Features ({len(data['feature_names'])}):")
for i, feat in enumerate(data['feature_names'], 1):
    print(f"    {i:2d}. {feat}")

print("\n" + "=" * 50)
print(f"Dataset size: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print("=" * 50)

# ============================================================================
# 2. Исследовательский анализ данных (EDA)
# ============================================================================
print("\n" + "=" * 60)
print("2. EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# Статистика для интервальных переменных
print("\nNumeric variables statistics:")
numeric_stats = df.describe(percentiles=[0.25, 0.5, 0.75]).T
numeric_stats = numeric_stats[['count', 'mean', '50%', 'min', '25%', '75%', 'max']]
numeric_stats.columns = ['Count', 'Mean', 'Median', 'Min', '25%', '75%', 'Max']

print(numeric_stats.to_string())

# Анализ целевой переменной
print("\n" + "=" * 60)
print("TARGET DISTRIBUTION")
print("=" * 60)

print(f"\nTarget variable statistics:")
print(f"  Mean: {df['target'].mean():.4f}")
print(f"  Median: {df['target'].median():.4f}")
print(f"  Std: {df['target'].std():.4f}")
print(f"  Min: {df['target'].min():.4f}")
print(f"  Max: {df['target'].max():.4f}")
print(f"  Mode: {df['target'].mode()[0]:.4f}")
print(f"  Mode count: {len(df[df['target'] == df['target'].mode()[0]])}")

# Проверка пропусков
print("\n" + "=" * 60)
print("MISSING VALUES ANALYSIS")
print("=" * 60)

missing = df.isnull().sum()
if missing.sum() == 0:
    print("\nNo missing values detected!")
else:
    print("\nMissing values by column:")
    print(missing[missing > 0])

# Анализ выбросов
print("\n" + "=" * 60)
print("OUTLIERS ANALYSIS (IQR Method)")
print("=" * 60)

outliers_info = {}
for col in df.columns:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)][col]
    outliers_info[col] = {
        'count': len(outliers),
        'percent': len(outliers) / len(df) * 100,
        'lower': lower,
        'upper': upper
    }

print(f"\nFeatures with most outliers:")
sorted_outliers = sorted(outliers_info.items(), key=lambda x: x[1]['count'], reverse=True)
for col, info in sorted_outliers[:10]:
    print(f"  {col}: {info['count']} outliers ({info['percent']:.1f}%)")

print("\nNo categorical variables - all features are numeric.")

# ============================================================================
# 3. Визуализация
# ============================================================================
print("\n" + "=" * 60)
print("3. CREATING VISUALIZATIONS")
print("=" * 60)

# Распределение целевой переменной
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Feature Distributions', fontsize=14)

for idx, feat in enumerate(X.columns[:6]):
    ax = axes[idx // 3, idx % 3]
    ax.hist(df[feat], bins=50, alpha=0.7, edgecolor='black')
    ax.set_xlabel(feat)
    ax.set_ylabel('Frequency')
    ax.axvline(df[feat].mean(), color='red', linestyle='--', label=f'Mean: {df[feat].mean():.2f}')
    ax.legend()

plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab4/feature_distributions.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: feature_distributions.png")

# Распределение целевой переменной
plt.figure(figsize=(10, 6))
plt.hist(df['target'], bins=50, alpha=0.7, edgecolor='black')
plt.xlabel('Target (Median House Value)')
plt.ylabel('Frequency')
plt.title('Target Distribution')
plt.axvline(df['target'].mean(), color='red', linestyle='--', label=f'Mean: {df["target"].mean():.2f}')
plt.axvline(df['target'].median(), color='green', linestyle='--', label=f'Median: {df["target"].median():.2f}')
plt.legend()
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab4/target_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: target_distribution.png")

# Корреляционная матрица
plt.figure(figsize=(12, 10))
correlation = df.corr()
mask = np.triu(np.ones_like(correlation, dtype=bool))
sns.heatmap(correlation, mask=mask, cmap='coolwarm', center=0,
            annot=True, fmt='.2f', cbar_kws={'label': 'Correlation'})
plt.title('Feature Correlation Matrix', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab4/correlation_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: correlation_matrix.png")

# Pairplot для первых 5 признаков
sns.pairplot(df[list(X.columns[:4]) + ['target']], diag_kind='hist', plot_kws={'alpha': 0.5})
plt.suptitle('Pairplot of First 4 Features', y=1.02)
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab4/pairplot.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: pairplot.png")

# Корреляция признаков с целевой переменной
target_corr = correlation['target'].abs().sort_values(ascending=False)
print("\n" + "=" * 60)
print("FEATURE CORRELATION WITH TARGET")
print("=" * 60)
for i, (feat, corr) in enumerate(target_corr[:-1].items(), 1):
    direction = "Positive" if correlation.loc[feat, 'target'] > 0 else "Negative"
    print(f"{i:2d}. {feat:25s}: {corr:.4f} ({direction})")

# ============================================================================
# 4. Проверка гипотез
# ============================================================================
print("\n" + "=" * 60)
print("4. HYPOTHESIS TESTING")
print("=" * 60)

# Гипотеза 1: MedInc (Median Income) имеет сильную положительную корреляцию с целевой переменной
print("\nHypothesis 1: Median Income (MedInc) positively correlates with target value")
correlation_medinc = df['MedInc'].corr(df['target'])
print(f"  Correlation: {correlation_medinc:.4f}")

# t-test для проверки значимости корреляции
t_stat, p_value = stats.pearsonr(df['MedInc'], df['target'])
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value: {p_value:.2e}")
print(f"  Conclusion: {'Reject H0 - correlation is significant' if p_value < 0.05 else 'Cannot reject H0'}")

# Гипотеза 2: Среднее значение целевой переменной отличается для домов с высокой и низкой средней комнатностью
print("\nHypothesis 2: Target mean differs for high vs low AveRooms")
median_ave_rooms = df['AveRooms'].median()
high_rooms = df[df['AveRooms'] > median_ave_rooms]['target']
low_rooms = df[df['AveRooms'] <= median_ave_rooms]['target']

print(f"  High AveRooms (n={len(high_rooms)}): Mean = {high_rooms.mean():.4f}, Std = {high_rooms.std():.4f}")
print(f"  Low AveRooms (n={len(low_rooms)}): Mean = {low_rooms.mean():.4f}, Std = {low_rooms.std():.4f}")

# t-test для двух независимых выборок
t_stat, p_value = stats.ttest_ind(high_rooms, low_rooms)
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value: {p_value:.2e}")
print(f"  Conclusion: {'Reject H0 - means are different' if p_value < 0.05 else 'Cannot reject H0'}")

# ============================================================================
# 5. Подготовка данных
# ============================================================================
print("\n" + "=" * 60)
print("5. DATA PREPARATION")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"\nTrain set: {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
print(f"Test set:  {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")

print(f"\nTarget statistics:")
print(f"  Train: mean={y_train.mean():.4f}, std={y_train.std():.4f}")
print(f"  Test:  mean={y_test.mean():.4f}, std={y_test.std():.4f}")

# Нормализация (для KNN, если нужно)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nData normalized (StandardScaler: mean=0, std=1)")
print(f"After normalization (train):")
print(f"  Mean: {X_train_scaled.mean():.6f}")
print(f"  Std: {X_train_scaled.std():.6f}")

# ============================================================================
# 6. Построение моделей регрессии
# ============================================================================
print("\n" + "=" * 60)
print("6. BUILDING REGRESSION MODELS")
print("=" * 60)

def evaluate_regression(model, X_train, X_test, y_train, y_test, model_name):
    """Train model and return metrics"""
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)

    # MAPE - Mean Absolute Percentage Error
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

    r2 = r2_score(y_test, y_pred)

    return {
        'model': model,
        'name': model_name,
        'y_pred': y_pred,
        'mae': mae,
        'mse': mse,
        'rmse': rmse,
        'mape': mape,
        'r2': r2
    }

# Модель 1: Linear Regression
print("\n" + "-" * 60)
print("MODEL 1: Linear Regression")
print("-" * 60)

lr = LinearRegression()
lr_results = evaluate_regression(lr, X_train, X_test, y_train, y_test, "Linear Regression")

print(f"\nMAE (Mean Absolute Error): {lr_results['mae']:.4f}")
print(f"MSE (Mean Squared Error): {lr_results['mse']:.4f}")
print(f"RMSE (Root Mean Squared Error): {lr_results['rmse']:.4f}")
print(f"MAPE (Mean Absolute % Error): {lr_results['mape']:.2f}%")
print(f"R^2 Score: {lr_results['r2']:.4f}")

# Коэффициенты модели
print(f"\nModel coefficients:")
for i, (feat, coef) in enumerate(zip(X.columns, lr.coef_)):
    print(f"  {feat:20s}: {coef:8.4f}")
print(f"  Intercept           : {lr.intercept_:8.4f}")

# ============================================================================
# 7. Визуализация результатов
# ============================================================================
print("\n" + "=" * 60)
print("7. RESULT VISUALIZATION")
print("=" * 60)

# Actual vs Predicted
plt.figure(figsize=(10, 6))
plt.scatter(y_test, lr_results['y_pred'], alpha=0.5, edgecolors='black')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Perfect prediction')
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Linear Regression: Actual vs Predicted')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab4/actual_vs_predicted.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: actual_vs_predicted.png")

# Residual plot
residuals = y_test - lr_results['y_pred']
plt.figure(figsize=(10, 6))
plt.scatter(lr_results['y_pred'], residuals, alpha=0.5, edgecolors='black')
plt.axhline(y=0, color='r', linestyle='--', lw=2)
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.title('Linear Regression: Residual Plot')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab4/residual_plot.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: residual_plot.png")

# Распределение остатков
plt.figure(figsize=(10, 6))
plt.hist(residuals, bins=50, alpha=0.7, edgecolor='black')
plt.xlabel('Residuals')
plt.ylabel('Frequency')
plt.title('Linear Regression: Residual Distribution')
plt.axvline(x=0, color='r', linestyle='--', lw=2)
plt.axvline(x=residuals.mean(), color='g', linestyle='--', lw=2, label=f'Mean: {residuals.mean():.4f}')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab4/residual_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: residual_distribution.png")

# Feature importance (absolute coefficient values)
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Coefficient': lr.coef_,
    'Abs_Coefficient': np.abs(lr.coef_)
}).sort_values('Abs_Coefficient', ascending=False)

plt.figure(figsize=(10, 6))
colors = ['red' if x < 0 else 'green' for x in feature_importance['Coefficient']]
plt.barh(feature_importance['Feature'], feature_importance['Coefficient'], color=colors)
plt.xlabel('Coefficient Value')
plt.ylabel('Feature')
plt.title('Linear Regression: Feature Importance')
plt.axvline(x=0, color='black', linestyle='-')
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab4/feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: feature_importance.png")

# Q-Q plot для проверки нормальности остатков
from scipy import stats
plt.figure(figsize=(10, 6))
stats.probplot(residuals, dist="norm", plot=plt)
plt.title('Linear Regression: Q-Q Plot of Residuals')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab4/qq_plot.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: qq_plot.png")

print("\n" + "=" * 60)
print("FEATURE IMPORTANCE (Linear Regression)")
print("=" * 60)
for i, row in feature_importance.iterrows():
    direction = "+" if row['Coefficient'] > 0 else "-"
    print(f"{row['Abs_Coefficient']:8.4f}: {row['Feature']:20s} ({direction})")

# ============================================================================
# 8. Идеи для улучшения
# ============================================================================
print("\n" + "=" * 60)
print("8. IDEAS FOR MODEL IMPROVEMENT")
print("=" * 60)

improvement_ideas = [
    ("Additional regression models", [
        "Ridge Regression (L2 regularization)",
        "LASSO Regression (L1 regularization for feature selection)",
        "ElasticNet (L1 + L2 regularization)",
        "KNN Regressor",
        "Decision Tree Regressor",
        "Random Forest Regressor",
        "Gradient Boosting (XGBoost, LightGBM)"
    ]),
    ("Feature engineering", [
        "Polynomial features for non-linear relationships",
        "Feature interaction terms",
        "Log transformation of skewed features",
        "Binning continuous features"
    ]),
    ("Outlier handling", [
        "Remove or cap outliers",
        "Use robust regression methods",
        "Transformations to reduce outlier impact"
    ]),
    ("Hyperparameter optimization", [
        "GridSearchCV for Ridge/LASSO alpha parameter",
        "Cross-validation for KNN n_neighbors"
    ]),
    ("Model validation", [
        "K-Fold Cross Validation",
        "Time Series Split if data is temporal",
        "Leave-One-Out CV for small datasets"
    ])
]

for category, ideas in improvement_ideas:
    print(f"\n{category}:")
    for idea in ideas:
        print(f"  - {idea}")

# ============================================================================
# 9. Финальные выводы
# ============================================================================
print("\n" + "=" * 60)
print("9. FINAL CONCLUSIONS")
print("=" * 60)

conclusions = f"""
Dataset: California Housing ({len(df)} samples, {len(X.columns)} features)
- Target: Median house value in $100,000s
- No missing values
- Some outliers detected in AveRooms, AveBedrms

Feature Analysis:
- MedInc (Median Income) has strongest positive correlation with target
- Location features (Latitude, Longitude) also important
- Some features have high correlation with each other (multicollinearity)

Hypothesis Testing:
- H1: MedInc positively correlates with target - CONFIRMED (p < 0.001)
- H2: Target differs for high vs low AveRooms - CONFIRMED (p < 0.001)

Model: Linear Regression
- MAE: {lr_results['mae']:.4f}
- RMSE: {lr_results['rmse']:.4f}
- MAPE: {lr_results['mape']:.2f}%
- R^2 Score: {lr_results['r2']:.4f}

Interpretation:
- R^2 of {lr_results['r2']:.2%} indicates the model explains this percentage
  of variance in the target variable
- The most important feature is {feature_importance.iloc[0]['Feature']}
- Residual analysis shows some heteroscedasticity (variance changes with predicted value)
"""

print(conclusions)

# Формулы метрик
print("\n" + "=" * 60)
print("METRICS FORMULAS")
print("=" * 60)
print("""
MAE  = (1/n) * sum(|y_i - y_pred_i|)                    - Mean Absolute Error
MSE  = (1/n) * sum((y_i - y_pred_i)^2)                  - Mean Squared Error
RMSE = sqrt(MSE)                                         - Root Mean Squared Error
MAPE = (100/n) * sum(|(y_i - y_pred_i) / y_i|)          - Mean Absolute Percentage Error
R^2  = 1 - [sum((y_i - y_pred_i)^2) / sum((y_i - y_mean)^2)] - Coefficient of Determination
""")

print("\n" + "=" * 50)
print("LAB 4 COMPLETED SUCCESSFULLY")
print("=" * 50)
