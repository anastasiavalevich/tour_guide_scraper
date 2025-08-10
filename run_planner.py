import asyncio, json, os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from sub_agents.topic_planner import topic_planner_agent

APP_NAME = "adk_planner"
USER_ID = "local_user"
SESSION_ID = "planner_s1"
OUT_DIR = "out"
PLAN_PATH = os.path.join(OUT_DIR, "tmp_plan.json")

def _sanitize_json_text(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        i, j = t.find("{"), t.rfind("}")
        t = t[i:j+1] if i != -1 and j != -1 else ""
    return t

async def main():
    load_dotenv()
    os.makedirs(OUT_DIR, exist_ok=True)

    session_service = InMemorySessionService()
    runner = Runner(agent=topic_planner_agent, app_name=APP_NAME, session_service=session_service)
    await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    payload = {
        "brief": (
            "Scrape official data about the 2025 National Qualifying Examination for Tourist Guides in Italy. "
            "Prioritize official sources (.gov.it, Ministero del Turismo, Gazzetta Ufficiale, inPA, Normattiva, Regioni/Comuni)."
        ),
        "seed_doc_hint": "Use terms: bando, Gazzetta Ufficiale, DM/Decreto, inPA, requisiti, prove d'esame, scadenze, equivalenza titoli."
    }

    plan_text = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=Content(role="user", parts=[Part(text=json.dumps(payload))])
    ):
        if event.is_final_response() and event.content and event.content.parts:
            plan_text = event.content.parts[0].text

    if not plan_text:
        raise RuntimeError("Planner returned empty result.")

    # Sanitation and validation
    clean_text = _sanitize_json_text(plan_text)
    try:
        plan_obj = json.loads(clean_text)
    except json.JSONDecodeError as e:
        # show the first 500 characters for debugging
        preview = clean_text[:500]
        raise RuntimeError(f"Planner output is not valid JSON. Preview:\n{preview}") from e

    # A little check of the expected structure
    # We expect that the plan will include: {"topics":[{"slug":..., "title":..., "queries":[...]} , ...]}
    if not isinstance(plan_obj, dict) or "topics" not in plan_obj or not isinstance(plan_obj["topics"], list):
        raise RuntimeError("Planner JSON does not contain expected 'topics' array.")

    # Saving
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan_obj, f, ensure_ascii=False, indent=2)

    # Short summary in the console
    print(f"Plan saved to {PLAN_PATH}")
    print("Topics:")
    for t in plan_obj["topics"]:
        slug = t.get("slug")
        title = t.get("title")
        qn = len(t.get("queries", []))
        print(f" - {slug} | {title} | {qn} queries")

if __name__ == "__main__":
    asyncio.run(main())
