"""Descarga la serie de la Encuesta de Supermercados del INDEC a data/raw/.

Fuente: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-1-34
Uso:    python src/download.py
"""
from datetime import datetime
from pathlib import Path

import requests

URL = "https://www.indec.gob.ar/ftp/cuadros/economia/serie_supermercados.xlsx"
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / "serie_supermercados.xlsx"
    resp = requests.get(URL, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] {len(resp.content):,} bytes -> {dest}")
    print(f"Last-Modified (servidor INDEC): {resp.headers.get('Last-Modified')}")


if __name__ == "__main__":
    main()
