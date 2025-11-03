from typing import Dict

from fastapi import APIRouter, Request


router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("/")
def list_categories(request: Request):
    """Retorna uma lista de categorias ordenada pela quantidade de livros (desc).

    Cada item é um dicionário com chaves: `categoria`, `count`.
    """
    books = list(getattr(request.app.state, "books", []) or [])
    counts: Dict[str, int] = {}
    for b in books:
        cat = (b.get("categoria") or "").strip()
        if not cat:
            cat = "(uncategorized)"
        counts[cat] = counts.get(cat, 0) + 1

    items = [{"categoria": k, "count": v} for k, v in counts.items()]
    items.sort(key=lambda it: (-it["count"], it["categoria"].lower()))
    return items
