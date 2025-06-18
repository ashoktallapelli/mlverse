import os
from typing import List, Tuple
from urllib.parse import urlparse

import requests


def classify_pdf_path(path: str) -> str:
    """
    Classify the input path as:
      - 'local'   : an existing local .pdf file
      - 'url'     : a URL ending in .pdf
      - 'unknown' : anything else
    """
    p = path.strip()
    parsed = urlparse(p)

    # 1) URL check
    if parsed.scheme in ("http", "https", "ftp") and parsed.path.lower().endswith(".pdf"):
        return "url"

    # 2) file:// URI
    if parsed.scheme == "file" and parsed.path.lower().endswith(".pdf"):
        return "local"

    # 3) Local filesystem
    if p.lower().endswith(".pdf") and os.path.isfile(os.path.expanduser(p)):
        return "local"

    return "unknown"


def is_url_reachable(url: str, timeout: float = 5.0) -> bool:
    """
    HEAD-request the URL to see if it exists and is a PDF.
    Returns True if 200–399 and 'pdf' in Content-Type.
    """
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        content_type = resp.headers.get("Content-Type", "")
        return (200 <= resp.status_code < 400) and ("pdf" in content_type.lower())
    except requests.RequestException:
        return False


def classify_pdf_list(
        paths: List[str],
        verify_urls: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Returns two lists:
      - local_paths: all inputs classified as local PDFs
      - url_paths: all inputs classified as URLs (if verify_urls=True, only those reachable)
    Unknown or non-PDF entries are ignored.
    """
    local_paths: List[str] = []
    url_paths: List[str] = []

    for p in paths:
        kind = classify_pdf_path(p)
        if kind == "local":
            local_paths.append(p)
        elif kind == "url":
            if not verify_urls or is_url_reachable(p):
                url_paths.append(p)

    return local_paths, url_paths


def filter_pdf_and_non_pdf(
        paths: List[str],
        verify_urls: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Filters the given paths into PDF and non-PDF lists.

    Returns:
      - pdf_paths: all local or reachable URL PDFs
      - non_pdf_paths: all other paths
    """
    # Get classified PDF lists
    pdf_local, pdf_urls = classify_pdf_list(paths, verify_urls)
    # Combine into one list of valid PDFs
    pdf_paths: List[str] = pdf_local + pdf_urls
    # Everything else is non-PDF
    non_pdf_paths: List[str] = [p for p in paths if p not in pdf_paths]

    return pdf_paths, non_pdf_paths


def _detect_content_type(content_path: str) -> str:
    """Auto-detect content type based on path/URL"""
    if _is_valid_youtube_url(content_path):
        return 'youtube'
    elif ',' in content_path and all(_is_valid_youtube_url(url.strip()) for url in content_path.split(',')):
        return 'youtube'
    else:
        return 'pdf'


def _is_valid_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube URL"""
    youtube_domains = [
        'youtube.com',
        'www.youtube.com',
        'youtu.be',
        'm.youtube.com'
    ]

    url_lower = url.lower()
    return any(domain in url_lower for domain in youtube_domains)
