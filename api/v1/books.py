from typing import List, Optional

from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel


class Book(BaseModel):
    id: int
    titulo: str
    preco: Optional[float]
    rating: Optional[int]
    disponibilidade: Optional[str]
    categoria: Optional[str]
    imagem_url: Optional[str]


router = APIRouter(prefix="/api/v1/books", tags=["books"])


@router.get("", response_model=List[Book])
def list_books(request: Request):
    """Retorna lista de livros já carregados na aplicação."""
    books = list(getattr(request.app.state, "books", []) or [])
    sb = ("rating").lower()
    ordv = ("desc").lower()

    def _rating_value(b: dict):
        r = b.get("rating")
        return r if isinstance(r, int) else -1

    def _title_value(b: dict):
        return (b.get("titulo") or "").lower()

    if sb == "titulo" or sb == "title" or sb == "name":
        reverse = True if ordv == "desc" else False
        books.sort(key=lambda b: (_title_value(b), -_rating_value(b)), reverse=reverse)
    else:
        if ordv == "desc":
            books.sort(key=lambda b: (-_rating_value(b), _title_value(b)))
        else:
            books.sort(key=lambda b: (_rating_value(b), _title_value(b)))

    return books


@router.get("/search", response_model=List[Book])
def search_books(request: Request, title: Optional[str] = None, category: Optional[str] = None):
    """Retorna livros usando filtro por título e categoria. Aceita `title` e `category` como query params."""
    books = list(getattr(request.app.state, "books", []) or [])
    if title:
        title_lower = title.lower()
        books = [b for b in books if title_lower in (b.get("titulo", "") or "").lower()]
    if category:
        cat_lower = category.lower()
        books = [b for b in books if cat_lower == (b.get("categoria", "") or "").lower()]

    sb = ("rating").lower()
    ordv = ("desc").lower()

    def _rating_value(b: dict):
        r = b.get("rating")
        return r if isinstance(r, int) else -1

    def _title_value(b: dict):
        return (b.get("titulo") or "").lower()

    if sb == "titulo" or sb == "title" or sb == "name":
        reverse = True if ordv == "desc" else False
        books.sort(key=lambda b: (_title_value(b), -_rating_value(b)), reverse=reverse)
    else:
        if ordv == "desc":
            books.sort(key=lambda b: (-_rating_value(b), _title_value(b)))
        else:
            books.sort(key=lambda b: (_rating_value(b), _title_value(b)))

    return books





@router.get("/top-rated", response_model=List[Book])
def top_rated_books(request: Request):
    """Lista livros ordenados por rating (maior primeiro)."""
    books = list(getattr(request.app.state, "books", []) or [])
    def _rating_value(b: dict):
        r = b.get("rating")
        return r if isinstance(r, int) else -1
    def _title_value(b: dict):
        return (b.get("titulo") or "").lower()
    books.sort(key=lambda b: (-_rating_value(b), _title_value(b)))
    books = books[:10]
    return books


@router.get("/price-range", response_model=List[Book])
def books_in_price_range(request: Request, min: Optional[float] = Query(None, ge=0.0), max: Optional[float] = Query(None, ge=0.0)):
    """Filtra livros cujo preço esteja no intervalo [min, max]. Se ambos ausentes retorna todos."""
    books = list(getattr(request.app.state, "books", []) or [])
    if min is None and max is None:
        return books
    def _price_value(b: dict):
        p = b.get("preco")
        return p if isinstance(p, (int, float)) else None
    filtered: List[dict] = []
    for b in books:
        p = _price_value(b)
        if p is None:
            continue
        if min is not None and p < min:
            continue
        if max is not None and p > max:
            continue
        filtered.append(b)
    return filtered


@router.get("/{book_id}", response_model=Book)
def get_book(request: Request, book_id: int):
    """Retorna um livro pelo seu `id` atribuído quando salvo (inteiro)."""
    books = list(getattr(request.app.state, "books", []) or [])
    found = next((b for b in books if b.get("id") == book_id), None)
    if not found:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return found
