#This code downloads a dataset from the Destatis API and saves it as a CSV file.

import requests
import pandas as pd
import io
import zipfile
import os
from dotenv import load_dotenv, find_dotenv

BASE_URL = 'https://genesis.destatis.de/genesisWS/rest/2020/'

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
TOKEN = os.getenv('TOKEN')

headers = {
'Content-Type': 'application/x-www-form-urlencoded',
'username': TOKEN,
'password': ""
}
langPref = "de"

response = requests.post(BASE_URL + 'data/tablefile',
headers = headers,
data = {
'name': '12211-0001',
'startyear': "2020",
'compress': 'true',
'format': 'ffcsv',
'language': langPref
})
# prüfe, ob die Antwort Text, binär oder leer ist
print(response.text[0:120])
print(response.headers.get("Content-Type"))

if response.status_code == 200:

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:

        # Name der CSV-Datei in der ZIP
        csv_name = z.namelist()[0]

        # CSV direkt speichern
        with open("12211-0001_de_flat.csv", "wb") as f:
            f.write(z.read(csv_name))

    print("CSV-Datei gespeichert.")

else:
    print(f"Fehler: {response.status_code}")
    print(response.text)