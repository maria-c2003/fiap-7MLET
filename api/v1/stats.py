from typing import Dict, List
from fastapi import APIRouter, Request

from util import Util

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/overview", response_model=Dict[str, object])
def overview_stats():
    """Estatísticas gerais da coleção: total, preço médio e distribuição de ratings."""
    books = Util.get_books_from_csv()
    total_books = len(books)
    prices = [b.get("preco") for b in books if isinstance(b.get("preco"), (int, float))]
    average_price = round(sum(prices) / len(prices), 2) if prices else None
    ratings_distribution: Dict[int, int] = {}
    for b in books:
        r = b.get("rating")
        if isinstance(r, int):
            ratings_distribution[r] = ratings_distribution.get(r, 0) + 1
    return {
        "total_books": total_books,
        "average_price": average_price,
        "ratings_distribution": ratings_distribution,
    }


@router.get("/categories", response_model=List[Dict[str, object]])
def categories_stats():
    """Estatísticas por categoria: quantidade de livros, preços (avg/min/max) e média de ratings."""
    books = Util.get_books_from_csv()
    categories: Dict[str, Dict[str, object]] = {}
    for b in books:
        cat = (b.get("categoria") or "Uncategorized")
        if cat not in categories:
            categories[cat] = {"count": 0, "prices": [], "ratings": []}
        categories[cat]["count"] += 1
        p = b.get("preco")
        if isinstance(p, (int, float)):
            categories[cat]["prices"].append(p)
        r = b.get("rating")
        if isinstance(r, int):
            categories[cat]["ratings"].append(r)
    result: List[Dict[str, object]] = []
    for cat, data in categories.items():
        prices = data["prices"]
        ratings = data.get("ratings", [])
        avg_price = round(sum(prices) / len(prices), 2) if prices else None
        min_p = min(prices) if prices else None
        max_p = max(prices) if prices else None
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
        result.append(
            {
                "categoria": cat,
                "count": data["count"],
                "average_price": avg_price,
                "min_price": min_p,
                "max_price": max_p,
                "average_rating": avg_rating,
            }
        )
    return result
