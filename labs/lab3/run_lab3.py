#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lab 3: Binary Classification - Breast Cancer Dataset
Rare complexity: 2 models (KNN + Logistic Regression)
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
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, roc_auc_score, roc_curve)

# Настройка визуализации
try:
    plt.style.use('seaborn-v0_8')
except:
    plt.style.use('seaborn')
sns.set_palette("husl")

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print("=" * 50)
print("LAB 3: BINARY CLASSIFICATION")
print("=" * 50)

# ============================================================================
# 1. Загрузка данных
# ============================================================================
print("\n" + "=" * 50)
print("1. LOADING DATA")
print("=" * 50)

data = datasets.load_breast_cancer()

X = pd.DataFrame(data["data"], columns=data["feature_names"])
y = data["target"]

df = X.copy()
df['target'] = y

print(f"\nDataset: Breast Cancer Wisconsin (Diagnostic)")
print(f"\nTarget variable:")
print(f"  0 - Malignant (cancerous)")
print(f"  1 - Benign (non-cancerous)")
print(f"\nFeatures ({len(data['feature_names'])}): Cell nucleus characteristics")

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
numeric_stats = df.drop(columns='target').describe(percentiles=[0.25, 0.5, 0.75]).T
numeric_stats = numeric_stats[['count', 'mean', '50%', 'min', '25%', '75%', 'max']]
numeric_stats.columns = ['Count', 'Mean', 'Median', 'Min', '25%', '75%', 'Max']

print(numeric_stats.to_string())

# Анализ целевой переменной
print("\n" + "=" * 60)
print("TARGET DISTRIBUTION")
print("=" * 60)

target_counts = df['target'].value_counts()
target_percent = df['target'].value_counts(normalize=True) * 100

print(f"\nMode class: {df['target'].mode()[0]}")
print(f"Mode count: {target_counts[df['target'].mode()[0]]}")

