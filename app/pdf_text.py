from __future__ import annotations

import hashlib
import re
from pathlib import Path

from pypdf import PdfReader


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_pages(path: Path) -> list[str]:
    reader = PdfReader(str(path))
    return [(page.extract_text() or "") for page in reader.pages]


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.replace("−", "-").replace("–", "-").replace("≥", ">=").replace("≤", "<=")
    return re.sub(r"\s+", " ", text).strip().lower()


def text_is_grounded(snippet: object, page_text: str) -> bool:
    needle = normalize_text(snippet)
    return bool(needle) and needle in normalize_text(page_text)

