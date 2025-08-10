SCRAPING_PROMPT = """
Available tools (use EXACT names):
- search_urls(query: str, max_results: int, allow_domains: str)  # allow_domains is comma-separated
- fetch_url_to_markdown(url: str)
Do not invent other tool names.

Do NOT call any other function names. If you need to fetch a URL, call fetch_url_to_markdown.

Input:
{
  "topic": {"slug": str, "title": str},
  "queries": [str, ...]
}

Process per query:
1) Call search_urls(query, max_results=8, allow_domains=".gov.it,ministeroturismo.gov.it,cultura.gov.it,inpa.gov.it,gazzettaufficiale.it,normattiva.it,regione,comune").
2) Keep authoritative URLs only (ministerial, inPA, Gazzetta Ufficiale, Normattiva, regional portals).
   Skip blogs/forums.
3) For each chosen URL (overall max 10 per topic), call fetch_url_to_markdown(url)
   to get {title, url, content_markdown}.

Return ONLY JSON:
{
  "topic": "slug",
  "pages": [
    {"title": "...", "url": "...", "content_markdown": "..."},
    ...
  ]
}
"""
