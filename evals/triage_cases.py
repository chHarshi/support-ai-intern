# evals/triage_cases.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import load_tickets, load_kb_docs
from src.retrieval import chunk_kb_docs, KBRetriever
from src.triage import triage_ticket
from evals.scoring import CheckResult, TestCaseResult

VALID_URGENCY = {"P1", "P2", "P3", "P4"}
VALID_CATEGORY = {"Billing", "Bug", "Feature Request", "How-To", "Performance", "Security/Access", "Integration"}


def _check_valid_urgency(result) -> CheckResult:
    ok = result.urgency in VALID_URGENCY
    return CheckResult("valid_urgency_value", ok, f"got '{result.urgency}'")


def _check_valid_category(result) -> CheckResult:
    ok = result.issue_category in VALID_CATEGORY
    return CheckResult("valid_category_value", ok, f"got '{result.issue_category}'")


def _check_has_reasoning(result) -> CheckResult:
    ok = len(result.reasoning.strip()) >= 20
    return CheckResult("has_substantive_reasoning", ok, f"len={len(result.reasoning)}")


def _check_has_draft_response(result) -> CheckResult:
    ok = len(result.draft_response.strip()) >= 30
    return CheckResult("has_draft_response", ok, f"len={len(result.draft_response)}")


def _check_no_placeholder_leftover(result) -> CheckResult:
    # catches un-filled template artifacts like "[Your Name]" being the ONLY content, or literal "{ticket_id}"
    bad_markers = ["{{", "}}", "TODO", "FIXME"]
    ok = not any(m in result.draft_response for m in bad_markers)
    return CheckResult("no_template_artifacts", ok, "")


def _check_kb_doc_is_real(result, real_kb_filenames: set) -> CheckResult:
    ok = result.matched_kb_doc == "none" or result.matched_kb_doc in real_kb_filenames
    return CheckResult("kb_doc_exists_in_dataset", ok, f"matched '{result.matched_kb_doc}'")


def _check_no_fabricated_urls(result) -> CheckResult:
    # our KB docs don't contain external kb.*.com support-article URLs; a response inventing
    # one is a hallucination signal (see the SecureVault example found during manual testing)
    import re
    urls = re.findall(r"https?://\S+", result.draft_response)
    suspicious = [u for u in urls if "kb." in u or "docs." in u]
    ok = len(suspicious) == 0
    return CheckResult("no_fabricated_kb_urls", ok, f"found: {suspicious}" if suspicious else "")


def build_triage_test_cases() -> list[TestCaseResult]:
    tickets = {t.ticket_id: t for t in load_tickets()}
    kb_docs = load_kb_docs()
    real_kb_filenames = {d.filename for d in kb_docs}
    retriever = KBRetriever(chunk_kb_docs(kb_docs))

    # pick a spread of real tickets across categories/urgencies for coverage
    all_tickets = list(tickets.values())
    case_ids = [
        all_tickets[0].ticket_id,
        all_tickets[10].ticket_id,
        all_tickets[50].ticket_id,
        all_tickets[100].ticket_id,
        all_tickets[200].ticket_id,
    ]

    results = []
    for tid in case_ids:
        t = tickets[tid]
        r = triage_ticket(subject=t.subject, body=t.body, retriever=retriever)
        checks = [
            _check_valid_urgency(r),
            _check_valid_category(r),
            _check_has_reasoning(r),
            _check_has_draft_response(r),
            _check_no_placeholder_leftover(r),
            _check_kb_doc_is_real(r, real_kb_filenames),
            _check_no_fabricated_urls(r),
        ]
        results.append(TestCaseResult(case_id=tid, task="triage", checks=checks))

    # --- adversarial cases ---

    # 1. Ambiguous/vague ticket with almost no information
    r = triage_ticket(subject="Help", body="It's broken. Please fix.", retriever=retriever)
    checks = [
        _check_valid_urgency(r),
        _check_valid_category(r),
        _check_has_reasoning(r),
        _check_has_draft_response(r),
        _check_no_fabricated_urls(r),
    ]
    results.append(TestCaseResult(case_id="adversarial_vague_ticket", task="triage", checks=checks))

    # 2. Ticket mentioning a product NOT in the KB at all
    r = triage_ticket(
        subject="Issue with QuantumMesh Sync",
        body="QuantumMesh Sync keeps disconnecting every 5 minutes and I can't find any settings for it.",
        retriever=retriever,
    )
    checks = [
        _check_valid_urgency(r),
        _check_valid_category(r),
        _check_has_reasoning(r),
        _check_has_draft_response(r),
        _check_no_fabricated_urls(r),
        _check_kb_doc_is_real(r, real_kb_filenames),
    ]
    results.append(TestCaseResult(case_id="adversarial_unknown_product", task="triage", checks=checks))

    return results