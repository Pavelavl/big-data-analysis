# Nashville Housing — Исследовательский анализ данных

Лабораторная работа №1 по дисциплине «Анализ больших данных».

**Вариант 16** — Housing - SQL Project
**Сложность:** Rare (SQLite3)

## Описание

Проект выполняет первичный исследовательский анализ (EDA) базы данных Nashville Housing, содержащей 56 477 записей о продажах недвижимости в Нэшвилле, штат Теннесси.

Анализ включает:
- Подключение к SQLite базе данных из Python
- Описание структуры данных (таблицы, поля, типы, шкалы)
- Одномерный анализ — гистограммы распределения SalePrice и TotalValue
- Многомерный анализ — scatter-plot с 4 признаками (SalePrice, TotalValue, LandUse, Bedrooms)

## Структура проекта

```
lab1/
├── README.md                  # Описание проекта
├── Nashville Housing.csv      # Исходные данные (CSV)
├── create_db.py               # Скрипт создания SQLite базы из CSV
├── nashville_housing.db       # SQLite база данных
├── lab1_analysis.ipynb        # Jupyter Notebook с анализом
├── hist_sale_price.png        # Гистограмма SalePrice
├── hist_total_value.png       # Гистограмма TotalValue
└── multivariate_plot.png      # Многомерный график
```

## Инструкции по запуску

### Требования

- Python 3.10+
- Библиотеки: `pandas`, `matplotlib`, `seaborn`

### Установка зависимостей

```bash
pip install pandas matplotlib seaborn jupyter
```

### Создание базы данных

```bash
python create_db.py
```

Скрипт создаёт файл `nashville_housing.db` из `Nashville Housing.csv`.

### Запуск анализа

```bash
jupyter notebook lab1_analysis.ipynb
```

## Источник данных

[Housing - SQL Project](https://www.kaggle.com/datasets/bvanntruong/housing-sql-project) — Kaggle
