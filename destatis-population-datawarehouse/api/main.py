from fastapi import FastAPI, HTTPException, Query, APIRouter
from contextlib import contextmanager
import sqlite3
from typing import Optional
from scalar_fastapi import get_scalar_api_reference


# ==================================================
# 1. Datenbank-Konfiguration
# ==================================================

class DatabaseConfig:
    """Kapselt die Datenbankverbindung und den Tabellennamen."""

    def __init__(self, database: str, table: str):
        self.database = database
        self.table = table

    @contextmanager
    def get_connection(self):
        """
        Kontextmanager für sichere Datenbankverbindungen.
        Stellt sicher, dass die Verbindung IMMER geschlossen wird –
        auch bei Exceptions im with-Block.
        """
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row  # Ermöglicht Zugriff per Spaltenname
        try:
            yield conn
        finally:
            conn.close()


# ==================================================
# 2. Repository-Schicht (reiner Datenzugriff)
# ==================================================

class PopulationRepository:
    """
    Kapselt alle SQL-Abfragen für die Tabelle mart_population_metrics.
    Keine Business-Logik, keine HTTP-Fehler – nur Daten.
    """

    def __init__(self, db_config: DatabaseConfig):
        self.db = db_config
        self.table = db_config.table

    def fetch_data(
        self,
        year: Optional[int] = None,
        gender_name: Optional[str] = None,
        age_group_name: Optional[str] = None,
        limit: int = 100,
    ) -> list[sqlite3.Row]:
        """Holt gefilterte Daten mit optionalen WHERE-Bedingungen."""

        query = f"SELECT * FROM {self.table} WHERE 1=1"
        params: list[int | str] = []

        if year is not None:
            query += " AND year = ?"
            params.append(year)

        if gender_name is not None:
            query += " AND gender_name = ?"
            params.append(gender_name)

        if age_group_name is not None:
            query += " AND age_group_name = ?"
            params.append(age_group_name)

        query += " ORDER BY year LIMIT ?"
        params.append(limit)

        with self.db.get_connection() as conn:
            return conn.execute(query, params).fetchall()

    def fetch_by_year(self, year: int) -> list[sqlite3.Row]:
        """Holt alle Daten für ein bestimmtes Jahr."""
        query = f"""
            SELECT * FROM {self.table}
            WHERE year = ?
            ORDER BY gender_name, age_group_name
        """
        with self.db.get_connection() as conn:
            return conn.execute(query, (year,)).fetchall()

    def fetch_distinct_years(self) -> list[int]:
        """Gibt alle verfügbaren Jahre zurück."""
        query = f"SELECT DISTINCT year FROM {self.table} ORDER BY year"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [row["year"] for row in rows]

    def fetch_distinct_genders(self) -> list[str]:
        """Gibt alle verfügbaren Geschlechter zurück."""
        query = f"SELECT DISTINCT gender_name FROM {self.table} ORDER BY gender_name"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [row["gender_name"] for row in rows]

    def fetch_distinct_age_groups(self) -> list[str]:
        """Gibt alle verfügbaren Altersgruppen zurück."""
        query = f"SELECT DISTINCT age_group_name FROM {self.table} ORDER BY age_group_name"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [row["age_group_name"] for row in rows]

    def fetch_table_info(self) -> dict:
        """Gibt Spaltennamen und eine Beispielzeile zurück."""
        query = f"SELECT * FROM {self.table} LIMIT 1"
        with self.db.get_connection() as conn:
            row = conn.execute(query).fetchone()

        if row is None:
            return {"table": self.table, "columns": [], "rows": 0}

        return {"table": self.table, "columns": list(row.keys())}


# ==================================================
# 3. Service-Schicht (Business-Logik)
# ==================================================

class PopulationService:
    """
    Enthält die Geschäftslogik und wandelt DB-Zeilen in API-taugliche
    Dictionaries um. Hier werden auch HTTP-Fehler geworfen.
    """

    def __init__(self, repository: PopulationRepository):
        self.repo = repository

    def get_filtered_data(
        self,
        year: Optional[int],
        gender_name: Optional[str],
        age_group_name: Optional[str],
        limit: int,
    ) -> dict:
        rows = self.repo.fetch_data(year, gender_name, age_group_name, limit)
        return {
            "count": len(rows),
            "data": [dict(row) for row in rows],
        }

    def get_data_by_year(self, year: int) -> dict:
        rows = self.repo.fetch_by_year(year)
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Keine Daten für das Jahr {year}",
            )
        return {
            "year": year,
            "count": len(rows),
            "data": [dict(row) for row in rows],
        }

    def get_years(self) -> dict:
        return {"years": self.repo.fetch_distinct_years()}

    def get_genders(self) -> dict:
        return {"genders": self.repo.fetch_distinct_genders()}

    def get_age_groups(self) -> dict:
        return {"age_groups": self.repo.fetch_distinct_age_groups()}

    def get_info(self) -> dict:
        return self.repo.fetch_table_info()


# ==================================================
# 4. API-Router (HTTP-Endpunkte)
# ==================================================

class PopulationAPI:
    """
    Kapselt alle HTTP-Endpunkte und delegiert an den Service.
    """

    def __init__(self, service: PopulationService):
        self.service = service
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        """Registriert alle Routen auf dem Router."""

        @self.router.get("/")
        def root():
            return {
                "message": "Population Metrics API",
                "table": self.service.repo.table,
            }

        @self.router.get("/data")
        def get_data(
            year: Optional[int] = None,
            gender_name: Optional[str] = None,
            age_group_name: Optional[str] = None,
            limit: int = Query(100, ge=1, le=10000),
        ):
            return self.service.get_filtered_data(
                year, gender_name, age_group_name, limit
            )

        @self.router.get("/data/{year}")
        def get_data_by_year(year: int):
            return self.service.get_data_by_year(year)

        @self.router.get("/years")
        def get_years():
            return self.service.get_years()

        @self.router.get("/genders")
        def get_genders():
            return self.service.get_genders()

        @self.router.get("/age-groups")
        def get_age_groups():
            return self.service.get_age_groups()

        @self.router.get("/info")
        def get_info():
            return self.service.get_info()


# ==================================================
# 5. App-Factory (Zusammenbau & Start)
# ==================================================

def create_app() -> FastAPI:
    """
    Factory-Funktion, die alle Schichten zusammensetzt.
    Vorteil: Testbar, konfigurierbar, keine globalen Variablen.
    """
    # Konfiguration
    db_config = DatabaseConfig(
        database="economic_dw.db",
        table="mart_population_metrics",
    )

    # Schichten aufbauen (Dependency Injection)
    repository = PopulationRepository(db_config)
    service = PopulationService(repository)
    api = PopulationAPI(service)

    # FastAPI-App erstellen
    app = FastAPI(
        title="Population Metrics API",
        description="REST API für mart_population_metrics",
        version="1.0.0",
    )

    # Router einbinden
    app.include_router(api.router)

    # Scalar-Docs (nicht im OpenAPI-Schema)
    @app.get("/scalar", include_in_schema=False)
    def get_scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title="Scalar API",
        )

    return app


# ==================================================
# 6. Einstiegspunkt
# ==================================================

app = create_app()