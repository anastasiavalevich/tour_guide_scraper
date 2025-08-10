import os, asyncio, json, datetime
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from sub_agents.writer import writer_agent

CLEAN_PATH = "out/tmp_framework_clean.json"
OUT_DIR = "out"

APP_NAME = "adk_writer_test"
USER_ID = "local_user"
SESSION_ID = "writer_s1"

def human_title_from_slug(slug: str) -> str:
    mapping = {
        "framework_and_law": "Framework and Law",
        "application_procedure": "Application Procedure",
        "deadlines_and_timing": "Deadlines and Timing",
        "required_documents": "Required Documents",
        "exam_structure_and_scoring": "Exam Structure and Scoring",
        "regional_specifics": "Regional Specifics",
        "faq_and_contacts": "FAQ & Contacts",
    }
    return mapping.get(slug, slug.replace("_", " ").title())

def filename_from_slug(slug: str) -> str:
    order = {
        "framework_and_law": "01",
        "application_procedure": "02",
        "deadlines_and_timing": "03",
        "required_documents": "04",
        "exam_structure_and_scoring": "05",
        "regional_specifics": "06",
        "faq_and_contacts": "07",
    }
    prefix = order.get(slug, "99")
    return f"{prefix}_{slug}.md"

async def main():
    load_dotenv()
    if not os.path.exists(CLEAN_PATH):
        raise FileNotFoundError(f"{CLEAN_PATH} not found. Run run_validator.py first.")

    # reading validated JSON
    with open(CLEAN_PATH, "r", encoding="utf-8") as f:
        data_str = f.read().strip()
    
    # sanitize: remove possible ```json ... ```
    if data_str.startswith("```"):
        i, j = data_str.find("{"), data_str.rfind("}")
        data_str = data_str[i:j+1] if i != -1 and j != -1 else ""

    if not data_str:
        raise RuntimeError("Clean file is empty after sanitization.")

    data = json.loads(data_str)

    # we'll substitute the human title + timestamps, if necessary (the model can also do it itself)
    data.setdefault("topic", "framework_and_law")
    slug = data["topic"]
    data.setdefault("_human_title", human_title_from_slug(slug))
    data.setdefault("_generated_at", datetime.datetime.now(datetime.UTC).isoformat())

    # we send it to the agent as text (the model expects a JSON text)
    session_service = InMemorySessionService()
    runner = Runner(agent=writer_agent, app_name=APP_NAME, session_service=session_service)
    await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    final_md = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=Content(role="user", parts=[Part(text=json.dumps(data, ensure_ascii=False))])
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_md = event.content.parts[0].text

    if not final_md:
        raise RuntimeError("Writer returned empty result.")

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, filename_from_slug(slug))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_md)

    print(f"Markdown saved to: {out_path}")

if __name__ == "__main__":
    asyncio.run(main())
