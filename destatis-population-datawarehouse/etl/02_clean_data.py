import pandas as pd
from pathlib import Path
import re


# ============================================================
# 1. Dateien
# ============================================================

INPUT_FILE = ("12211-0001_de_flat.csv")
#OUTPUT_FILE = Path("../data/12211-0001_de_flat_clean.csv")
OUTPUT_FILE = Path.cwd()/"12211-0001_de_flat_clean.csv"


# ============================================================
# 2. CSV laden
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

print("========================================")
print("ORIGINAL DATA")
print("========================================")

print(f"Zeilen : {len(df)}")
print(f"Spalten: {len(df.columns)}")

print("\nOriginale Spaltennamen:")
print(df.columns.tolist())


# ============================================================
# 3. Spaltennamen bereinigen
# ============================================================

def clean_column_name(column_name):

    column_name = column_name.strip().lower()

    # Leerzeichen → _
    column_name = re.sub(r"\s+", "_", column_name)

    # Sonderzeichen → _
    column_name = re.sub(r"[^a-zA-Z0-9_]", "_", column_name)

    # Mehrere ___ → _
    column_name = re.sub(r"_+", "_", column_name)

    # _ am Anfang / Ende entfernen
    column_name = column_name.strip("_")

    return column_name


df.columns = [
    clean_column_name(col)
    for col in df.columns
]


# ============================================================
# 4. Doppelte Spaltennamen erkennen
# ============================================================

if df.columns.duplicated().any():

    print("\nWARNUNG: Doppelte Spaltennamen gefunden!")

    duplicates = df.columns[df.columns.duplicated()].tolist()

    print(duplicates)

    # Eindeutige Namen erzeugen
    new_columns = []
    counter = {}

    for col in df.columns:

        if col not in counter:
            counter[col] = 0
            new_columns.append(col)

        else:
            counter[col] += 1
            new_columns.append(
                f"{col}_{counter[col]}"
            )

    df.columns = new_columns


# ============================================================
# 5. Textwerte bereinigen
# ============================================================

for column in df.select_dtypes(include="object").columns:

    df[column] = (
        df[column]
        .str.strip()
        .replace("", pd.NA)
    )


# ============================================================
# 6. Fehlende Werte vereinheitlichen
# ============================================================

df = df.replace(
    {
        "": pd.NA,
        " ": pd.NA,
        "nan": pd.NA,
        "NaN": pd.NA,
        "NA": pd.NA,
        "N/A": pd.NA
    }
)


# ============================================================
# 7. Destatis Geheimhaltung "x"
# ============================================================

# "x" bedeutet bei Destatis nicht automatisch 0.
# Deshalb wird x als fehlender/geheimer Wert behandelt.

for column in df.columns:

    df[column] = df[column].replace(
        r"^\s*x\s*$",
        pd.NA,
        regex=True
    )


# ============================================================
# 8. Duplikate entfernen
# ============================================================

duplicate_count = df.duplicated().sum()

print(f"\nGefundene Duplikate: {duplicate_count}")

df = df.drop_duplicates()


# ============================================================
# 9. Numerische Werte konvertieren
# ============================================================

# Typische numerische Spalten erkennen

for column in df.columns:

    # Versuch einer numerischen Konvertierung
    numeric_values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    # Anteil der erfolgreich konvertierten Werte
    valid_values = df[column].notna().sum()

    if valid_values > 0:

        ratio = (
            numeric_values.notna().sum()
            / valid_values
        )

        # Wenn mindestens 80 % numerisch sind
        if ratio >= 0.8:

            df[column] = numeric_values


# ============================================================
# 10. Ergebnis kontrollieren
# ============================================================

print("\n========================================")
print("CLEAN DATA")
print("========================================")

print(f"Zeilen : {len(df)}")
print(f"Spalten: {len(df.columns)}")

print("\nBereinigte Spaltennamen:")

for column in df.columns:
    print(f" - {column}")


print("\nDatentypen:")
print(df.dtypes)


print("\nFehlende Werte:")
print(df.isna().sum())


# ============================================================
# 11. Bereinigte CSV speichern
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    sep=";",
    encoding="utf-8-sig",
    index=False
)

print("\n========================================")
print("FERTIG")
print("========================================")

print(
    f"Bereinigte Datei gespeichert:\n"
    f"{OUTPUT_FILE}"
)