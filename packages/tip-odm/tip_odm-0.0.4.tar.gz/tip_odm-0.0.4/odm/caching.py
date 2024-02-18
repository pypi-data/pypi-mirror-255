import dataclasses
import datetime
import os.path
import threading
import time
from functools import wraps
from typing import Callable
import schedule
import polars as pl
from .logger import log_info, log_exception, log_error
from .utils import timer

type JobType = schedule.Job | list[schedule.Job] | str | list[str]
type DataFrame = pl.DataFrame | pl.LazyFrame


@dataclasses.dataclass
class CacheItem:
    cache_key: str
    name: str
    recreate: bool
    lazy: bool
    func: Callable[[], DataFrame]
    data: DataFrame | None = None

    is_creating: bool = False
    is_invalidated: bool = False
    last_refresh: datetime.datetime | None = None

    def create(self):
        if self.is_creating:
            log_info(f"Cache [{self.cache_key}] wird bereits erstellt")
            return

        self.is_creating = True

        try:
            log_info(f"Cache [{self.cache_key}] wird neu erstellt")
            text = f"Cache [{self.cache_key}] wurde neu erstellt"
            data: DataFrame = timer(text, self.func)

            if not os.path.exists("cache") or not os.path.isdir("cache"):
                os.makedirs("cache")

            if isinstance(data, pl.LazyFrame):
                # TODO wird aktuell noch nicht unterstützt. Daher über DataFrame lösen
                # data.sink_parquet(self.__get_file_path())

                data.collect().write_parquet(self.__get_file_path())
            else:
                data.write_parquet(self.__get_file_path())

            if self.lazy:
                data = pl.scan_parquet(self.__get_file_path())

            self.data = data
            self.is_invalidated = False
            self.last_refresh = datetime.datetime.now()

            return data
        finally:
            self.is_creating = False

    def get_or_create(self):
        data = self.data

        if data is None:
            data = self.create()

        return data

    def invalidate(self, is_startup: bool = False):
        if self.is_invalidated:
            log_info(f"Cache [{self.cache_key}] ist bereits invalidiert")
            return

        self.is_invalidated = True

        if is_startup and self.__cache_exists():
            self.__load_cache()
            log_info(f"Cache [{self.cache_key}] aus Dateisystem eingelesen")
            self.last_refresh = datetime.datetime.fromtimestamp(os.path.getmtime(self.__get_file_path()))
            self.is_invalidated = False
            return

        if self.recreate:
            recreate_list.append(self)
            log_info(f"Cache [{self.cache_key}] zur Neuerstellung vorgemerkt")
        else:
            log_info(f"Cache [{self.cache_key}] invalidiert")
            self.data = None

    def get_file_size_mb(self):
        if not self.__cache_exists():
            return None

        return round(os.path.getsize(self.__get_file_path()) / 1024 / 1024, 2)

    def __get_file_path(self):
        return f"cache/{self.cache_key}.parquet"

    def __cache_exists(self):
        return os.path.exists(self.__get_file_path()) and os.path.isfile(self.__get_file_path())

    def __load_cache(self):
        if self.lazy:
            self.data = pl.scan_parquet(self.__get_file_path())
        else:
            self.data = pl.read_parquet(self.__get_file_path())


cache: dict[str, CacheItem] = {}
recreate_list: list[CacheItem] = []


def data_cache(cache_key: str, name: str, jobs: JobType = None, recreate: bool = True, lazy: bool = True):
    """
    Liefert die Daten aus dem Cache oder erstellt diesen neu
    :param cache_key: Key des Caches
    :param name: Name des Caches
    :param jobs: Uhrzeit, Jobs, Liste von Uhrzeit oder Liste von Jobs
    :param recreate: Angabe, ob nach Invalidieren des Cache der Cache direkt neu befüllt werden soll.
    :param lazy: Angabe, ob das Ergebnis als DataFrame oder LazyDataFrame zurückgegeben werden soll.
    Funktioniert nur mit Methoden ohne Parameter!
    :return: Ergebnis der dekorierten Methode
    """
    if jobs is None:
        jobs = ["02:00"]
    if isinstance(jobs, str):
        jobs = [jobs]
    if isinstance(jobs, schedule.Job):
        jobs = [jobs]
    if isinstance(jobs, list):
        jobs = [job if isinstance(job, schedule.Job) else schedule.every().day.at(job) for job in jobs]

    def decorator(func):
        cache_item = CacheItem(cache_key=cache_key, name=name, recreate=recreate, func=func, lazy=lazy, data=None)
        cache[cache_key] = cache_item

        @wraps(func)
        def wrapper():
            return cache_item.get_or_create()

        cache_item.invalidate(True)

        for job in jobs:
            job.do(cache_item.invalidate)

        return wrapper

    return decorator


def get_cached_items():
    """
    Liefert alle Cache
    :return: Cache
    """

    return cache.values()


def get_cached_data(cache_key: str):
    """
    Liefert die Daten aus dem Cache oder erstellt diesen neu
    :param cache_key: Key des Caches
    :return: Ergebnis der dekorierten Methode
    """

    cache_item = cache.get(cache_key, None)
    if cache_item is None:
        log_error(f"Cache [{cache_key}] nicht gefunden")
        return None

    return cache_item.get_or_create()


def invalidate_cached_data(cache_key: str):
    """
    Invalidiert den Cache
    :param cache_key: Key des Caches
    :return: None
    """

    cache_item = cache.get(cache_key, None)
    if cache_item is None:
        log_error(f"Cache [{cache_key}] nicht gefunden")
        return

    cache_item.invalidate()


def run_scheduler():
    stop_event = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not stop_event.is_set():
                schedule.run_pending()
                cls.recreate()
                time.sleep(5)

        @classmethod
        def recreate(cls):
            while len(recreate_list) > 0:
                cache_item = recreate_list.pop()

                try:
                    if cache_item.is_invalidated:
                        cache_item.create()
                except Exception:
                    log_exception(f"Cache [{cache_item.cache_key}] konnte nicht neu erstellt werden")

    schedule_thread = ScheduleThread()
    schedule_thread.start()

    return stop_event
