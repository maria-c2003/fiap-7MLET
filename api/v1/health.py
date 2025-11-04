from fastapi import APIRouter, Request
from datetime import datetime

from util import Util

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/")
def health():
    """Retorna status simples da aplicação e número de livros carregados."""
    books = Util.get_books_from_csv()
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z",
        "book_count": len(books),
        "scraping_in_progress": len(books) == 0,
    }


