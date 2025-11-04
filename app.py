from fastapi import FastAPI
 
from api.v1.books import router as books_router
from api.v1.categories import router as categories_router
from api.v1.health import router as health_router
from api.v1.stats import router as stats_router
from api.v1.scrape import router as scrape_router

class Main:
    """
    Este projeto contém um pequeno serviço em FastAPI que executa um scraping do site "Books to Scrape" em background e expõe endpoints para consultar os livros coletados, categorias e métricas simples.
    """

    def __init__(self):

        self.app = FastAPI(
            title="Books Scraper API",
            description=(
                "Este projeto contém um pequeno serviço em FastAPI que executa um scraping do site Books to Scrape em background e expõe endpoints para consultar os livros coletados, categorias e métricas simples."
            ),
            version="0.1.0",
        )

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
