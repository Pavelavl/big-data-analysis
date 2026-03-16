#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lab 5: Unsupervised Learning - Clustering and Dimensionality Reduction
Rare complexity: 1 clustering method + PCA
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import (silhouette_score, adjusted_rand_score,
                             adjusted_mutual_info_score, confusion_matrix)
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
print("LAB 5: UNSUPERVISED LEARNING")
print("Clustering and Dimensionality Reduction")
print("=" * 50)

# ============================================================================
# 1. Загрузка данных
# ============================================================================
print("\n" + "=" * 50)
print("1. LOADING DATA")
print("=" * 50)

# Используем Iris dataset для кластеризации
data = datasets.load_iris()

X = pd.DataFrame(data["data"], columns=data["feature_names"])
y = data["target"]

df = X.copy()
df['target'] = y
df['species'] = [data['target_names'][t] for t in y]

print(f"\nDataset: Iris")
print(f"\nTarget variable: Species (3 classes)")
print(f"  {data['target_names']}")
print(f"\nFeatures ({len(data['feature_names'])}):")
for i, feat in enumerate(data['feature_names'], 1):
    print(f"  {i}. {feat}")

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

# Статистика
print("\nNumeric variables statistics:")
numeric_stats = X.describe(percentiles=[0.25, 0.5, 0.75]).T
numeric_stats = numeric_stats[['count', 'mean', '50%', 'min', '25%', '75%', 'max']]
numeric_stats.columns = ['Count', 'Mean', 'Median', 'Min', '25%', '75%', 'Max']

print(numeric_stats.to_string())

# Распределение классов
print("\n" + "=" * 60)
print("CLASS DISTRIBUTION")
print("=" * 60)

class_counts = df['species'].value_counts()
class_percent = df['species'].value_counts(normalize=True) * 100

for species, count in class_counts.items():
    print(f"  {species}: {count} ({class_percent[species]:.1f}%)")

# Корреляционная матрица
print("\n" + "=" * 60)
print("FEATURE CORRELATIONS")
print("=" * 60)

correlation = X.corr()
print(correlation.to_string())

# ============================================================================
# 3. Визуализация
# ============================================================================
print("\n" + "=" * 60)
print("3. CREATING VISUALIZATIONS")
print("=" * 60)

# Scatter plot
plt.figure(figsize=(12, 10))
colors = ['red', 'green', 'blue']
for i, species in enumerate(data['target_names']):
    species_df = df[df['species'] == species]
    plt.scatter(species_df.iloc[:, 0], species_df.iloc[:, 1],
                c=colors[i], label=species, alpha=0.7, edgecolors='black')

plt.xlabel(data['feature_names'][0])
plt.ylabel(data['feature_names'][1])
plt.title('Iris Dataset: Sepal Length vs Sepal Width')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab5/iris_scatter.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: iris_scatter.png")

# Boxplot по признакам
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Feature Distribution by Species', fontsize=14)

