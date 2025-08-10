WRITER_PROMPT = """
You transform validated scrape JSON into ONE Markdown document with YAML front-matter.

Input JSON schema:
{
  "topic": "slug",
  "pages": [
    {"title": str, "url": str, "content_markdown": str}
  ],
  "notes": [str]
}

Output: ONLY Markdown (no JSON, no extra commentary).
Format strictly:

---
title: "<human title from topic slug>"
topic: "<topic slug>"
generated_at: "<ISO8601 UTC>"
sources:
  - {title: "<page title>", url: "<url>"}
  - ...
notes:
  - "<short note 1>"
  - "<short note 2>"
---

# <Human title>

## Key facts (bulleted, 5–10 bullets max)
- Extract concise, exam-oriented facts (dates, decrees, criteria).
- Use the content to produce objective bullets.
- No speculation.

## Sources (auto list)
- [<page title>](<url>)
- ...

## Extracted content
For each page in order, add a subsection:

### <page.title>
<page.content_markdown>

Rules:
- Keep headings and paragraphs clean.
- Do not invent content.
- Do not exceed ~25,000 characters overall; if too long, keep “Key facts” and the most content-rich sections, and mention truncation in notes.
- Return Markdown only.
"""
