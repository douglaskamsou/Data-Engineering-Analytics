# Destatis Population Data Warehouse

## End-to-End Data Engineering Project

An end-to-end Data Engineering project based on population and
employment statistics from the German Federal Statistical Office
(Destatis).

The project demonstrates the complete data pipeline from raw
statistical data to a dimensional Data Warehouse, REST API and
interactive Power BI dashboard.

---

## 📊 Project Overview

The goal of this project is to build a reproducible Data Warehouse
for analysing population and employment-related metrics over time,
by gender and age group.

The project follows an end-to-end Data Engineering architecture:

```text
Destatis CSV
     │
     ▼
Python ETL
     │
     ▼
Data Cleaning
     │
     ▼
fact_metric_ready
     │
     ▼
SQLite Data Warehouse
     │
     ├──────────────┐
     │              │
     ▼              ▼
Dimensions      fact_metric
     │              │
     └───────┬──────┘
             ▼
     mart_population_metrics
             │
             ▼
        FastAPI REST API
             │
             ▼
            JSON
             │
             ▼
          Power BI
             │
             ▼
   Interactive Dashboard

# 🎯 Business Questions

The Data Warehouse can be used to answer questions such as:

- How has the population in main-residence households changed over the years?
- How does the population differ by gender?
- How does the population differ by age group?
- How have employment and unemployment developed over time?
- How do employment-related metrics differ between age groups?
- What are the differences between male and female populations?
- How do the different statistical metrics develop over time?

# 🗃️ Data Source

The project uses statistical data from the German Federal Statistical
Office (Destatis).

Dataset:

12211-0001

The dataset contains information related to population and
employment in main-residence households.

The relevant metrics include:

| Metric Code | Description                                      |
| ----------- | ------------------------------------------------ |
| BEV036      | Bevölkerung in Hauptwohnsitzhaushalten           |
| ERW040      | Erwerbspersonen aus Hauptwohnsitzhaushalten      |
| ERW041      | Erwerbstätige aus Hauptwohnsitzhaushalten        |
| ERW042      | Erwerbslose aus Hauptwohnsitzhaushalten          |
| ERW043      | Nichterwerbspersonen aus Hauptwohnsitzhaushalten |

The data covers multiple years and is available by gender and
age group.


# 🏗️ Architecture

The project consists of several layers.

# 1. Data Source

Raw statistical data is obtained from Destatis.

12211-0001_de_flat.csv

# 2. Data Cleaning

The raw CSV is processed using Python and Pandas.

The cleaning process includes:

- standardising column names
- removing unnecessary whitespace
- handling missing values
- handling duplicate records
- converting numerical values
- creating consistent data types
- preparing the dataset for dimensional modelling

Output:

12211-0001_de_flat_clean.csv

# 3. Data Preparation

The cleaned Destatis structure is transformed into a simplified
metric-oriented format.

Input:

12211-0001_de_flat_clean.csv

Output:

fact_metric_ready.csv

The resulting structure is:
```text
| Column       | Description          |
| ------------ | -------------------- |
| year         | Statistical year     |
| gender       | Gender               |
| age_group    | Age group            |
| metric_code  | Destatis metric code |
| metric_name  | Metric description   |
| metric_value | Statistical value    |

Example:

year | gender    | age_group              | metric_code | metric_value
-----|-----------|------------------------|-------------|-------------
2020 | Insgesamt | 15 bis unter 20 Jahre  | BEV036      | 3893
2020 | Insgesamt | 15 bis unter 20 Jahre  | ERW040      | 1156
2020 | Insgesamt | 15 bis unter 20 Jahre  | ERW041      | 1044


# ⭐ Star Schema

The Data Warehouse uses a dimensional Star Schema.
```text
                       ┌───────────────┐
                       │   dim_date    │
                       └───────┬───────┘
                               │
                               │
┌───────────────┐       ┌──────▼──────┐       ┌───────────────┐
│  dim_gender   │──────▶│ fact_metric │◀──────│  dim_metric   │
└───────────────┘       └──────┬──────┘       └───────────────┘
                               │
                               │
                       ┌───────▼─────────┐
                       │  dim_age_group  │
                       └─────────────────┘

# Dimension Tables

## dim_date
Contains the time dimension.

date_key
year

Example:
```text
date_key | year
---------|-----
1        | 2020
2        | 2021
3        | 2022
4        | 2023

