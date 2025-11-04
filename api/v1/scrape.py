from fastapi import APIRouter, Request

from script.scrape import scrape_books

router = APIRouter(prefix="/api/v1/scrape", tags=["scrape"])        

@router.get("/")
def scrape(request: Request):
    """Triga o processo de scraping
    """
    books = scrape_books()
    request.app.state.books = books
    return books
