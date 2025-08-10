# Tour Guide Exam Scraper

This project automatically collects, cleans, and structures data about the **2025 National Qualification Exam for Tour Guides in Italy** from official sources.  
The result is a set of topic-based Markdown files with up-to-date information, useful for exam preparation.

## Project Structure

├── run_planner.py # Generates topic plan and search queries\
├── run_pipeline.py # Runs scraping, validation, and Markdown export\
├── sub_agents/ # Sub-agents (scraper, validator, writer, planner)\
├── out/ # Output data (Markdown + intermediate JSON)\
│ ├── 01_framework_and_law.md\
│ ├── 02_application_procedure.md\
│ ├── 03_deadlines_and_timing.md\
│ ├── 04_required_documents.md\
│ ├── 05_exam_structure_and_scoring.md\
│ ├── 06_regional_specifics.md\
│ └── 07_faq_and_contacts.md\
├── .env # API tokens and keys (do not commit!)\
├── requirements.txt # Python dependencies\
└── README.md

## Installation

1. Clone the repository:

   ```bash
   git clone <repo_url>
   cd tour_guide_scraper

   ```

2. Create and activate a virtual environment:

   ```python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows

   ```

3. Install dependencies:\
   `pip install -r requirements.txt`

4. Create a `.env` file and set your keys:\
   `GOOGLE_API_KEY=...`

## Usage

1. Generate topics and queries:\
   `python run_planner.py`

This will produce `out/tmp_plan.json` with topics and related search queries.

2. Run the full pipeline:\
   `python run_pipeline.py`

The script will:

- Search for links for each topic
- Download pages / PDFs
- Clean and validate the text
- Save final Markdown files in `out/`
- You can also run it for specific topics:\
  `python run_pipeline.py --only application_procedure,deadlines_and_timing`

## Output

All ready-to-use files are located in the `out/` folder:

```01_framework_and_law.md
02_application_procedure.md
...
07_faq_and_contacts.md

```

Each file contains:

- Key facts (bulleted list)
- List of sources with URLs
- Cleaned and extracted text from official documents

## Notes

- The scraper uses Google ADK (`gemini-2.5-pro`) and DuckDuckGo for search.
- Sources are filtered by domain; priority is given to official websites.