## dim_gender

Contains gender information.
```text
gender_key
gender_code
gender_name

Example:

gender_key | gender_code | gender_name
-----------|-------------|-------------
1          | G001        | Insgesamt
2          | G002        | männlich
3          | G003        | weiblich

## dim_age_group

Contains age-group information.
```text
age_group_key
age_group_code
age_group_name

## dim_metric

Contains the statistical metrics.

metric_key
metric_code
metric_name

Example:
```text
metric_key | metric_code | metric_name
-----------|-------------|-----------------------------
1          | BEV036      | Bevölkerung ...
2          | ERW040      | Erwerbspersonen ...
3          | ERW041      | Erwerbstätige ...
4          | ERW042      | Erwerbslose ...
5          | ERW043      | Nichterwerbspersonen ...

# 📦 Fact Table

The central fact table is:

fact_metric

Structure:
```text
metric_fact_key
date_key
gender_key
age_group_key
metric_key
metric_value

The fact table contains the measurable statistical value and foreign
keys to the dimensions.

This design separates:

- descriptive attributes → Dimension tables
- measurable values → Fact table

# 🏪 Data Mart

For analytics and reporting, the project creates:

mart_population_metrics

The Data Mart provides a simplified analytical representation of the
Data Warehouse.

It is used by:
```text
SQLite
   │
   ├── FastAPI
   │
   └── Power BI

# 🔄 ETL Pipeline

The ETL process is implemented in **Python**.
```text
Extract
   │
   ▼
Destatis CSV
   │
   ▼
Transform
   │
   ├── Clean columns
   ├── Clean values
   ├── Handle missing values
   ├── Convert data types
   └── Prepare metrics
   │
   ▼
Load
   │
   ▼
SQLite Data Warehouse

# 🐍 Python ETL

The main ETL scripts are:
```text
etl/
│
├── 01_load_destatis.py
├── 02_clean_data.py
├── 03_create_dimensions.py
├── 04_create_fact_metric.py
└── 05_create_data_mart.py
```

**01_load_destatis.py**

Loads the Destatis source data.

**02_clean_data.py**

Cleans and standardises the raw dataset.

**03_create_dimensions.py**

Creates:
```text
dim_date
dim_gender
dim_age_group
dim_metric
```
**04_create_fact_metric.py**

Creates the central fact table:

        fact_metric

**05_create_data_mart.py**

Creates:

        mart_population_metrics

for analytical consumption.


# 🗄️ SQLite Data Warehouse

SQLite is used as the Data Warehouse database.

Database:

    economic_dw.db

Main tables:

economic_dw.db
```text
│
├── dim_date
├── dim_gender
├── dim_age_group
├── dim_metric
├── fact_metric
└── mart_population_metrics
```
SQLite was selected for this project because it provides a lightweight,
portable relational database suitable for demonstrating dimensional
modelling and analytical workflows without requiring a separate
database server.

# 🚀 FastAPI REST API

The Data Mart is exposed through a REST API using FastAPI.

API:

    Population Metrics API

Main endpoints:
```text
GET /
GET /data
GET /data/{year}
GET /years
GET /genders
GET /age-groups
GET /info
GET /scalar
```

# Example API Request
GET /data?year=2023&gender_name=weiblich

Example response:
```text
{
    "count": 10,
    "data": [
        {
            "year": 2023,
            "gender_name": "weiblich",
            "age_group_name": "15 bis unter 20 Jahre",
            "BEV036": 1234
        }
    ]
}
```

# 📖 API Documentation

FastAPI automatically provides OpenAPI documentation.

**Swagger:**

    http://127.0.0.1:8000/docs

**Scalar:**

    http://127.0.0.1:8000/scalar

# 🛠️ Technologies
```text
| Technology       | Purpose                     |
| ---------------- | --------------------------- |
| Python           | ETL and data processing     |
| Pandas           | Data transformation         |
| SQLite           | Data Warehouse              |
| SQL              | Data modelling and analysis |
| FastAPI          | REST API                    |
| JSON             | Data exchange               |
| Power BI         | Data visualisation          |
| Jupyter Notebook | Data exploration            |
| PyCharm          | Development environment     |
| Git              | Version control             |
| GitHub           | Project repository          |
```



```python

```
