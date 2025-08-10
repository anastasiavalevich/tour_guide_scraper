from google.adk import Agent
from . import prompt

MODEL = "gemini-2.5-pro"

writer_agent = Agent(
    model=MODEL,
    name="writer_agent",
    description="Turns validated JSON into a single Markdown file with YAML front-matter and clean sections.",
    instruction=prompt.WRITER_PROMPT,
    output_key="markdown",
)
