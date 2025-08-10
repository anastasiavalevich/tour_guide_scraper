from google.adk import Agent
from . import prompt

MODEL = "gemini-2.5-pro"

validator_agent = Agent(
    model=MODEL,
    name="validator_agent",
    description="Filters, deduplicates, and normalizes scraped pages; keeps only official and relevant content.",
    instruction=prompt.VALIDATOR_PROMPT,
    output_key="validated",
)
