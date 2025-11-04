"""Configurações centrais do projeto.

Coloquei aqui todas as opções que o scraper usa por padrão para facilitar
ajustes futuros e centralizar valores.
"""

# CSV de saída padrão
DEFAULT_SAVE_PATH = "/tmp/data/books.csv"

# Scraper defaults
DEFAULT_START_PAGE = 1
DEFAULT_MAX_PAGES = 50
DEFAULT_DELAY = 0.5
DEFAULT_TIMEOUT = 15
DEFAULT_VERIFY_SSL = False

# Requests/session retry strategy
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 0.3
DEFAULT_STATUS_FORCELIST = (500, 502, 503, 504)

# User-Agent
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

# Concurrency
DEFAULT_MAX_WORKERS_PAGES = 10
DEFAULT_MAX_WORKERS_DETAILS = 20

# Target site
URL_BASE = "https://books.toscrape.com/catalogue/"


