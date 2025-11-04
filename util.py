import csv
import os
from typing import List, Optional, Dict


class Util:
    @staticmethod
    def get_books_from_csv(csv_path: Optional[str] = None) -> List[Dict]:
        """Lê um CSV de livros e retorna lista de dicionários com tipos convertidos.

        Se `csv_path` não for informado, tenta `tmp/data/books.csv` no diretório do projeto.
        """
        if csv_path is None:
            project_root = os.path.dirname(__file__)
            csv_path = os.path.join(project_root, "tmp", "data", "books.csv")

        if not os.path.exists(csv_path):
            return []

        books: List[Dict] = []
        with open(csv_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    _id = int(row.get("id") or 0)
                except ValueError:
                    _id = 0

                titulo = (row.get("titulo") or "").strip()

                preco_raw = row.get("preco")
                try:
                    preco = float(preco_raw) if preco_raw not in (None, "", "None") else None
                except ValueError:
                    preco = None

                rating_raw = row.get("rating")
                try:
                    rating = int(rating_raw) if rating_raw not in (None, "", "None") else None
                except ValueError:
                    rating = None

                disponibilidade = row.get("disponibilidade") or None
                categoria = row.get("categoria") or None
                imagem_url = row.get("imagem_url") or None

                books.append({
                    "id": _id,
                    "titulo": titulo,
                    "preco": preco,
                    "rating": rating,
                    "disponibilidade": disponibilidade,
                    "categoria": categoria,
                    "imagem_url": imagem_url,
                })

        return books
