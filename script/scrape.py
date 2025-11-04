import os
import re
import logging
from typing import List, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import concurrent.futures
import config


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def _create_session_with_retries() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=config.DEFAULT_RETRIES,
        read=config.DEFAULT_RETRIES,
        connect=config.DEFAULT_RETRIES,
        backoff_factor=config.DEFAULT_BACKOFF,
        status_forcelist=config.DEFAULT_STATUS_FORCELIST,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def scrape_books(start_page: int = None) -> List[Dict]:

    if start_page is None:
        start_page = config.DEFAULT_START_PAGE
    timeout = config.DEFAULT_TIMEOUT
    verify_ssl = config.DEFAULT_VERIFY_SSL
    save_to = config.DEFAULT_SAVE_PATH
    headers = {"User-Agent": config.DEFAULT_USER_AGENT}

    url_base = config.URL_BASE
    all_books_data: List[Dict] = []

    session = _create_session_with_retries()
    session.headers.update(headers)

    session.verify = verify_ssl
    if not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    pages_visited = 0

    def _process_single_page(page_num: int) -> List[Dict]:
        page_url = url_base + f"page-{page_num}.html"
        try:
            resp = session.get(page_url, timeout=timeout)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logging.warning("Falha ao acessar %s: %s", page_url, exc)
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        livros = soup.find_all("article", class_="product_pod")

        books_on_page = []
        for livro in livros:
            try:
                titulo = livro.h3.a["title"]
                preco_str = livro.find("p", class_="price_color").text
                preco_match = re.search(r"[\d\.]+", preco_str)
                preco = float(preco_match.group()) if preco_match else None
                rating = livro.find("p", class_="star-rating")["class"][1]
                disponibilidade = livro.find("p", class_="instock availability").text.strip()
                url_imagem_relativa = livro.find("img")["src"]
                url_imagem_completa = "https://books.toscrape.com/" + url_imagem_relativa.replace("../", "")
                url_livro_relativa = livro.h3.a["href"]
                url_livro_completa = url_base + url_livro_relativa

                books_on_page.append({
                    "titulo": titulo,
                    "preco": preco,
                    "rating": rating,
                    "disponibilidade": disponibilidade,
                    "imagem_url": url_imagem_completa,
                    "url_livro_completa": url_livro_completa,
                    "categoria": "",
                })
            except Exception as e:
                logging.debug("Erro ao parsear item de livro: %s", e)

        def _fetch_category(url: str) -> str:
            try:
                r = requests.get(url, headers=headers, verify=session.verify, timeout=timeout)
                r.raise_for_status()
                soup_livro = BeautifulSoup(r.text, "html.parser")
                breadcrumb_links = soup_livro.find("ul", class_="breadcrumb").find_all("a")
                return breadcrumb_links[-1].text if breadcrumb_links else ""
            except Exception:
                return ""

        if books_on_page:
            with concurrent.futures.ThreadPoolExecutor(max_workers=config.DEFAULT_MAX_WORKERS_DETAILS) as detail_executor:
                futures = [detail_executor.submit(_fetch_category, b["url_livro_completa"]) for b in books_on_page]
                for b, fut in zip(books_on_page, concurrent.futures.as_completed(futures)):
                    try:
                        b["categoria"] = fut.result()
                    except Exception:
                        b["categoria"] = ""

        return books_on_page


    page_nums = list(range(start_page, start_page + config.DEFAULT_MAX_PAGES))
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as page_executor:
        future_to_page = {page_executor.submit(_process_single_page, pn): pn for pn in page_nums}
        for fut in concurrent.futures.as_completed(future_to_page):
            pages_visited += 1
            page_books = fut.result()
            for book in page_books:
                all_books_data.append({
                    "titulo": book["titulo"],
                    "preco": book["preco"],
                    "rating": book["rating"],
                    "disponibilidade": book["disponibilidade"],
                    "categoria": book["categoria"],
                    "imagem_url": book["imagem_url"],
                })

    logging.info("Scraping finalizado! %d livros encontrados.", len(all_books_data))

    def _rating_to_int(rating_val):
        if rating_val is None:
            return None
        try:
            if isinstance(rating_val, (int, float)):
                return int(rating_val)
            rv = str(rating_val).strip()
            if rv.isdigit():
                return int(rv)
            word_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
            rv_lower = rv.lower()
            if rv_lower in word_map:
                return word_map[rv_lower]
            m = re.search(r"(\d+)", rv)
            if m:
                return int(m.group(1))
        except Exception:
            pass
        return None

    processed = []
    for idx, b in enumerate(all_books_data, start=1):
        nb = dict(b)
        nb["rating"] = _rating_to_int(nb.get("rating"))
        nb["id"] = idx
        processed.append(nb)

    if save_to:
        try:
            save_to_csv(processed, filename=save_to)
        except Exception as e:
            logging.exception("Erro ao salvar CSV em %s: %s", save_to, e)

    return processed


def save_to_csv(books_data: List[Dict], filename: str) -> None:
    if not books_data:
        logging.warning("Nenhum dado para salvar em CSV.")
        return

    dirpath = os.path.dirname(filename)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    df = pd.DataFrame(books_data)
    df.to_csv(filename, index=False)
    logging.info("Dados salvos em %s", filename)
