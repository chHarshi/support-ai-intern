# src/data_loader.py
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta, timezone

DATA_DIR = Path(__file__).parent.parent / "data"


@dataclass
class Ticket:
    ticket_id: str
    account_id: str
    company: str
    subject: str
    body: str
    product: str
    product_area: str
    category: str          # ground-truth label — use for eval only, never feed to the LLM prompt
    urgency: str            # ground-truth label — use for eval only, never feed to the LLM prompt
    status: str
    plan_tier: str
    assigned_agent: str
    created_at: str
    updated_at: str
    tags: list = field(default_factory=list)
    channel: str = ""
    satisfaction_score: Optional[float] = None


@dataclass
class Account:
    account_id: str
    company: str
    tam: str
    plan_tier: str
    arr_usd: float
    seats_licensed: int
    seats_active: int
    products: list
    health_status: str
    usage_trend: str
    open_tickets: int
    p1_tickets_last_30d: int
    customer_since: str
    renewal_date: str
    last_qbr_date: str
    primary_contact: dict
    escalation_notes: list
    nps_score: Optional[float]
    last_login_days_ago: int
    integrations_active: list
    region: str
    industry: str


@dataclass
class KBDoc:
    filename: str
    title: str
    content: str
    category: str


def load_tickets(path: Path = DATA_DIR / "tickets.json") -> list[Ticket]:
    with open(path) as f:
        raw = json.load(f)
    return [Ticket(**t) for t in raw]


def load_accounts(path: Path = DATA_DIR / "accounts.json") -> list[Account]:
    with open(path) as f:
        raw = json.load(f)
    return [Account(**a) for a in raw]


def load_kb_docs(kb_dir: Path = DATA_DIR / "knowledge_base") -> list[KBDoc]:
    docs = []
    for md_file in kb_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        title = content.splitlines()[0].lstrip("#").strip() if content else md_file.stem
        category = md_file.parent.name  # e.g. "billing", "products", "troubleshooting"
        docs.append(KBDoc(filename=md_file.name, title=title, content=content, category=category))
    return docs

def tickets_for_account(account_id: str, tickets: list[Ticket], days: int = 90) -> list[Ticket]:
    """Returns tickets for this account created within the last `days` days,
    relative to the most recent ticket in the dataset (since this is synthetic/mock
    data, not live data — 'now' in the dataset's own timeline gives more realistic
    results than using the actual current date)."""
    account_tickets = [t for t in tickets if t.account_id == account_id]
    if not account_tickets:
        return []

    all_dates = [datetime.fromisoformat(t.created_at.replace("Z", "+00:00")) for t in tickets]
    reference_date = max(all_dates)
    cutoff = reference_date - timedelta(days=days)

    return [
        t for t in account_tickets
        if datetime.fromisoformat(t.created_at.replace("Z", "+00:00")) >= cutoff
    ]


if __name__ == "__main__":
    tickets = load_tickets()
    accounts = load_accounts()
    kb_docs = load_kb_docs()
    print(f"Loaded {len(tickets)} tickets, {len(accounts)} accounts, {len(kb_docs)} KB docs")
    print("\nSample ticket:", tickets[0])
    print("\nSample account:", accounts[0])
    print("\nKB doc categories found:", sorted(set(d.category for d in kb_docs)))