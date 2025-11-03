from typing import Dict, List, Optional
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/overview")
def overview_stats(request: Request):
    """Estatísticas gerais da coleção: total, preço médio e distribuição de ratings."""
    books = list(getattr(request.app.state, "books", []) or [])
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


@router.get("/categories")
def categories_stats(request: Request):
    """Estatísticas por categoria: quantidade de livros, preços (avg/min/max) e média de ratings."""
    books = list(getattr(request.app.state, "books", []) or [])
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



@router.get("/runtime")
def runtime_stats(request: Request):
    """Métricas de runtime simples: contadores de requisições e latências.

    Retorna métricas coletadas pela middleware de logging.
    """
    metrics = getattr(request.app.state, "metrics", None) or {}
    total = metrics.get("total_requests", 0)
    total_latency = metrics.get("total_latency_ms", 0.0)
    average_latency_ms = round(total_latency / total, 2) if total else None
    return {
        "total_requests": total,
        "total_latency_ms": round(total_latency, 2),
        "average_latency_ms": average_latency_ms,
        "per_path": metrics.get("per_path", {}),
        "errors": metrics.get("errors", 0),
    }