for idx, feat in enumerate(data['feature_names']):
    ax = axes[idx // 2, idx % 2]
    for i, species in enumerate(data['target_names']):
        species_data = df[df['species'] == species][feat]
        ax.boxplot(species_data, positions=[i], widths=0.6,
                   patch_artist=True, boxprops=dict(facecolor=colors[i], alpha=0.7),
                   medianprops=dict(color='black', linewidth=2))
    ax.set_xticks(range(3))
    ax.set_xticklabels(data['target_names'], rotation=45)
    ax.set_ylabel(feat)
    ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab5/feature_boxplots.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: feature_boxplots.png")

# ============================================================================
# 4. PCA - Снижение размерности
# ============================================================================
print("\n" + "=" * 60)
print("4. PCA - DIMENSIONALITY REDUCTION")
print("=" * 60)

# Нормализация данных перед PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA с максимальным количеством компонент
pca = PCA()
X_pca = pca.fit_transform(X_scaled)

print("\nExplained Variance Ratio:")
for i, ratio in enumerate(pca.explained_variance_ratio_, 1):
    cumsum = np.sum(pca.explained_variance_ratio_[:i])
    print(f"  PC{i}: {ratio:.4f} (Cumulative: {cumsum:.4f})")

# График объясненной дисперсии
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.bar(range(1, len(pca.explained_variance_ratio_) + 1),
        pca.explained_variance_ratio_, alpha=0.7, edgecolor='black')
plt.xlabel('Principal Component')
plt.ylabel('Explained Variance Ratio')
plt.title('Explained Variance by Component')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(range(1, len(pca.explained_variance_ratio_) + 1),
         np.cumsum(pca.explained_variance_ratio_), 'bo-')
plt.axhline(y=0.95, color='r', linestyle='--', label='95% threshold')
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance')
plt.title('Cumulative Explained Variance')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab5/pca_variance.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: pca_variance.png")

# PCA для визуализации (2 компоненты)
pca_2d = PCA(n_components=2)
X_pca_2d = pca_2d.fit_transform(X_scaled)

print(f"\nPCA (2 components):")
print(f"  Explained variance: {np.sum(pca_2d.explained_variance_ratio_):.4f}")
print(f"  PC1: {pca_2d.explained_variance_ratio_[0]:.4f}")
print(f"  PC2: {pca_2d.explained_variance_ratio_[1]:.4f}")

# Визуализация PCA с истинными метками
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
for i, species in enumerate(data['target_names']):
    mask = y == i
    plt.scatter(X_pca_2d[mask, 0], X_pca_2d[mask, 1],
                c=colors[i], label=species, alpha=0.7, edgecolors='black')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title('PCA with True Labels')
plt.legend()
plt.grid(True, alpha=0.3)

# Визуализация PCA с загружками признаков
plt.subplot(1, 2, 2)
for i, species in enumerate(data['target_names']):
    mask = y == i
    plt.scatter(X_pca_2d[mask, 0], X_pca_2d[mask, 1],
                c=colors[i], label=species, alpha=0.7)

# Добавляем векторы загрузок (loadings)
loadings = pca_2d.components_.T * np.sqrt(pca_2d.explained_variance_)
for i, feat in enumerate(data['feature_names']):
    plt.arrow(0, 0, loadings[i, 0], loadings[i, 1],
                color='black', alpha=0.5, head_width=0.1)
    plt.text(loadings[i, 0] * 1.1, loadings[i, 1] * 1.1, feat,
              fontsize=9, ha='center', va='center')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title('PCA with Loadings')
plt.grid(True, alpha=0.3)
plt.xlim(-3, 3)
plt.ylim(-2, 2)

plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab5/pca_2d_visualization.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: pca_2d_visualization.png")

# ============================================================================
# 5. KMeans Clustering
# ============================================================================
print("\n" + "=" * 60)
print("5. KMEANS CLUSTERING")
print("=" * 60)

# Метод локтя для определения оптимального числа кластеров
inertia = []
silhouette_scores = []
k_range = range(2, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertia.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

# График метода локтя
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(k_range, inertia, 'bo-')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia (Within-cluster sum of squares)')
plt.title('Elbow Method')
plt.grid(True, alpha=0.3)

# Находим "локоть" простым методом
def find_elbow(x_values, y_values):
    """Find elbow point using maximum distance from line"""
    p1 = np.array([x_values[0], y_values[0]])
    p2 = np.array([x_values[-1], y_values[-1]])
    max_dist = 0
    elbow_idx = 0

    for i in range(len(x_values)):
        p = np.array([x_values[i], y_values[i]])
        d = np.abs(np.cross(p2-p1, p1-p)) / np.linalg.norm(p2-p1)
        if d > max_dist:
            max_dist = d
            elbow_idx = i

    return x_values[elbow_idx]

optimal_k = find_elbow(list(k_range), inertia)
plt.axvline(x=optimal_k, color='r', linestyle='--',
            label=f'Elbow at k={optimal_k}')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(k_range, silhouette_scores, 'go-')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Method')
plt.axvline(x=np.argmax(silhouette_scores) + 2, color='r', linestyle='--',
            label=f'Best k={np.argmax(silhouette_scores) + 2}')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab5/cluster_evaluation.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: cluster_evaluation.png")

print(f"\nOptimal number of clusters (Elbow): {optimal_k}")
print(f"Optimal number of clusters (Silhouette): {np.argmax(silhouette_scores) + 2}")

# KMeans с оптимальным числом кластеров (используем 3 так как знаем истинное число классов)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(X_scaled)
labels = kmeans.labels_

print(f"\nKMeans Clustering Results (k=3):")
print(f"  Silhouette Score: {silhouette_score(X_scaled, labels):.4f}")
print(f"  ARI: {adjusted_rand_score(y, labels):.4f}")
print(f"  AMI: {adjusted_mutual_info_score(y, labels):.4f}")

# Распределение кластеров
print(f"\nCluster distribution:")
for i in range(3):
    print(f"  Cluster {i}: {np.sum(labels == i)} samples")

# ============================================================================
# 6. Визуализация кластеров
# ============================================================================
print("\n" + "=" * 60)
print("6. CLUSTER VISUALIZATION")
print("=" * 60)

# Визуализация кластеров в пространстве PCA
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
for i in range(3):
    mask = labels == i
    plt.scatter(X_pca_2d[mask, 0], X_pca_2d[mask, 1],
                label=f'Cluster {i}', alpha=0.7, edgecolors='black')
# Transform centroids to PCA space
centroids_pca = pca_2d.transform(kmeans.cluster_centers_)
plt.scatter(centroids_pca[:, 0], centroids_pca[:, 1],
            marker='x', s=200, c='red', label='Centroids', linewidths=3)
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title('KMeans Clusters (PCA)')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
for i, species in enumerate(data['target_names']):
    mask = y == i
    plt.scatter(X_pca_2d[mask, 0], X_pca_2d[mask, 1],
                c=colors[i], label=species, alpha=0.7, edgecolors='black')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title('True Labels (PCA)')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab5/kmeans_pca.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: kmeans_pca.png")

# Матрица несоответствия кластеров и истинных меток
conf_mat = confusion_matrix(y, labels)

plt.figure(figsize=(10, 8))
sns.heatmap(conf_mat, annot=True, fmt='d', cmap='Blues',
            xticklabels=[f'Cluster {i}' for i in range(3)],
            yticklabels=data['target_names'])
plt.xlabel('Predicted Cluster')
plt.ylabel('True Species')
plt.title('Confusion Matrix: True Labels vs Clusters')
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab5/cluster_confusion.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: cluster_confusion.png")

# Silhouette plot
from sklearn.metrics import silhouette_samples

plt.figure(figsize=(12, 6))
y_lower = 10

for i in range(3):
    cluster_silhouette_values = silhouette_samples(X_scaled, labels)
    ith_cluster_silhouette_values = cluster_silhouette_values[labels == i]

    ith_cluster_silhouette_values.sort()

    size_cluster_i = ith_cluster_silhouette_values.shape[0]
    y_upper = y_lower + size_cluster_i

    plt.fill_betweenx(np.arange(y_lower, y_upper),
                     0, ith_cluster_silhouette_values,
                     alpha=0.7, edgecolor='black')

    plt.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
    y_lower = y_upper + 10

plt.axvline(x=silhouette_score(X_scaled, labels), color="red", linestyle="--",
            label=f'Average Score: {silhouette_score(X_scaled, labels):.3f}')
plt.xlabel('Silhouette Score')
plt.ylabel('Cluster')
plt.title('Silhouette Plot for KMeans')
plt.legend()
plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab5/silhouette_plot.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: silhouette_plot.png")

# ============================================================================
# 7. Анализ центроидов кластеров
# ============================================================================
print("\n" + "=" * 60)
print("7. CLUSTER CENTROIDS ANALYSIS")
print("=" * 60)

# Центроиды в исходном масштабе
centroids = scaler.inverse_transform(kmeans.cluster_centers_)
centroids_df = pd.DataFrame(centroids, columns=data['feature_names'])

print("\nCluster Centroids (original scale):")
print(centroids_df.to_string())

# Визуализация центроидов
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Cluster Centroids by Feature', fontsize=14)

for idx, feat in enumerate(data['feature_names']):
    ax = axes[idx // 2, idx % 2]
    ax.bar(range(3), centroids_df[feat],
            color=colors[:3], alpha=0.7, edgecolor='black')
    ax.set_xlabel('Cluster')
    ax.set_ylabel(feat)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f'C{i}' for i in range(3)])
    ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('G:/Studies/TSTU/korneeva/4 couse 2 sem/big-data-analysis/labs/lab5/centroids_barplot.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: centroids_barplot.png")

# ============================================================================
# 8. Идеи для улучшения
# ============================================================================
print("\n" + "=" * 60)
print("8. IDEAS FOR IMPROVEMENT")
print("=" * 60)

improvement_ideas = [
    ("Additional clustering methods", [
        "Hierarchical Clustering (Agglomerative)",
        "DBSCAN (Density-Based Spatial Clustering)",
        "Gaussian Mixture Models (GMM)",
        "Spectral Clustering"
    ]),
    ("Additional dimensionality reduction", [
        "t-SNE (t-Distributed Stochastic Neighbor Embedding)",
        "UMAP (Uniform Manifold Approximation and Projection)",
        "LDA (Linear Discriminant Analysis) - supervised"
    ]),
    ("Feature engineering", [
        "Interaction terms between features",
        "Polynomial features",
        "Domain-specific feature transformations"
    ]),
    ("Model optimization", [
        "Try different distance metrics (cosine, manhattan)",
        "Use MiniBatchKMeans for large datasets",
        "Ensemble clustering methods"
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
Dataset: Iris ({len(df)} samples, {len(X.columns)} features)
- Target: 3 species (setosa, versicolor, virginica)
- Features: 4 measurements (sepal/petal length/width)

PCA Analysis:
- PC1 explains {pca.explained_variance_ratio_[0]*100:.2f}% of variance
- PC2 explains {pca.explained_variance_ratio_[1]*100:.2f}% of variance
- 2 PCs explain {np.sum(pca.explained_variance_ratio_[:2])*100:.2f}% total variance
- PC1 is dominated by petal measurements
- PC2 separates based on sepal measurements

KMeans Clustering (k=3):
- Silhouette Score: {silhouette_score(X_scaled, labels):.4f}
- ARI: {adjusted_rand_score(y, labels):.4f} (perfect = 1.0)
- AMI: {adjusted_mutual_info_score(y, labels):.4f} (perfect = 1.0)

Interpretation:
- High ARI and AMI scores indicate good alignment with true labels
- Setosa is well-separated in the original space
- Versicolor and Virginica have some overlap
- Petal length and width are the most discriminative features
"""

print(conclusions)

print("\n" + "=" * 50)
print("LAB 5 COMPLETED SUCCESSFULLY")
print("=" * 50)
