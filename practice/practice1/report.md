================================================================================
РЕЗУЛЬТАТЫ SQL-ЗАПРОСОВ - ЗАДАЧА 1
================================================================================

================================================================================
ЗАПРОС 1: JOIN по двум таблицам (parcels + sales) с сортировкой и агрегацией
================================================================================

SQL:

SELECT
    p.ParcelID,
    p.LandUse,
    p.TaxDistrict,
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


Столбцы: ParcelID, LandUse, TaxDistrict, TotalSales, AvgSalePrice, MinSalePrice, MaxSalePrice, TotalSalesValue
Всего записей: 20

Пример результатов (первые 5):
--------------------------------------------------------------------------------
093 13 0B 134.00 | RESIDENTIAL CONDO |  | 2 | 27271530.0 | 265000.0 | 54278060.0 | 54543060.0
093 13 0B 456.00 | RESIDENTIAL CONDO |  | 2 | 27234030.0 | 190000.0 | 54278060.0 | 54468060.0
093 13 0B 108.00 | RESIDENTIAL CONDO |  | 2 | 27229030.0 | 180000.0 | 54278060.0 | 54458060.0
093 13 0B 322.00 | RESIDENTIAL CONDO |  | 2 | 27218030.0 | 158000.0 | 54278060.0 | 54436060.0
093 13 0B 447.00 | RESIDENTIAL CONDO |  | 2 | 27218030.0 | 158000.0 | 54278060.0 | 54436060.0


================================================================================
ЗАПРОС 2: JOIN по трем таблицам (parcels + properties + sales) с сортировкой и агрегацией
================================================================================

SQL:

SELECT
    p.ParcelID,
    prop.YearBuilt,
    p.LandUse,
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


Столбцы: ParcelID, YearBuilt, LandUse, SalesCount, AvgSalePrice, AvgTotalValue, PriceToValueRatio
Всего записей: 15

Пример результатов (первые 5):
--------------------------------------------------------------------------------
073 00 0 007.00 | NULL | VACANT RESIDENTIAL LAND | 1 | 12350000.0 | 50000.0 | 24700.0
073 00 0 042.00 | 1980 | CHURCH | 1 | 12350000.0 | 13940400.0 | 88.59
133 02 0 031.00 | NULL | PARKING LOT | 1 | 9500000.0 | 127700.0 | 7439.31
133 02 0 035.00 | NULL | VACANT COMMERCIAL LAND | 1 | 9500000.0 | 26000.0 | 36538.46
133 02 0 036.00 | NULL | VACANT COMMERCIAL LAND | 1 | 9500000.0 | 26000.0 | 36538.46


================================================================================
ЗАПРОС 3: Запрос по одному объекту по всем таблицам с JOIN и агрегацией
================================================================================

SQL:

SELECT
    p.ParcelID,
    p.LandUse,
    p.Acreage,
    p.TaxDistrict,
    a.PropertyAddress,
    a.OwnerAddress,
    prop.LandValue,
    prop.BuildingValue,
    prop.TotalValue,
    prop.YearBuilt,
    prop.Bedrooms,
    prop.FullBath,
    prop.HalfBath,
    o.OwnerName,
    COUNT(s.SaleID) as TotalSales,
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


Столбцы: ParcelID, LandUse, Acreage, TaxDistrict, PropertyAddress, OwnerAddress, LandValue, BuildingValue, TotalValue, YearBuilt, Bedrooms, FullBath, HalfBath, OwnerName, TotalSales, AvgSalePrice, FirstSaleDate, LastSaleDate, TotalSalesAmount
Всего записей: 1

Пример результатов (первые 5):
--------------------------------------------------------------------------------
119 05 0 186.00 | SINGLE FAMILY | 0.34 | URBAN SERVICES DISTRICT | 316  LUTIE ST, NASHVILLE | 316  LUTIE ST, NASHVILLE, TN | 25000.0 | 138100.0 | 164800.0 | 1910 | 2 | 1 | 0 | HENDERSON, JAMES P. & LYNN P. | 4 | 140500.0 | August 12, 2014 | January 23, 2013 | 562000.0


================================================================================
ЗАПРОС 4: Подсчет количества строк по совмещенным данным (parcels + addresses + sales)
================================================================================

SQL:

SELECT
    p.LandUse,
    COUNT(DISTINCT p.ParcelID) as UniqueParcels,
    COUNT(DISTINCT a.AddressID) as UniqueAddresses,
    COUNT(s.SaleID) as TotalSales,
    ROUND(AVG(s.SalePrice), 2) as AvgSalePrice
