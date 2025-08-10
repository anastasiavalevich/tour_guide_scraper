import os, sys, json, argparse, datetime
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from sub_agents.scraping import scraping_agent
from sub_agents.validator import validator_agent
from sub_agents.writer import writer_agent

APP_NAME = "adk_pipeline"
USER_ID = "local_user"

SESSION_SCRAPER = "pipe_scraper_s1"
SESSION_VALIDATOR = "pipe_validator_s1"
SESSION_WRITER  = "pipe_writer_s1"

OUT_DIR = "out"
PLAN_PATH = os.path.join(OUT_DIR, "tmp_plan.json")

def _sanitize_json_text(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        i, j = t.find("{"), t.rfind("}")
        t = t[i:j+1] if i != -1 and j != -1 else ""
    return t

def _human_title_from_slug(slug: str) -> str:
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

def _filename_from_slug(slug: str) -> str:
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

async def _run_single_topic(session_service: InMemorySessionService, topic: dict, queries: list[str]):
    slug  = topic["slug"]
    title = topic.get("title") or _human_title_from_slug(slug)

    # 1) SCRAPER
    scraper_runner = Runner(agent=scraping_agent, app_name=APP_NAME, session_service=session_service)
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=f"{SESSION_SCRAPER}_{slug}")

    scraper_input = {"topic": {"slug": slug, "title": title}, "queries": queries}
    scraped_text = None
    async for event in scraper_runner.run_async(
        user_id=USER_ID,
        session_id=f"{SESSION_SCRAPER}_{slug}",
        new_message=Content(role="user", parts=[Part(text=json.dumps(scraper_input, ensure_ascii=False))]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            scraped_text = event.content.parts[0].text

    scraped_text = _sanitize_json_text(scraped_text)
    scraped_obj = json.loads(scraped_text)
    raw_path = os.path.join(OUT_DIR, f"tmp_{slug}_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(scraped_obj, f, ensure_ascii=False, indent=2)
    print(f"[SCRAPER] {slug}: saved {raw_path}")

    # 2) VALIDATOR
    validator_runner = Runner(agent=validator_agent, app_name=APP_NAME, session_service=session_service)
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=f"{SESSION_VALIDATOR}_{slug}")

    clean_text = None
    async for event in validator_runner.run_async(
        user_id=USER_ID,
        session_id=f"{SESSION_VALIDATOR}_{slug}",
        new_message=Content(role="user", parts=[Part(text=json.dumps(scraped_obj, ensure_ascii=False))]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            clean_text = event.content.parts[0].text

    clean_text = _sanitize_json_text(clean_text)
    clean_obj = json.loads(clean_text)
    clean_path = os.path.join(OUT_DIR, f"tmp_{slug}_clean.json")
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(clean_obj, f, ensure_ascii=False, indent=2)
    print(f"[VALIDATOR] {slug}: saved {clean_path}")

    # 3) WRITER
    writer_runner = Runner(agent=writer_agent, app_name=APP_NAME, session_service=session_service)
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=f"{SESSION_WRITER}_{slug}")

    clean_obj.setdefault("_human_title", title)
    clean_obj.setdefault("_generated_at", datetime.datetime.now(datetime.UTC).isoformat())

    final_md = None
    async for event in writer_runner.run_async(
        user_id=USER_ID,
        session_id=f"{SESSION_WRITER}_{slug}",
        new_message=Content(role="user", parts=[Part(text=json.dumps(clean_obj, ensure_ascii=False))]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_md = event.content.parts[0].text

    if not final_md:
        raise RuntimeError(f"Writer returned empty result for {slug}.")

    out_md_path = os.path.join(OUT_DIR, _filename_from_slug(slug))
    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write(final_md)
    print(f"[WRITER]  {slug}: saved {out_md_path}")

async def main():
    load_dotenv()
    os.makedirs(OUT_DIR, exist_ok=True)

    # CLI
    ap = argparse.ArgumentParser(description="Planner-driven pipeline: Scraper → Validator → Writer")
    ap.add_argument("--only", help="Comma-separated slugs to run (e.g., framework_and_law,required_documents)")
    ap.add_argument("--limit-topics", type=int, default=0, help="Process only first N topics from plan")
    ap.add_argument("--limit-queries", type=int, default=0, help="Use only first M queries per topic")
    args = ap.parse_args()

    if not os.path.exists(PLAN_PATH):
        print(f"Plan file not found: {PLAN_PATH}. Run: python run_planner.py")
        sys.exit(1)

    plan = json.load(open(PLAN_PATH, "r", encoding="utf-8"))
    topics = plan.get("topics", [])
    if not topics:
        print("No topics in plan.")
        sys.exit(1)

    if args.only:
        wanted = {s.strip() for s in args.only.split(",")}
        topics = [t for t in topics if t.get("slug") in wanted]

    if args.limit_topics and args.limit_topics > 0:
        topics = topics[:args.limit_topics]

    session_service = InMemorySessionService()

    for t in topics:
        slug = t.get("slug")
        queries = t.get("queries", [])
        if args.limit_queries and args.limit_queries > 0:
            queries = queries[:args.limit_queries]

        print(f"\n=== RUN {slug} ({len(queries)} queries) ===")
        try:
            await _run_single_topic(session_service, t, queries)
        except Exception as e:
            print(f"[ERROR] {slug}: {e}")
            # continue the remaining topics

if __name__ == "__main__":
    asyncio.run(main())
