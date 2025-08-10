import re, requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import trafilatura

def _is_pdf_url(url: str) -> bool:
    return urlparse(url).path.lower().endswith(".pdf")

def _pdf_bytes_to_md(pdf_bytes: bytes) -> str:
    try:
        text = trafilatura.extract(pdf_bytes, input_format="pdf")
        return (text or "").strip()
    except Exception:
        return ""

def _html_to_md(html: str, base_url: str) -> str:
    extracted = trafilatura.extract(html, url=base_url, include_comments=False, include_images=False)
    if extracted:
        return extracted.strip()
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","nav","footer","header","noscript","aside"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    return text.strip()

def fetch_and_clean(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (ADK-scraper)"}
    r = requests.get(url, headers=headers, timeout=40)
    r.raise_for_status()

    if _is_pdf_url(url):
        content_md = _pdf_bytes_to_md(r.content)
        title = url.split("/")[-1]
    else:
        html = r.text
        content_md = _html_to_md(html, base_url=url)
        try:
            soup = BeautifulSoup(html, "html.parser")
            title = (soup.title.string or "").strip() if soup.title else url
        except Exception:
            title = url

    content_md = re.sub(r"\n{3,}", "\n\n", content_md or "").strip()
    return {"title": title, "url": url, "content_markdown": content_md}