FROM parcels p
LEFT JOIN addresses a ON p.ParcelID = a.ParcelID
LEFT JOIN sales s ON p.ParcelID = s.ParcelID
GROUP BY p.LandUse
ORDER BY UniqueParcels DESC;


Столбцы: LandUse, UniqueParcels, UniqueAddresses, TotalSales, AvgSalePrice
Всего записей: 39

Пример результатов (первые 5):
--------------------------------------------------------------------------------
SINGLE FAMILY | 29151 | 33432 | 42847 | 285158.98
RESIDENTIAL CONDO | 12479 | 13958 | 17052 | 439400.89
VACANT RESIDENTIAL LAND | 2845 | 4004 | 6592 | 313890.3
DUPLEX | 1257 | 1414 | 1754 | 282601.44
VACANT RES LAND | 1238 | 1916 | 3465 | 239830.72


================================================================================
ЗАПРОС 5.1: Анализ цен по налоговому округу и типу использования
================================================================================

SQL:

SELECT
    p.TaxDistrict,
    p.LandUse,
    COUNT(s.SaleID) as SalesCount,
    ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
    ROUND(MIN(s.SalePrice), 2) as MinSalePrice,
    ROUND(MAX(s.SalePrice), 2) as MaxSalePrice,
    ROUND(SUM(s.SalePrice), 2) as TotalValue,
    ROUND(SQRT(AVG(s.SalePrice * s.SalePrice) - AVG(s.SalePrice) * AVG(s.SalePrice)), 2) as StdDev
FROM parcels p
JOIN sales s ON p.ParcelID = s.ParcelID
WHERE s.SalePrice > 0
GROUP BY p.TaxDistrict, p.LandUse
HAVING SalesCount >= 10
ORDER BY AvgSalePrice DESC;


Столбцы: TaxDistrict, LandUse, SalesCount, AvgSalePrice, MinSalePrice, MaxSalePrice, TotalValue, StdDev
Всего записей: 39

Пример результатов (первые 5):
--------------------------------------------------------------------------------
CITY OF BELLE MEADE | SINGLE FAMILY | 221 | 1419543.88 | 27500.0 | 7200000.0 | 313719197.0 | 857689.32
 | CONDO | 238 | 1281853.82 | 14000.0 | 4250000.0 | 305081210.0 | 1653240.51
 | CONDOMINIUM OFC  OR OTHER COM CONDO | 35 | 1254597.14 | 140000.0 | 4000000.0 | 43910900.0 | 1622924.16
URBAN SERVICES DISTRICT | CHURCH | 23 | 912847.83 | 50000.0 | 12350000.0 | 20995500.0 | 2474203.7
CITY OF FOREST HILLS | VACANT RESIDENTIAL LAND | 38 | 911059.21 | 20000.0 | 5000000.0 | 34620250.0 | 1007994.64


================================================================================
ЗАПРОС 5.2: Владельцы с наибольшим количеством продаж
================================================================================

SQL:

SELECT
    o.OwnerName,
    COUNT(s.SaleID) as PropertiesSold,
    COUNT(DISTINCT s.ParcelID) as UniqueParcels,
    ROUND(SUM(s.SalePrice), 2) as TotalSalesValue,
    ROUND(AVG(s.SalePrice), 2) as AvgSalePrice,
    ROUND(MIN(s.SalePrice), 2) as MinSalePrice,
    ROUND(MAX(s.SalePrice), 2) as MaxSalePrice
FROM owners o
JOIN sales s ON o.OwnerID = s.OwnerID
WHERE s.SalePrice > 0
GROUP BY o.OwnerName, o.OwnerID
HAVING PropertiesSold >= 2
ORDER BY TotalSalesValue DESC
LIMIT 20;


Столбцы: OwnerName, PropertiesSold, UniqueParcels, TotalSalesValue, AvgSalePrice, MinSalePrice, MaxSalePrice
Всего записей: 20

Пример результатов (первые 5):
--------------------------------------------------------------------------------
HILL 33, LLC | 24 | 24 | 105600000.0 | 4400000.0 | 4400000.0 | 4400000.0
RADNOR II, L.P. | 6 | 6 | 57000000.0 | 9500000.0 | 9500000.0 | 9500000.0
CATHOLIC DIOCESE OF NASHVILLE | 3 | 3 | 24875000.0 | 8291666.67 | 175000.0 | 12350000.0
CUMBERLAND DEVELOPMENT PARTNERS, LLC | 10 | 10 | 20400000.0 | 2040000.0 | 2040000.0 | 2040000.0
WALLACE, ANNE B. | 14 | 12 | 12149000.0 | 867785.71 | 110000.0 | 1725000.0


