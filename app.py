from fastapi import FastAPI, Request
import threading
import logging
from typing import List, Dict
import re
import requests
import urllib3
from bs4 import BeautifulSoup
import time
import json

from script.scrape import scrape_books

# API routers
from api.v1.books import router as books_router
from api.v1.categories import router as categories_router
from api.v1.health import router as health_router
from api.v1.stats import router as stats_router


class JSONLogFormatter(logging.Formatter):
    """Minimal JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": time.time(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # include any extra structured fields if present
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            payload.update(record.extra)
        return json.dumps(payload, default=str)


class Main:
    """Simple application wrapper that runs the scraper at startup
    and exposes a single endpoint `/` returning all scraped books.
    """

    def __init__(self):
        # configure structured logging
        handler = logging.StreamHandler()
        handler.setFormatter(JSONLogFormatter())
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        # clear existing handlers to avoid duplicate logs in some environments
        if root_logger.handlers:
            root_logger.handlers = []
        root_logger.addHandler(handler)

        self.app = FastAPI()
        # application state for books and runtime metrics
        self.app.state.books = []
        self.app.state.metrics = {
            "total_requests": 0,
            "total_latency_ms": 0.0,
            "per_path": {},
            "errors": 0,
        }

        # include API v1 routers
        self.app.include_router(books_router)
        self.app.include_router(categories_router)
        self.app.include_router(health_router)
        self.app.include_router(stats_router)

        # middleware to log each request and collect simple metrics
        @self.app.middleware("http")
        async def _log_requests(request: Request, call_next):
            start = time.time()
            status_code = None
            try:
                response = await call_next(request)
                status_code = getattr(response, "status_code", None)
            except Exception as exc:
                status_code = 500
                # update metrics for errors
                try:
                    self.app.state.metrics["errors"] += 1
                except Exception:
                    pass
                # log the exception as structured log then re-raise
                logging.getLogger().error(json.dumps({
                    "event": "unhandled_exception",
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(exc),
                }))
                raise
            finally:
                duration_ms = (time.time() - start) * 1000.0
                # update aggregated metrics
                try:
                    m = self.app.state.metrics
                    m["total_requests"] += 1
                    m["total_latency_ms"] += duration_ms
                    per = m["per_path"].setdefault(request.url.path, {"count": 0, "total_latency_ms": 0.0, "status_counts": {}})
                    per["count"] += 1
                    per["total_latency_ms"] += duration_ms
                    sc = str(status_code or "unknown")
                    per["status_counts"][sc] = per["status_counts"].get(sc, 0) + 1
                except Exception:
                    pass

                log_record = {
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query),
                    "client": request.client.host if request.client else None,
                    "status": status_code,
                    "latency_ms": round(duration_ms, 2),
                }
                logging.getLogger().info(json.dumps(log_record))

            return response

        @self.app.on_event("startup")
        def _startup():
            logging.getLogger().info("Aplicação iniciada - iniciando scraping em background")
            t = threading.Thread(target=self._run_scrape, daemon=True)
            t.start()

    def _run_scrape(self) -> None:
        try:
            try:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                r = requests.get("https://books.toscrape.com/catalogue/page-1.html", timeout=10, verify=False)
                r.raise_for_status()
                s = BeautifulSoup(r.text, "html.parser")
                current = s.find("li", class_="current")
                if current:
                    m = re.search(r"of\s+(\d+)", current.text)
                    total_pages = int(m.group(1)) if m else 1
                else:
                    total_pages = 1
            except Exception:
                logging.getLogger().warning("Não foi possível determinar número total de páginas; assumindo 1")
                total_pages = 1

            logging.getLogger().info("Número de páginas detectado: %d", total_pages)

            books = scrape_books(1, total_pages)
            self.app.state.books = books
            logging.getLogger().info("Scraping finalizado no background: %d livros carregados.", len(books))
        except Exception as e:
            logging.getLogger().exception("Erro ao rodar scraper no background: %s", e)

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        import uvicorn

        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    Main().run()


