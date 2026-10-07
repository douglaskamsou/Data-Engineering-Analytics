
import pandas as pd
import sqlite3
from pathlib import Path


# ============================================================
# 1. Dateien / Datenbank
# ============================================================

INPUT_FILE = ("fact_metric_ready.csv")
DATABASE = "economic_dw.db"


# ============================================================
# 2. Daten laden
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    sep=";",
    encoding="utf-8-sig"
)

print("Eingabedaten:")
print(df.head())

print("\nSpalten:")
print(df.columns.tolist())


# ============================================================
# 3. Datenbank öffnen
# ============================================================

conn = sqlite3.connect(DATABASE)

# ============================================================
# 4. Dimensionstabellen aus SQLite laden
# ============================================================

dim_date = pd.read_sql(
    """
    SELECT
        date_key,
        year
    FROM dim_date
    """,
    conn
)

dim_gender = pd.read_sql(
    """
    SELECT
        gender_key,
        gender_name
    FROM dim_gender
    """,
    conn
)

dim_age_group = pd.read_sql(
    """
    SELECT
        age_group_key,
        age_group_name
    FROM dim_age_group
    """,
    conn
)

dim_metric = pd.read_sql(
    """
    SELECT
        metric_key,
        metric_code,
        metric_name
    FROM dim_metric
    """,
    conn
)


# ============================================================
# 5. Dimension Keys hinzufügen
# ============================================================

# ------------------------------------------------------------
# Date Dimension
# ------------------------------------------------------------

df = df.merge(
    dim_date,
    on="year",
    how="left"
)


# ------------------------------------------------------------
# Gender Dimension
# ------------------------------------------------------------

df = df.merge(
    dim_gender,
    left_on="gender",
    right_on="gender_name",
    how="left"
)


# ------------------------------------------------------------
# Age Group Dimension
# ------------------------------------------------------------

df = df.merge(
    dim_age_group,
    left_on="age_group",
    right_on="age_group_name",
    how="left"
)


# ------------------------------------------------------------
# Metric Dimension
# ------------------------------------------------------------

df = df.merge(
    dim_metric,
    on=["metric_code", "metric_name"],
    how="left"
)


# ============================================================
# 6. Prüfen, ob alle Dimension Keys gefunden wurden
# ============================================================

print("\nNicht zugeordnete Date Keys:")
print(df["date_key"].isna().sum())

print("\nNicht zugeordnete Gender Keys:")
print(df["gender_key"].isna().sum())

print("\nNicht zugeordnete Age Group Keys:")
print(df["age_group_key"].isna().sum())

print("\nNicht zugeordnete Metric Keys:")
print(df["metric_key"].isna().sum())


# ============================================================
# 7. Fact-Tabelle erzeugen
# ============================================================

fact_metric = df[
    [
        "date_key",
        "gender_key",
        "age_group_key",
        "metric_key",
        "metric_value"
    ]
].copy()


# ============================================================
# 8. Metric Value in numerischen Typ umwandeln
# ============================================================

fact_metric["metric_value"] = pd.to_numeric(
    fact_metric["metric_value"],
    errors="coerce"
)


# ============================================================
# 9. Ungültige Datensätze entfernen
# ============================================================

fact_metric = fact_metric.dropna(
    subset=[
        "date_key",
        "gender_key",
        "age_group_key",
        "metric_key"
    ]
)


# ============================================================
# 10. Integer Keys
# ============================================================

fact_metric["date_key"] = fact_metric["date_key"].astype(int)
fact_metric["gender_key"] = fact_metric["gender_key"].astype(int)
fact_metric["age_group_key"] = fact_metric["age_group_key"].astype(int)
fact_metric["metric_key"] = fact_metric["metric_key"].astype(int)


# ============================================================
# 11. Surrogate Key erzeugen
# ============================================================

fact_metric.insert(
    0,
    "metric_fact_key",
    range(1, len(fact_metric) + 1)
)


# ============================================================
# 12. Duplikate prüfen
# ============================================================

duplicates = fact_metric.duplicated(
    subset=[
        "date_key",
        "gender_key",
        "age_group_key",
        "metric_key"
    ]
).sum()

print(f"\nDoppelte Fact Records: {duplicates}")


# ============================================================
# 13. Fact-Tabelle anzeigen
# ============================================================

print("\n========================================")
print("FACT_METRIC")
print("========================================")

print(fact_metric.head(20))

print("\nAnzahl Datensätze:")
print(len(fact_metric))


# ============================================================
# 14. In SQLite speichern
# ============================================================

fact_metric.to_sql(
    "fact_metric",
    conn,
    if_exists="replace",
    index=False
)


# ============================================================
# 15. Datenbank prüfen
# ============================================================

result = pd.read_sql(
    """
    SELECT *
    FROM fact_metric
    LIMIT 10
    """,
    conn
)

print("\nGespeicherte Fact-Tabelle:")
print(result)


# ============================================================
# 16. Verbindung schließen
# ============================================================

conn.close()

print("\n========================================")
print("FERTIG")
print("========================================")

print(
    "fact_metric wurde erfolgreich in "
    f"{DATABASE} gespeichert."
)