================================================================================
ЗАПРОС 5.3: Анализ постройки по десятилетиям (с CTE)
================================================================================

SQL:

WITH DecadeCategories AS (
    SELECT
        prop.ParcelID,
        prop.YearBuilt,
        CASE
            WHEN prop.YearBuilt < 1900 THEN 'Before 1900'
            WHEN prop.YearBuilt < 1920 THEN '1900-1919'
            WHEN prop.YearBuilt < 1940 THEN '1920-1939'
            WHEN prop.YearBuilt < 1960 THEN '1940-1959'
            WHEN prop.YearBuilt < 1980 THEN '1960-1979'
            WHEN prop.YearBuilt < 2000 THEN '1980-1999'
            ELSE '2000+'
        END as Decade,
        prop.TotalValue,
        prop.Bedrooms
    FROM properties prop
    WHERE prop.YearBuilt IS NOT NULL AND prop.TotalValue IS NOT NULL
)
SELECT
    Decade,
    COUNT(*) as PropertiesCount,
    ROUND(AVG(TotalValue), 2) as AvgTotalValue,
    ROUND(AVG(Bedrooms), 2) as AvgBedrooms,
    ROUND(MIN(TotalValue), 2) as MinTotalValue,
    ROUND(MAX(TotalValue), 2) as MaxTotalValue
FROM DecadeCategories
GROUP BY Decade
ORDER BY Decade;


Столбцы: Decade, PropertiesCount, AvgTotalValue, AvgBedrooms, MinTotalValue, MaxTotalValue
Всего записей: 7

Пример результатов (первые 5):
--------------------------------------------------------------------------------
1900-1919 | 353 | 323629.22 | 3.17 | 31600.0 | 1970500.0
1920-1939 | 2966 | 280201.31 | 3.09 | 13900.0 | 3157400.0
1940-1959 | 6673 | 206423.13 | 2.83 | 14300.0 | 2909700.0
1960-1979 | 5383 | 187463.51 | 3.24 | 12600.0 | 3723900.0
1980-1999 | 3109 | 185149.61 | 3.05 | 26100.0 | 13940400.0




================================================================================
РЕЗУЛЬТАТЫ PANDAS ЗАПРОСОВ - ЗАДАЧА 2 (PANDAS-ВЕРСИЯ)
================================================================================

================================================================================
ЗАПРОС 1: JOIN по двум таблицам (parcels + sales) с сортировкой и агрегацией
================================================================================

Столбцы: parcel_id, land_use, tax_district, total_sales, avg_sale_price, min_sale_price, max_sale_price, total_sales_value
Всего записей: 20

Пример результатов (первые 10):
--------------------------------------------------------------------------------
073 00 0 007.00 | VACANT RESIDENTIAL LAND | URBAN SERVICES DISTRICT | 1 | 12350000.0 | 12350000.0 | 12350000.0 | 12350000.0
073 00 0 042.00 | CHURCH | URBAN SERVICES DISTRICT | 1 | 12350000.0 | 12350000.0 | 12350000.0 | 12350000.0
117 07 0 137.00 | SINGLE FAMILY | URBAN SERVICES DISTRICT | 2 | 5978750.0 | 1207500.0 | 10750000.0 | 11957500.0
133 02 0 037.00 | VACANT COMMERCIAL LAND | URBAN SERVICES DISTRICT | 1 | 9500000.0 | 9500000.0 | 9500000.0 | 9500000.0
133 02 0 035.00 | VACANT COMMERCIAL LAND | URBAN SERVICES DISTRICT | 1 | 9500000.0 | 9500000.0 | 9500000.0 | 9500000.0
133 02 0 036.00 | VACANT COMMERCIAL LAND | URBAN SERVICES DISTRICT | 1 | 9500000.0 | 9500000.0 | 9500000.0 | 9500000.0
133 02 0 038.00 | VACANT COMMERCIAL LAND | URBAN SERVICES DISTRICT | 1 | 9500000.0 | 9500000.0 | 9500000.0 | 9500000.0
133 02 0 031.00 | PARKING LOT | URBAN SERVICES DISTRICT | 1 | 9500000.0 | 9500000.0 | 9500000.0 | 9500000.0
133 02 0 381.00 | VACANT COMMERCIAL LAND | URBAN SERVICES DISTRICT | 1 | 9500000.0 | 9500000.0 | 9500000.0 | 9500000.0
130 03 0 122.00 | SINGLE FAMILY | CITY OF BELLE MEADE | 1 | 7200000.0 | 7200000.0 | 7200000.0 | 7200000.0


