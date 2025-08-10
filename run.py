import asyncio, json
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agent import root_agent

load_dotenv()

APP_NAME = "adk_smoke"
USER_ID = "local_user"
SESSION_ID = "s1"

async def main():
    # 1) session service (in—memory for simplicity)
    session_service = InMemorySessionService()
    # 2) runner
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    # 3) creating a session
    await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    # 4) we send a message and wait for the final response
    final_text = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=Content(role="user", parts=[Part(text="ping")])
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text

    print(json.dumps({"final_text": final_text}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
