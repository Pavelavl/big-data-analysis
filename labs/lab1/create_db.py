"""Скрипт для создания SQLite базы данных из CSV-файла Nashville Housing."""
import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "nashville_housing.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "Nashville Housing.csv")

def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE housing (
            UniqueID INTEGER PRIMARY KEY,
            ParcelID TEXT,
            LandUse TEXT,
            PropertyAddress TEXT,
            SaleDate TEXT,
            SalePrice REAL,
            LegalReference TEXT,
            SoldAsVacant TEXT,
            OwnerName TEXT,
            OwnerAddress TEXT,
            Acreage REAL,
            TaxDistrict TEXT,
            LandValue REAL,
            BuildingValue REAL,
            TotalValue REAL,
            YearBuilt INTEGER,
            Bedrooms INTEGER,
            FullBath INTEGER,
            HalfBath INTEGER
        )
    """)

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            values = []
            for col in ["UniqueID ", "ParcelID", "LandUse", "PropertyAddress",
                         "SaleDate", "SalePrice", "LegalReference", "SoldAsVacant",
                         "OwnerName", "OwnerAddress", "Acreage", "TaxDistrict",
                         "LandValue", "BuildingValue", "TotalValue", "YearBuilt",
                         "Bedrooms", "FullBath", "HalfBath"]:
                val = row.get(col, "").strip()
                if val == "":
                    values.append(None)
                elif col in ("SalePrice", "Acreage", "LandValue", "BuildingValue", "TotalValue"):
                    try:
                        values.append(float(val.replace(",", "")))
                    except ValueError:
                        values.append(None)
                elif col in ("UniqueID ", "YearBuilt", "Bedrooms", "FullBath", "HalfBath"):
                    try:
                        values.append(int(float(val)))
                    except ValueError:
                        values.append(None)
                else:
                    values.append(val)
            cursor.execute(
                "INSERT INTO housing VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                values
            )

    conn.commit()
    count = cursor.execute("SELECT COUNT(*) FROM housing").fetchone()[0]
    print(f"Database created: {DB_PATH}")
    print(f"Records loaded: {count}")
    conn.close()

if __name__ == "__main__":
    create_database()
