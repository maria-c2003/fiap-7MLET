from fastapi import APIRouter, Request
from datetime import datetime


router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/")
def health(request: Request):
    """Retorna status simples da aplicação e número de livros carregados."""
    books = list(getattr(request.app.state, "books", []) or [])
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z",
        "book_count": len(books),
        "scraping_in_progress": len(books) == 0,
    }


