from ddgs import DDGS
from urllib.parse import urlparse

WHITELIST_HINTS = [
    ".gov.it","ministeroturismo.gov.it","cultura.gov.it",
    "inpa.gov.it","gazzettaufficiale.it","normattiva.it",
    "regione","comune"
]

def _allowed(url: str, allow_domains_list):
    host = urlparse(url).netloc.lower()
    hints = allow_domains_list or WHITELIST_HINTS
    return any(h in host for h in hints)

def search_urls(query: str, max_results: int, allow_domains: str):
    """
    Args:
        query: search string
        max_results: number of results to return (e.g., 8)
        allow_domains: comma-separated domain substrings, e.g., ".gov.it,inpa.gov.it"
    """
    # Parsing a line into a list
    if allow_domains:
        allow_domains_list = [d.strip() for d in allow_domains.split(",") if d.strip()]
    else:
        allow_domains_list = WHITELIST_HINTS

    out = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            url = r.get("href") or r.get("url")
            if not url:
                continue
            if _allowed(url, allow_domains_list):
                out.append({"title": r.get("title",""), "url": url})
    return out