print("\nClass distribution:")
for val, count in target_counts.items():
    class_name = "Benign" if val == 1 else "Malignant"
    print(f"  {class_name} ({val}): {count} ({target_percent[val]:.1f}%)")

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
for col in X.columns:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)][col]
    outliers_info[col] = {
        'count': len(outliers),
        'percent': len(outliers) / len(df) * 100
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

# Распределение признаков
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Feature Distributions', fontsize=14)

features_to_plot = ['mean radius', 'mean texture', 'mean perimeter',
                    'mean area', 'mean smoothness', 'mean concavity']

for idx, feat in enumerate(features_to_plot):
    ax = axes[idx // 3, idx % 3]
    for target_val in [0, 1]:
        label = 'Malignant' if target_val == 0 else 'Benign'
        ax.hist(df[df['target'] == target_val][feat], bins=30, alpha=0.6, label=label)
    ax.set_xlabel(feat)
    ax.set_ylabel('Count')
    ax.legend()

plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab3/feature_distributions.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: feature_distributions.png")

# Корреляционная матрица
plt.figure(figsize=(14, 12))
correlation = df.corr()
mask = np.triu(np.ones_like(correlation, dtype=bool))
sns.heatmap(correlation, mask=mask, cmap='coolwarm', center=0,
            annot=False, fmt='.2f', cbar_kws={'label': 'Correlation'})
plt.title('Feature Correlation Matrix', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab3/correlation_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: correlation_matrix.png")

# Признаки с высокой корреляцией
target_corr = correlation['target'].abs().sort_values(ascending=False)
print("\n" + "=" * 60)
print("TOP 10 FEATURES CORRELATED WITH TARGET")
print("=" * 60)
for i, (feat, corr) in enumerate(target_corr[1:11].items(), 1):
    print(f"{i:2d}. {feat:25s}: {corr:.4f}")

# ============================================================================
# 4. Подготовка данных
# ============================================================================
print("\n" + "=" * 60)
print("4. DATA PREPARATION")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nTrain set: {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
print(f"Test set:  {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")

print(f"\nClass distribution in train:")
print(f"  0: {(y_train==0).sum()} ({(y_train==0).sum()/len(y_train)*100:.1f}%)")
print(f"  1: {(y_train==1).sum()} ({(y_train==1).sum()/len(y_train)*100:.1f}%)")

print(f"\nClass distribution in test:")
print(f"  0: {(y_test==0).sum()} ({(y_test==0).sum()/len(y_test)*100:.1f}%)")
print(f"  1: {(y_test==1).sum()} ({(y_test==1).sum()/len(y_test)*100:.1f}%)")

# Нормализация
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nData normalized (StandardScaler: mean=0, std=1)")
print(f"After normalization (train):")
print(f"  Mean: {X_train_scaled.mean():.6f}")
print(f"  Std: {X_train_scaled.std():.6f}")

# ============================================================================
# 5. Построение моделей
# ============================================================================
print("\n" + "=" * 60)
print("5. BUILDING CLASSIFICATION MODELS")
print("=" * 60)

def evaluate_model(model, X_train, X_test, y_train, y_test, model_name):
    """Train model and return metrics"""
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    if y_pred_proba is not None:
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    else:
        roc_auc = None
        fpr, tpr = None, None

    return {
        'model': model,
        'name': model_name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm,
        'roc_auc': roc_auc,
        'fpr': fpr,
        'tpr': tpr,
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba
    }

# Модель 1: KNN
print("\n" + "-" * 60)
print("MODEL 1: K-Nearest Neighbors (KNN)")
print("-" * 60)

knn = KNeighborsClassifier(n_neighbors=5)
knn_results = evaluate_model(knn, X_train_scaled, X_test_scaled, y_train, y_test, "KNN")

print(f"\nAccuracy (A): {knn_results['accuracy']:.4f}")
print(f"Precision (P): {knn_results['precision']:.4f}")
print(f"Recall (R): {knn_results['recall']:.4f}")
print(f"F1-score: {knn_results['f1']:.4f}")
print(f"ROC-AUC: {knn_results['roc_auc']:.4f}")

print("\nConfusion Matrix:")
print("                Predicted")
print("                0    1")
print(f"Actual  0   {knn_results['confusion_matrix'][0,0]:3d}  {knn_results['confusion_matrix'][0,1]:3d}")
print(f"        1   {knn_results['confusion_matrix'][1,0]:3d}  {knn_results['confusion_matrix'][1,1]:3d}")

tn, fp, fn, tp = knn_results['confusion_matrix'].ravel()
print(f"\nTN={tn}, FP={fp}, FN={fn}, TP={tp}")

# Модель 2: Logistic Regression
print("\n" + "-" * 60)
print("MODEL 2: Logistic Regression")
print("-" * 60)

log_reg = LogisticRegression(max_iter=5000, random_state=42)
log_reg_results = evaluate_model(log_reg, X_train, X_test, y_train, y_test, "Logistic Regression")

print(f"\nAccuracy (A): {log_reg_results['accuracy']:.4f}")
print(f"Precision (P): {log_reg_results['precision']:.4f}")
print(f"Recall (R): {log_reg_results['recall']:.4f}")
print(f"F1-score: {log_reg_results['f1']:.4f}")
print(f"ROC-AUC: {log_reg_results['roc_auc']:.4f}")

print("\nConfusion Matrix:")
print("                Predicted")
print("                0    1")
print(f"Actual  0   {log_reg_results['confusion_matrix'][0,0]:3d}  {log_reg_results['confusion_matrix'][0,1]:3d}")
print(f"        1   {log_reg_results['confusion_matrix'][1,0]:3d}  {log_reg_results['confusion_matrix'][1,1]:3d}")

tn, fp, fn, tp = log_reg_results['confusion_matrix'].ravel()
print(f"\nTN={tn}, FP={fp}, FN={fn}, TP={tp}")

# ============================================================================
# 6. Сравнение моделей
# ============================================================================
print("\n" + "=" * 70)
print("6. MODEL COMPARISON")
print("=" * 70)

results_df = pd.DataFrame({
    'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-score', 'ROC-AUC'],
    'KNN': [knn_results['accuracy'], knn_results['precision'],
           knn_results['recall'], knn_results['f1'], knn_results['roc_auc']],
    'Logistic Regression': [log_reg_results['accuracy'], log_reg_results['precision'],
                           log_reg_results['recall'], log_reg_results['f1'], log_reg_results['roc_auc']]
})

print("\n" + results_df.to_string(index=False))

# Лучшая модель
best_model = knn_results if knn_results['roc_auc'] > log_reg_results['roc_auc'] else log_reg_results

print("\n" + "=" * 60)
print(f"BEST MODEL: {best_model['name'].upper()}")
print("=" * 60)
print(f"\nROC-AUC: {best_model['roc_auc']:.4f}")
print(f"Accuracy: {best_model['accuracy']:.4f}")
print(f"Precision: {best_model['precision']:.4f}")
print(f"Recall: {best_model['recall']:.4f}")
print(f"F1-score: {best_model['f1']:.4f}")

# ============================================================================
# 7. Дополнительные визуализации
# ============================================================================
print("\n" + "=" * 60)
print("7. ADDITIONAL VISUALIZATIONS")
print("=" * 60)

# ROC-кривые
plt.figure(figsize=(10, 8))
plt.plot(knn_results['fpr'], knn_results['tpr'], label=f"KNN (AUC = {knn_results['roc_auc']:.4f})", linewidth=2)
plt.plot(log_reg_results['fpr'], log_reg_results['tpr'], label=f"Logistic Regression (AUC = {log_reg_results['roc_auc']:.4f})", linewidth=2)
plt.plot([0, 1], [0, 1], 'k--', label='Random classifier')
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('ROC Curves', fontsize=14)
plt.legend(loc='lower right', fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab3/roc_curves.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: roc_curves.png")

# Confusion Matrix для обеих моделей
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# KNN
sns.heatmap(knn_results['confusion_matrix'], annot=True, fmt='d', cmap='Blues',
            xticklabels=['Malignant', 'Benign'],
            yticklabels=['Malignant', 'Benign'], ax=axes[0])
axes[0].set_title('KNN Confusion Matrix', fontsize=12)
axes[0].set_xlabel('Predicted class')
axes[0].set_ylabel('Actual class')

# Logistic Regression
sns.heatmap(log_reg_results['confusion_matrix'], annot=True, fmt='d', cmap='Greens',
            xticklabels=['Malignant', 'Benign'],
            yticklabels=['Malignant', 'Benign'], ax=axes[1])
axes[1].set_title('Logistic Regression Confusion Matrix', fontsize=12)
axes[1].set_xlabel('Predicted class')
axes[1].set_ylabel('Actual class')

plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab3/confusion_matrices.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: confusion_matrices.png")

# Важность признаков для логистической регрессии
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Coefficient': log_reg.coef_[0],
    'Abs_Coefficient': np.abs(log_reg.coef_[0])
}).sort_values('Abs_Coefficient', ascending=False)

plt.figure(figsize=(12, 8))
colors = ['red' if x < 0 else 'green' for x in feature_importance['Coefficient']]
plt.barh(feature_importance['Feature'][:15], feature_importance['Coefficient'][:15], color=colors)
plt.xlabel('Regression Coefficient', fontsize=12)
plt.ylabel('Feature', fontsize=12)
plt.title('Feature Importance (Logistic Regression)', fontsize=14)
plt.axvline(x=0, color='black', linestyle='-')
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab3/feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: feature_importance.png")

print("\n" + "=" * 60)
print("TOP 10 FEATURES BY IMPORTANCE (Logistic Regression)")
print("=" * 60)
for i, row in feature_importance.head(10).iterrows():
    direction = "-> Benign" if row['Coefficient'] > 0 else "-> Malignant"
    print(f"{row['Abs_Coefficient']:6.3f}: {row['Feature']:25s} {direction}")

# ============================================================================
# 8. Выводы и идеи для улучшения
# ============================================================================
print("\n" + "=" * 60)
print("8. IDEAS FOR MODEL IMPROVEMENT")
print("=" * 60)

improvement_ideas = [
    ("Hyperparameter optimization", [
        "KNN: tune k using GridSearchCV",
        "Logistic Regression: tune regularization parameter C, L1/L2 penalty"
    ]),
    ("Feature selection", [
        "RFE (Recursive Feature Elimination)",
        "SelectKBest with statistical tests",
        "Remove highly correlated features"
    ]),
    ("Class balancing", [
        "SMOTE (Synthetic Minority Over-sampling)",
        "Class weighting (class_weight='balanced')"
    ]),
    ("Ensemble methods", [
        "Random Forest",
        "Gradient Boosting (XGBoost, LightGBM)",
        "Stacking/Blending models"
    ]),
    ("Outlier handling", [
        "Winsorization",
        "RobustScaler instead of StandardScaler"
    ]),
    ("Additional models", [
        "SVM with different kernels",
        "Neural Networks",
        "Naive Bayes"
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

conclusions = """
Dataset: Breast Cancer (569 samples, 30 features)
- Target: Tumor type (0=Malignant, 1=Benign)
- No missing values
- Class imbalance: ~37%/63%

Feature Analysis:
- High correlation among features (mean radius, mean perimeter, mean area)
- Outliers detected in some features
- All features are numeric

Model Comparison:
- KNN and Logistic Regression showed similar results
- ROC-AUC ~0.98-0.99 indicates excellent classification quality

Most Important Features:
- worst radius, worst perimeter, worst concave points
- mean concave points, mean concavity

Conclusion:
Both models achieved high classification accuracy (~97-98%),
indicating good dataset quality and informative features for
breast cancer diagnosis. Logistic Regression has the advantage
of interpretability (coefficients show feature influence).
"""
print(conclusions)

print("\n" + "=" * 50)
print("LAB 3 COMPLETED SUCCESSFULLY")
print("=" * 50)
