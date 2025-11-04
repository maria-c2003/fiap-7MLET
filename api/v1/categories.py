from typing import Dict

from fastapi import APIRouter, Request

from util import Util

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("/")
def list_categories():
    """Retorna uma lista de categorias ordenada pela quantidade de livros (desc).

    Cada item é um dicionário com chaves: `categoria`, `count`.
    """
    books = Util.get_books_from_csv()
    counts: Dict[str, int] = {}
    for b in books:
        cat = (b.get("categoria") or "").strip()
        if not cat:
            cat = "(uncategorized)"
        counts[cat] = counts.get(cat, 0) + 1

    items = [{"categoria": k, "count": v} for k, v in counts.items()]
    items.sort(key=lambda it: (-it["count"], it["categoria"].lower()))
    return items
