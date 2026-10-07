import pandas as pd
import sqlite3
from pathlib import Path


# ============================================================
# 1. Pfade
# ============================================================

INPUT_FILE = ("fact_metric_ready.csv")
DATABASE = ("economic_dw.db")


# ============================================================
# 2. fact_metric_ready.csv laden
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    sep=";",
    encoding="utf-8-sig"
)

print("Daten geladen:")
print(df.head())

print("\nSpalten:")
print(df.columns.tolist())


# ============================================================
# 3. Datenbank öffnen
# ============================================================

conn = sqlite3.connect(DATABASE)


# ============================================================
# 4. DIM_DATE
# ============================================================

dim_date = (
    df[["year"]]
    .drop_duplicates()
    .sort_values("year")
    .reset_index(drop=True)
)

# Surrogate Key
dim_date.insert(
    0,
    "date_key",
    range(1, len(dim_date) + 1)
)

print("\n========================================")
print("DIM_DATE")
print("========================================")

print(dim_date)


# ============================================================
# 5. DIM_GENDER
# ============================================================

dim_gender = (
    df[["gender"]]
    .drop_duplicates()
    .sort_values("gender")
    .reset_index(drop=True)
)

dim_gender.insert(
    0,
    "gender_key",
    range(1, len(dim_gender) + 1)
)

# gender → gender_name
dim_gender = dim_gender.rename(
    columns={
        "gender": "gender_name"
    }
)

# Optionaler technischer Code
dim_gender.insert(
    1,
    "gender_code",
    [
        f"G{i:03d}"
        for i in range(1, len(dim_gender) + 1)
    ]
)

print("\n========================================")
print("DIM_GENDER")
print("========================================")

print(dim_gender)


# ============================================================
# 6. DIM_AGE_GROUP
# ============================================================

dim_age_group = (
    df[["age_group"]]
    .drop_duplicates()
    .sort_values("age_group")
    .reset_index(drop=True)
)

dim_age_group.insert(
    0,
    "age_group_key",
    range(1, len(dim_age_group) + 1)
)

dim_age_group = dim_age_group.rename(
    columns={
        "age_group": "age_group_name"
    }
)

# Optionaler technischer Code
dim_age_group.insert(
    1,
    "age_group_code",
    [
        f"AGE{i:03d}"
        for i in range(1, len(dim_age_group) + 1)
    ]
)

print("\n========================================")
print("DIM_AGE_GROUP")
print("========================================")

print(dim_age_group)


# ============================================================
# 7. DIM_METRIC
# ============================================================

dim_metric = (
    df[
        [
            "metric_code",
            "metric_name"
        ]
    ]
    .drop_duplicates()
    .sort_values("metric_code")
    .reset_index(drop=True)
)

dim_metric.insert(
    0,
    "metric_key",
    range(1, len(dim_metric) + 1)
)

print("\n========================================")
print("DIM_METRIC")
print("========================================")

print(dim_metric)


# ============================================================
# 8. Dimensionen in SQLite speichern
# ============================================================

dim_date.to_sql(
    "dim_date",
    conn,
    if_exists="replace",
    index=False
)

dim_gender.to_sql(
    "dim_gender",
    conn,
    if_exists="replace",
    index=False
)

dim_age_group.to_sql(
    "dim_age_group",
    conn,
    if_exists="replace",
    index=False
)

dim_metric.to_sql(
    "dim_metric",
    conn,
    if_exists="replace",
    index=False
)


# ============================================================
# 9. Kontrolle
# ============================================================

print("\n========================================")
print("DATABASE CHECK")
print("========================================")

tables = [
    "dim_date",
    "dim_gender",
    "dim_age_group",
    "dim_metric"
]

for table in tables:

    result = pd.read_sql(
        f"SELECT * FROM {table}",
        conn
    )

    print(f"\n{table}:")
    print(result)


# ============================================================
# 10. Verbindung schließen
# ============================================================

conn.close()

print("\n========================================")
print("FERTIG")
print("========================================")

print(
    f"Dimensionstabellen wurden in\n"
    f"{DATABASE}\ngespeichert."
)