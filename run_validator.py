import asyncio, json, os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from sub_agents.validator import validator_agent

load_dotenv()

APP_NAME = "adk_validator_test"
USER_ID = "local_user"
SESSION_ID = "validator_s1"

RAW_PATH = "out/tmp_framework_raw.json"

async def main():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"{RAW_PATH} not found. Run run_scraper.py first.")

    with open(RAW_PATH, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    # if it's already a dict string with JSON, we'll just send it as it is.

    session_service = InMemorySessionService()
    runner = Runner(agent=validator_agent, app_name=APP_NAME, session_service=session_service)
    await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    final_json = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=Content(role="user", parts=[Part(text=raw)])
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_json = event.content.parts[0].text

    print(final_json or "")

    # saving cleared version
    os.makedirs("out", exist_ok=True)
    try:
        with open("out/tmp_framework_clean.json", "w", encoding="utf-8") as f:
            f.write(final_json or "")
    except Exception as e:
        print("WARN: failed to write out/tmp_framework_clean.json:", e)

if __name__ == "__main__":
    asyncio.run(main())
