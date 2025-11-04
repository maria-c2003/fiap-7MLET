from typing import List
from fastapi import APIRouter

from api.v1.books import Book
from script.scrape import scrape_books

router = APIRouter(prefix="/api/v1/scrape", tags=["scrape"])        

@router.get("/" , response_model=List[Book])
def scrape():
    """Triga o processo de scraping
    """
    return scrape_books()
