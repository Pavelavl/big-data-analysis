# Nashville Housing — Исследовательский анализ данных. Постановка гипотез

Лабораторная работа №2 по дисциплине «Анализ больших данных».

**Вариант 16** — Housing - SQL Project
**Сложность:** Medium (общая + самостоятельная часть)

## Описание

Проект выполняет исследовательский анализ данных (EDA), проверку статистических гипотез, кодирование категориальных переменных и реализацию градиентного спуска.

Работа состоит из двух частей:
1. **Общее задание** — датасет mpg из библиотеки Seaborn (398 записей, 9 признаков)
2. **Самостоятельное задание** — Nashville Housing из SQLite БД (56 477 записей, 19 признаков)

Анализ включает:
- Разведочный анализ числовых и категориальных переменных
- Формулировку и проверку статистических гипотез (t-тест Уэлча, критерий Пирсона)
- Кодирование категориальных переменных (LabelEncoding, OneHotEncoding)
- Построение корреляционных матриц с heatmap
- Реализацию обычного и стохастического градиентного спуска

## Структура проекта

```
lab2/
├── README.md                  # Описание проекта
├── lab2_analysis.ipynb        # Jupyter Notebook с анализом
├── corr_mpg.png               # Корреляционная матрица (mpg)
├── gradient_descent.png       # Графики градиентного спуска
└── corr_housing.png           # Корреляционная матрица (Nashville Housing)
```

## Инструкции по запуску

### Требования

- Python 3.10+
- Библиотеки: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `scikit-learn`
- БД из ЛР1: `../lab1/nashville_housing.db`

### Установка зависимостей

```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn jupyter
```

### Запуск анализа

```bash
jupyter notebook lab2_analysis.ipynb
```

## Источник данных

- [mpg dataset](https://github.com/mwaskom/seaborn-data) — Seaborn
- [Housing - SQL Project](https://www.kaggle.com/datasets/bvanntruong/housing-sql-project) — Kaggle
