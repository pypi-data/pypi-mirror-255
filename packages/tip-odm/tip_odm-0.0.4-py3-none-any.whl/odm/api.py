from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, HTTPException
import os
import uvicorn
from .caching import get_cached_items, run_scheduler
from .models_caching import Cache
from .models_definition import DefinitionCompact, Definition
from .query import LoadOptions
from .logger import init_logger
from .settings import get_settings
from . import query

app = FastAPI()


@app.get("/api/query", response_model_exclude_none=True)
def get_queries() -> list[DefinitionCompact]:
    return query.get_queries()


@app.get("/api/query/{key}", response_model_exclude_none=True)
def get_queries(key: str) -> Definition:
    definition = query.get_query(key)
    if definition is None:
        raise HTTPException(status_code=404, detail="Query nicht vorhanden")

    return definition


@app.post("/api/data", response_model=list[list])
def get_query_result(options: LoadOptions):
    r = query.get_query_result(options)
    return Response(content=r, media_type="application/json")


@app.get("/api/cache")
def get_cache_info() -> list[Cache]:
    cached_items = get_cached_items()

    return [Cache(
        key=i.cache_key,
        name=i.name,
        last_refresh=i.last_refresh,
        lazy=i.lazy,
        size_mb=i.get_file_size_mb(),
        is_invalidated=i.is_invalidated
    ) for i in cached_items]


@app.post("/api/cache/{key}/invalidate")
def invalid_cache(key: str):
    cached_items = get_cached_items()
    cached_item = next((i for i in cached_items if i.cache_key == key), None)

    if cached_item is None:
        raise HTTPException(status_code=404, detail="Cache nicht vorhanden")

    cached_item.invalidate()
    return Response(status_code=200)


def init():
    """
    Initialisiert die Umgebung
    :return: FastAPI
    """

    init_logger()
    load_dotenv()

    return app


def start():
    """
    Startet den Webserver
    :param api_key: Api-Key für das Abfragen der Definitionen und der Daten
    :return: None
    """

    api_key = os.getenv("API_KEY") or "TEST"

    @app.middleware("http")
    async def check_api_key(request: Request, call_next):
        if request.headers.get("X-Api-Key", "") != api_key:
            return Response(status_code=401, content="API Key ungültig")

        return await call_next(request)

    run_scheduler()

    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port, log_config={
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {}
    })
