import pandas as pd
import sqlite3
from pathlib import Path

INPUT_FILE = Path("../data/fact_metric_ready.csv")
DATABASE = Path("../database/economic_dw.db")
conn = sqlite3.connect(DATABASE)

# Beispiel:
df = pd.read_sql("""
SELECT
    d.year,
    g.gender_name,
    a.age_group_name,
    m.metric_name,
    f.metric_value
FROM fact_metric f
JOIN dim_date d
    ON f.date_key = d.date_key
JOIN dim_gender g
    ON f.gender_key = g.gender_key
JOIN dim_age_group a
    ON f.age_group_key = a.age_group_key
JOIN dim_metric m
    ON f.metric_key = m.metric_key
""", conn)

# Pivotieren
pivot_df = df.pivot_table(
    index=[
        "year",
        "gender_name",
        "age_group_name"
    ],
    columns="metric_name",
    values="metric_value",
    aggfunc="sum"
).reset_index()

# Speichern
pivot_df.to_csv(
    "population_metrics_pivot.csv",
    index=False
)

print(pivot_df.head())

#***********************************************************************

# SQLite-Verbindung
conn = sqlite3.connect(DATABASE)

# CSV laden
df = pd.read_csv("population_metrics_pivot.csv")

# Tabelle in SQLite schreiben
df.to_sql(
    "mart_population_metrics",
    conn,
    if_exists="replace",  # replace | append
    index=False
)

# Optional: Index für schnellere Abfragen
conn.execute("""
CREATE INDEX IF NOT EXISTS idx_mart_year
ON mart_population_metrics(year)
""")