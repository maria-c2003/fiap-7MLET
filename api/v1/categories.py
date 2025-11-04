from typing import List, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from util import Util


class CategoryItem(BaseModel):
    categoria: str
    count: int


router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=List[CategoryItem])
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

    items = [CategoryItem(categoria=k, count=v) for k, v in counts.items()]
    items.sort(key=lambda it: (-it.count, it.categoria.lower()))
    return items
