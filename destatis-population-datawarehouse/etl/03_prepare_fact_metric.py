"""
The original Destatis file is not structured optimally for direct use in the star schema.
It contains many technical columns and Destatis-specific labels.
The purpose of the script is to transform the cleaned Destatis raw data into a standardized
intermediate structure suitable for the data warehouse.
the out file is fact_metric_ready.csv
"""

import pandas as pd
from pathlib import Path


# ============================================================
# 1. Dateien
# ============================================================

INPUT_FILE = Path("../data/12211-0001_de_flat_clean.csv")
#OUTPUT_FILE = Path("../data/fact_metric_ready.csv")
OUTPUT_FILE = Path.cwd()/"fact_metric_ready.csv"


# ============================================================
# 2. Clean-Datei laden
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

print("Originale Daten:")
print(df.head())

print("\nSpalten der Clean-Datei:")
print(df.columns.tolist())


# ============================================================
# 3. Benötigte Spalten prüfen
# ============================================================

required_columns = [
    "time",
    "2_variable_attribute_label",
    "3_variable_attribute_label",
    "value_variable_code",
    "value_variable_label",
    "value"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "Folgende benötigte Spalten fehlen:\n"
        + "\n".join(missing_columns)
    )


# ============================================================
# 4. Neue Fact-Metric-Vorbereitung erstellen
# ============================================================

fact_metric_ready = pd.DataFrame({

    "year": df["time"],

    "gender": (
        df["2_variable_attribute_label"]
        .str.strip()
    ),

    "age_group": (
        df["3_variable_attribute_label"]
        .str.strip()
    ),

    "metric_code": (
        df["value_variable_code"]
        .str.strip()
    ),

    "metric_name": (
        df["value_variable_label"]
        .str.strip()
    ),

    "metric_value": df["value"]
})


# ============================================================
# 5. Year in Integer umwandeln
# ============================================================

fact_metric_ready["year"] = pd.to_numeric(
    fact_metric_ready["year"],
    errors="coerce"
)


# ============================================================
# 6. Metric Value in numerischen Wert umwandeln
# ============================================================

# Deutsche Dezimaldarstellung berücksichtigen
fact_metric_ready["metric_value"] = (
    fact_metric_ready["metric_value"]
    .str.replace(",", ".", regex=False)
)

fact_metric_ready["metric_value"] = pd.to_numeric(
    fact_metric_ready["metric_value"],
    errors="coerce"
)


# ============================================================
# 7. Fehlende Dimensionen behandeln
# ============================================================

fact_metric_ready["gender"] = (
    fact_metric_ready["gender"]
    .fillna("Insgesamt")
)

fact_metric_ready["age_group"] = (
    fact_metric_ready["age_group"]
    .fillna("Insgesamt")
)


# ============================================================
# 8. Zeilen ohne notwendige Informationen entfernen
# ============================================================

fact_metric_ready = fact_metric_ready.dropna(
    subset=[
        "year",
        "metric_code",
        "metric_name"
    ]
)


# ============================================================
# 9. Year als Integer
# ============================================================

fact_metric_ready["year"] = (
    fact_metric_ready["year"]
    .astype(int)
)


# ============================================================
# 10. Sortieren
# ============================================================

fact_metric_ready = fact_metric_ready.sort_values(
    by=[
        "year",
        "gender",
        "age_group",
        "metric_code"
    ]
).reset_index(drop=True)


# ============================================================
# 11. Ergebnis prüfen
# ============================================================

print("\n========================================")
print("FACT METRIC READY")
print("========================================")

print(
    f"Anzahl Zeilen: "
    f"{len(fact_metric_ready)}"
)

print(
    f"Anzahl Spalten: "
    f"{len(fact_metric_ready.columns)}"
)

print("\nSpalten:")

for column in fact_metric_ready.columns:
    print(f" - {column}")


print("\nDatentypen:")
print(fact_metric_ready.dtypes)


print("\nJahre:")
print(
    sorted(
        fact_metric_ready["year"]
        .unique()
    )
)


print("\nGeschlechter:")
print(
    fact_metric_ready["gender"]
    .unique()
)


print("\nAltersgruppen:")
print(
    fact_metric_ready["age_group"]
    .unique()
)


print("\nMetrics:")

print(
    fact_metric_ready[
        [
            "metric_code",
            "metric_name"
        ]
    ]
    .drop_duplicates()
    .sort_values("metric_code")
    .to_string(index=False)
)


print("\nErste 10 Datensätze:")

print(
    fact_metric_ready.head(10)
    .to_string(index=False)
)


# ============================================================
# 12. Als neue CSV speichern
# ============================================================

fact_metric_ready.to_csv(
    OUTPUT_FILE,
    sep=";",
    encoding="utf-8-sig",
    index=False
)


print("\n========================================")
print("FERTIG")
print("========================================")

print(
    f"Datei gespeichert unter:\n"
    f"{OUTPUT_FILE}"
)