================================================================================
ЗАПРОС 2: JOIN по трем таблицам (parcels + properties + sales) с сортировкой и агрегацией
================================================================================

Столбцы: parcel_id, year_built, land_use, sales_count, avg_sale_price, avg_total_value, price_to_value_ratio
Всего записей: 15

Пример результатов (первые 10):
--------------------------------------------------------------------------------
073 00 0 042.00 | 1980.0 | CHURCH | 1 | 12350000.0 | 13940400.0 | 88.59143209663998
130 03 0 122.00 | 1990.0 | SINGLE FAMILY | 1 | 7200000.0 | 5697100.0 | 126.38008811500588
117 07 0 137.00 | 1953.0 | SINGLE FAMILY | 2 | 5978750.0 | 911800.0 | 655.7084887036631
144 01 0 005.00 | 1929.0 | SINGLE FAMILY | 1 | 5000000.0 | 2348300.0 | 212.9199846697611
144 00 0 102.00 | 2005.0 | SINGLE FAMILY | 1 | 5000000.0 | 2927200.0 | 170.81169718502323
144 00 0 012.00 | 1996.0 | SINGLE FAMILY | 1 | 4500000.0 | 4058100.0 | 110.88933244621867
132 10 0 034.00 | 1935.0 | SINGLE FAMILY | 1 | 4450000.0 | 3151300.0 | 141.2115634817377
092 09 0 285.02 | 1963.0 | DUPLEX | 1 | 4400000.0 | 65400.0 | 6727.82874617737
092 09 0 277.00 | 1967.0 | SINGLE FAMILY | 1 | 4400000.0 | 171400.0 | 2567.0945157526253
092 09 0 285.01 | 1963.0 | SINGLE FAMILY | 1 | 4400000.0 | 182700.0 | 2408.31964969896


================================================================================
ЗАПРОС 3: Запрос по объекту 119 05 0 186.00 по всем таблицам с JOIN и агрегацией
================================================================================

Столбцы: parcel_id, land_use, acreage, tax_district, property_address, owner_address, land_value, building_value, total_value, year_built, bedrooms, full_bath, half_bath, owner_name, total_sales, avg_sale_price, first_sale_date, last_sale_date, total_sales_amount
Всего записей: 1

Пример результатов (первые 10):
--------------------------------------------------------------------------------
119 05 0 186.00 | SINGLE FAMILY | 0.34 | URBAN SERVICES DISTRICT | 316  LUTIE ST, NASHVILLE | 316  LUTIE ST, NASHVILLE, TN | 25000.0 | 138100.0 | 164800.0 | 1910.0 | 2.0 | 1.0 | 0.0 | HENDERSON, JAMES P. & LYNN P. | 2 | 140500.0 | August 12, 2014 | January 23, 2013 | 281000.0


================================================================================
ЗАПРОС 4: Подсчет количества строк по совмещенным данным (parcels + addresses + sales)
================================================================================

Столбцы: land_use, unique_parcels, unique_addresses, total_sales, avg_sale_price
Всего записей: 39

Пример результатов (первые 10):
--------------------------------------------------------------------------------
SINGLE FAMILY | 29151 | 29151 | 35685 | 284304.8448928121
RESIDENTIAL CONDO | 12479 | 12479 | 15008 | 429358.6588486141
VACANT RESIDENTIAL LAND | 2845 | 2845 | 4775 | 335662.30513089005
DUPLEX | 1257 | 1257 | 1514 | 276311.7919418758
VACANT RES LAND | 1238 | 1238 | 2147 | 253439.98882161157
ZERO LOT LINE | 974 | 974 | 1091 | 124719.98166819432
CONDO | 213 | 213 | 261 | 1192739.1379310344
TRIPLEX | 87 | 87 | 100 | 283449.31
RESIDENTIAL COMBO/MISC | 81 | 81 | 125 | 378099.824
QUADPLEX | 39 | 39 | 40 | 364785.0


