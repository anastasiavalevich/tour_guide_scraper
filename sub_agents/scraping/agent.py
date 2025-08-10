from google.adk import Agent
from google.adk.tools import FunctionTool
from . import prompt
from .fetch_page import fetch_and_clean
from .search_tool import search_urls

MODEL = "gemini-2.5-pro"

# ---- PROXY FUNCTIONS WITH UNIQUE NAMES ----
def fetch_url_to_markdown(url: str):
    """Primary wrapper used by the model."""
    return fetch_and_clean(url)

def fetch_url_to_markdown_func(url: str):
    """Alias wrapper, in case the model calls *_func."""
    return fetch_and_clean(url)

# ---- TOOLS ----
fetch_tool = FunctionTool(func=fetch_url_to_markdown)
fetch_tool.name = "fetch_url_to_markdown"
fetch_tool.description = "Download a webpage or PDF and return {'title','url','content_markdown'}."

fetch_tool_alias2 = FunctionTool(func=fetch_url_to_markdown_func)
fetch_tool_alias2.name = "fetch_url_to_markdown_func"
fetch_tool_alias2.description = "Alias of fetch_url_to_markdown."

search_tool = FunctionTool(func=search_urls)
search_tool.name = "search_urls"
search_tool.description = "DuckDuckGo search. Args: query:str, max_results:int, allow_domains:str (comma-separated)."

scraping_agent = Agent(
    model=MODEL,
    name="scraping_agent",
    description="Search authoritative URLs by topic, fetch them, and return clean Markdown grouped by topic.",
    instruction=prompt.SCRAPING_PROMPT,
    output_key="crawled_topics",
    tools=[search_tool, fetch_tool, fetch_tool_alias2],
)
