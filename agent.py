from google.adk.agents import LlmAgent

MODEL = "gemini-2.5-pro"

root_agent = LlmAgent(
    name="smoke_test_agent",
    model=MODEL,
    description="Just confirms that Gemini works.",
    instruction="Reply with a single line 'OK - ADK works' and nothing else.",
)
