# src/account_brief.py
import os
import json
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI

from src.data_loader import load_tickets, load_accounts, tickets_for_account, Account

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

PROMPT_VERSION = "account-brief-v1"
MODEL = "openai/gpt-oss-120b"

BRIEF_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_account_brief",
        "description": "Submit a structured TAM account health brief.",
        "parameters": {
            "type": "object",
            "properties": {
                "executive_summary": {
                    "type": "string",
                    "description": "3-5 sentences summarizing overall account health and context.",
                },
                "risks_and_flags": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "flag": {"type": "string", "description": "Short description of the risk/signal."},
                            "ticket_id": {"type": "string", "description": "The ticket_id this flag is based on, or 'account_data' if based on account fields not a ticket."},
                            "justification_quote": {"type": "string", "description": "A direct quote from the ticket body/subject supporting this flag. Empty string if based on account_data instead."},
                        },
                        "required": ["flag", "ticket_id", "justification_quote"],
                    },
                },
                "talking_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Recommended talking points for the TAM's next conversation with this account.",
                },
            },
            "required": ["executive_summary", "risks_and_flags", "talking_points"],
        },
    },
}

SYSTEM_PROMPT = """You are an assistant that helps Technical Account Managers (TAMs) prepare for
account reviews (QBRs). Given an account's structured data and its recent ticket history, produce
a concise, actionable brief.

Rules:
- executive_summary: 3-5 sentences, factual, no fluff.
- risks_and_flags: identify tickets or account signals suggesting churn risk or escalation
  (e.g. repeated P1s, negative sentiment, explicit mention of competitors, declining usage,
  low seat utilization vs licensed seats). Every flag based on a ticket MUST include a direct
  quote from that ticket's subject or body as justification_quote. Do not fabricate quotes —
  only use text that appears in the provided ticket data. If a flag is based on account-level
  data (e.g. nps_score, usage_trend) rather than a specific ticket, set ticket_id to
  "account_data" and justification_quote to an empty string.
- talking_points: concrete, specific points the TAM can raise in conversation, tied to the
  account's actual situation (not generic advice).
- Only use facts present in the provided account data and tickets. Do not invent numbers,
  dates, or details not given to you.

Always respond by calling the submit_account_brief function."""


@dataclass
class AccountBrief:
    account_id: str
    company: str
    executive_summary: str
    risks_and_flags: list
    talking_points: list
    prompt_version: str


def _format_account(account: Account) -> str:
    return f"""Account: {account.company} ({account.account_id})
Plan: {account.plan_tier} | ARR: ${account.arr_usd:,.0f}
Seats: {account.seats_active}/{account.seats_licensed} active
Health status: {account.health_status} | Usage trend: {account.usage_trend}
Open tickets: {account.open_tickets} | P1 tickets (last 30d): {account.p1_tickets_last_30d}
Customer since: {account.customer_since} | Renewal: {account.renewal_date}
Last QBR: {account.last_qbr_date} | Last login: {account.last_login_days_ago} days ago
NPS score: {account.nps_score}
Primary contact: {account.primary_contact.get('name')} ({account.primary_contact.get('title')})
Escalation notes: {'; '.join(account.escalation_notes) if account.escalation_notes else 'None'}
Products: {', '.join(account.products)}
Integrations active: {', '.join(account.integrations_active) if account.integrations_active else 'None'}
Region: {account.region} | Industry: {account.industry}"""


def _format_tickets(tickets: list) -> str:
    if not tickets:
        return "No tickets in this period."
    lines = []
    for t in tickets:
        lines.append(
            f"[{t.ticket_id}] subject: \"{t.subject}\" | category: {t.category} | "
            f"urgency: {t.urgency} | status: {t.status} | body: \"{t.body}\""
        )
    return "\n".join(lines)


def generate_account_brief(account_id: str) -> AccountBrief:
    accounts = load_accounts()
    all_tickets = load_tickets()

    account = next((a for a in accounts if a.account_id == account_id), None)
    if account is None:
        raise ValueError(f"No account found with id {account_id}")

    account_tickets = tickets_for_account(account_id, all_tickets)

    user_prompt = f"""{_format_account(account)}

Recent tickets ({len(account_tickets)} total):
{_format_tickets(account_tickets)}

Produce the account brief."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            tools=[BRIEF_TOOL],
            tool_choice={"type": "function", "function": {"name": "submit_account_brief"}},
        )
        tool_call = response.choices[0].message.tool_calls[0]
        parsed = json.loads(tool_call.function.arguments)
    except Exception as e:
        return AccountBrief(
            account_id=account_id,
            company=account.company,
            executive_summary=f"Brief generation failed: {e}. Manual review required.",
            risks_and_flags=[],
            talking_points=[],
            prompt_version=PROMPT_VERSION,
        )

    return AccountBrief(
        account_id=account_id,
        company=account.company,
        executive_summary=parsed["executive_summary"],
        risks_and_flags=parsed["risks_and_flags"],
        talking_points=parsed["talking_points"],
        prompt_version=PROMPT_VERSION,
    )


if __name__ == "__main__":
    accounts = load_accounts()

    # test on the account flagged "At Risk" from your sample data, plus one more
    test_ids = ["ACC-3336"] + [a.account_id for a in accounts if a.account_id != "ACC-3336"][:1]

    for acc_id in test_ids:
        print(f"\n{'='*60}")
        print(f"ACCOUNT BRIEF: {acc_id}")
        print(f"{'='*60}")
        brief = generate_account_brief(acc_id)
        print(json.dumps(brief.__dict__, indent=2))