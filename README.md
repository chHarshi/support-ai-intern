# Support & TAM AI Tooling
Production-style AI tooling for two internal teams: Technical Support (ticket triage)
and Technical Account Management (account health briefs), built against a mock dataset
of 500 synthetic tickets, 50 synthetic accounts, and a product knowledge base.

## Setup
1. Clone the repo and enter the folder:
   ```
   git clone <your-repo-url>
   cd support-ai-intern
   ```
2. Create a virtual environment (recommended) and install dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate # Windows
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your own Groq API key (free tier — get one at
   console.groq.com):
   ```
   copy .env.example .env
   ```
4. Ensure `data/tickets.json`, `data/accounts.json`, and `data/knowledge_base/` are present
   (the provided mock dataset).

## Running the API
```
uvicorn app:app --reload
```
Then open **http://127.0.0.1:8000/docs** for the interactive Swagger UI, or call the
endpoints directly:
- `POST /triage` — body: `{"subject": "...", "body": "..."}`
- `GET /account-brief/{account_id}` — e.g. `/account-brief/ACC-3336`

## Sample run — Task 1 (Triage)
```
python -m src.triage
```
Runs the triage pipeline against sample tickets from the dataset and prints structured
JSON output (product area, issue category, urgency, KB match, draft response) for each.

## Sample run — Task 2 (Account Brief)
```
python -m src.account_brief
```
Generates a full TAM account brief (executive summary, risks & flags with verbatim
quote justification, talking points) for sample accounts.

## Sample run — Task 3 (Eval Harness)
```
python -m evals.run_evals
```
Runs 14 rule-based test cases (7 for triage, 7 for account briefs, including one
adversarial case per task) and writes `eval_report.json` and `eval_report.md` to the
project root.

## Project structure

```
support-ai-intern/
├── data/                    # mock dataset (tickets, accounts, KB docs)
├── src/
│   ├── data_loader.py       # loads/parses the mock dataset
│   ├── retrieval.py         # TF-IDF KB retriever, chunked by section
│   ├── triage.py            # Task 1: ticket triage agent
│   └── account_brief.py     # Task 2: TAM account health summariser
├── evals/
│   ├── scoring.py           # shared scoring/result classes
│   ├── triage_cases.py      # Task 1 eval cases
│   ├── account_cases.py     # Task 2 eval cases
│   └── run_evals.py         # runs everything, writes eval_report.{json,md}
├── app.py                   # FastAPI entrypoint
├── requirements.txt
├── .env.example
├── eval_report.json / .md
└── DESIGN_NOTE.md           # Task 4
```

## Design note

See [DESIGN_NOTE.md](./DESIGN_NOTE.md) for failure modes, the latency/quality trade-off,
data sensitivity handling, and scaling considerations.

## Notes on model choice
Uses Llama 3.3 / gpt-oss-120b via Groq's free API tier rather than a paid provider — see
the Design Note for the reasoning and trade-offs.
