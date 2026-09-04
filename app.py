# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.data_loader import load_kb_docs
from src.retrieval import chunk_kb_docs, KBRetriever
from src.triage import triage_ticket
from src.account_brief import generate_account_brief

app = FastAPI(title="Support & TAM Tooling API")

# build the retriever once at startup, not per-request
_docs = load_kb_docs()
_chunks = chunk_kb_docs(_docs)
_retriever = KBRetriever(_chunks)


class TicketInput(BaseModel):
    subject: str
    body: str


@app.get("/")
def root():
    return {"status": "ok", "endpoints": ["/triage", "/account-brief/{account_id}"]}


@app.post("/triage")
def triage_endpoint(ticket: TicketInput):
    result = triage_ticket(subject=ticket.subject, body=ticket.body, retriever=_retriever)
    return result.__dict__


@app.get("/account-brief/{account_id}")
def account_brief_endpoint(account_id: str):
    try:
        brief = generate_account_brief(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return brief.__dict__