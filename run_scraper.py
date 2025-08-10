import asyncio, os, json 
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from sub_agents.scraping import scraping_agent

load_dotenv()

APP_NAME = "adk_scraper_test"
USER_ID = "local_user"
SESSION_ID = "scraper_s1"

async def main():
    session_service = InMemorySessionService()
    runner = Runner(agent=scraping_agent, app_name=APP_NAME, session_service=session_service)
    await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    payload = {
        "topic": {"slug": "framework_and_law", "title": "Framework and Law"},
        "queries": [
            "esame abilitazione guida turistica 2025 legge",
            "site:inpa.gov.it guida turistica 2025",
            "site:gazzettaufficiale.it guida turistica",
            "site:ministeroturismo.gov.it esame guida turistica"
        ]
    }

    final_json = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=Content(role="user", parts=[Part(text=json.dumps(payload))])
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_json = event.content.parts[0].text

    print(final_json)  # must be JSON with {"topic":"framework_and_law","pages":[...]}
    os.makedirs("out", exist_ok=True)
    try:
        with open("out/tmp_framework_raw.json", "w", encoding="utf-8") as f:
            f.write(final_json or "")
    except Exception as e:
        print("WARN: failed to write out/tmp_framework_raw.json:", e)

if __name__ == "__main__":
    asyncio.run(main())
