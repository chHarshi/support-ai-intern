# src/triage.py
import os
import json
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI

from src.data_loader import load_kb_docs
from src.retrieval import chunk_kb_docs, KBRetriever

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

PROMPT_VERSION = "triage-v1"
MODEL = "openai/gpt-oss-120b"

TRIAGE_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_triage",
        "description": "Submit the structured triage classification for a support ticket.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_area": {"type": "string"},
                "issue_category": {
                    "type": "string",
                    "enum": ["Billing", "Bug", "Feature Request", "How-To", "Performance", "Security/Access", "Integration"],
                },
                "urgency": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
                "reasoning": {"type": "string"},
                "responder_team": {"type": "string"},
                "draft_response": {"type": "string"},
            },
            "required": ["product_area", "issue_category", "urgency", "reasoning", "responder_team", "draft_response"],
        },
    },
}

SYSTEM_PROMPT = """You are a support ticket triage assistant. Given a ticket's subject and body,
classify it and draft a first response. Use these urgency guidelines:
- P1: production outage, data loss, security breach, service completely unusable
- P2: major feature broken with no workaround, significant business impact
- P3: minor bug, workaround exists, moderate impact
- P4: how-to question, feature request, cosmetic issue

Base your product_area on the product/module mentioned in the ticket.

IMPORTANT: Only reference specific facts (URLs, scope names, error codes, exact steps) that
appear verbatim in the provided knowledge base excerpts. If the KB excerpts don't cover a
specific detail, write the draft_response in general terms and say a specialist will follow up
with exact steps — do not invent URLs, permission names, or configuration details.

Always respond by calling the submit_triage function."""


@dataclass
class TriageResult:
    product_area: str
    issue_category: str
    urgency: str
    reasoning: str
    matched_kb_doc: str
    responder_team: str
    draft_response: str
    prompt_version: str


def triage_ticket(subject: str, body: str, retriever: KBRetriever) -> TriageResult:
    query = f"{subject}\n{body}"
    kb_matches = retriever.search(query, top_k=2)
    kb_context = "\n\n".join(
        f"[{c.doc_filename} - {c.section_title}]\n{c.content[:600]}" for c, _ in kb_matches
    )

    user_prompt = f"""Ticket subject: {subject}
Ticket body: {body}

Relevant knowledge base excerpts:
{kb_context if kb_context else "No close match found."}

Classify this ticket and draft a first response."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            tools=[TRIAGE_TOOL],
            tool_choice={"type": "function", "function": {"name": "submit_triage"}},
        )
        tool_call = response.choices[0].message.tool_calls[0]
        parsed = json.loads(tool_call.function.arguments)
    except Exception as e:
        return TriageResult(
            product_area="Unknown",
            issue_category="Unknown",
            urgency="P3",
            reasoning=f"Triage failed, defaulted to P3 for manual review. Error: {e}",
            matched_kb_doc=kb_matches[0][0].doc_filename if kb_matches else "none",
            responder_team="General Support",
            draft_response="Thanks for reaching out — a support agent will review your ticket shortly.",
            prompt_version=PROMPT_VERSION,
        )

    return TriageResult(
        **parsed,
        matched_kb_doc=kb_matches[0][0].doc_filename if kb_matches else "none",
        prompt_version=PROMPT_VERSION,
    )


if __name__ == "__main__":
    from src.data_loader import load_tickets

    docs = load_kb_docs()
    chunks = chunk_kb_docs(docs)
    retriever = KBRetriever(chunks)

    tickets = load_tickets()

    # test a few different tickets — indices are arbitrary, just picking a spread
    sample_indices = [0, 10, 50, 100]

    for i in sample_indices:
        t = tickets[i]
        print(f"\n{'='*60}")
        print(f"TICKET: {t.ticket_id} — {t.subject}")
        print(f"Ground truth: category={t.category}, urgency={t.urgency}")
        print(f"{'='*60}")

        result = triage_ticket(subject=t.subject, body=t.body, retriever=retriever)
        print(json.dumps(result.__dict__, indent=2))