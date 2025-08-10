from google.adk import Agent
from . import prompt

MODEL = "gemini-2.5-pro"

topic_planner_agent = Agent(
    model=MODEL,
    name="topic_planner_agent",
    description="Plans topics and seed queries for the tourist guide exam 2025 scraping task.",
    instruction=prompt.TOPIC_PLANNER_PROMPT,
    output_key="topic_plan",
)
