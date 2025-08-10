TOPIC_PLANNER_PROMPT = """
You plan the scraping for the Italian National Qualifying Examination for Tourist Guides (2025).

Input: { "brief": str, "seed_doc_hint": str (optional) }

Output: ONLY valid JSON with this schema:
{
  "topics": [
    {
      "slug": "framework_and_law",
      "title": "Framework and Law",
      "queries": [
        "esame abilitazione guida turistica 2025 legge",
        "ministero del turismo esame guida turistica 2025 bando",
        "site:inpa.gov.it guida turistica 2025",
        "site:gazzettaufficiale.it guida turistica 2025",
        "site:normattiva.it guida turistica"
      ]
    },
    {
      "slug": "application_procedure",
      "title": "Application Procedure",
      "queries": ["…"]
    },
    {
      "slug": "deadlines_and_timing",
      "title": "Deadlines and Timing",
      "queries": ["…"]
    },
    {
      "slug": "required_documents",
      "title": "Required Documents",
      "queries": ["…"]
    },
    {
      "slug": "exam_structure_and_scoring",
      "title": "Exam Structure and Scoring",
      "queries": ["…"]
    },
    {
      "slug": "regional_specifics",
      "title": "Regional Specifics",
      "queries": ["…"]
    },
    {
      "slug": "faq_and_contacts",
      "title": "FAQ & Contacts",
      "queries": ["…"]
    }
  ]
}

Rules:
- Prefer official sources in queries: ministeroturismo.gov.it, cultura.gov.it, inpa.gov.it, gazzettaufficiale.it, normattiva.it, regional gov portals (regione.*, comune.*).
- Do NOT include explanations or comments. Return JSON only.
"""
