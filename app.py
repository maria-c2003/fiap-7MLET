from fastapi import FastAPI
 
from api.v1.books import router as books_router
from api.v1.categories import router as categories_router
from api.v1.health import router as health_router
from api.v1.stats import router as stats_router
from api.v1.scrape import router as scrape_router

class Main:
    """Simple application wrapper that runs the scraper at startup
    and exposes a single endpoint `/` returning all scraped books.
    """

    def __init__(self):

        self.app = FastAPI()
        self.app.state.books = []
        self.app.state.metrics = {
            "total_requests": 0,
            "total_latency_ms": 0.0,
            "per_path": {},
            "errors": 0,
        }

        self.app.include_router(books_router)
        self.app.include_router(categories_router)
        self.app.include_router(health_router)
        self.app.include_router(stats_router)
        self.app.include_router(scrape_router)
        
    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        import uvicorn

        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    Main().run()


app = Main().app
