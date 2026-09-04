# evals/account_cases.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import load_accounts, load_tickets, tickets_for_account
from src.account_brief import generate_account_brief
from evals.scoring import CheckResult, TestCaseResult


def _check_has_exec_summary(brief) -> CheckResult:
    sentence_count = brief.executive_summary.count(". ") + 1
    ok = len(brief.executive_summary.strip()) >= 50
    return CheckResult("has_exec_summary", ok, f"~{sentence_count} sentences, len={len(brief.executive_summary)}")


def _check_has_talking_points(brief) -> CheckResult:
    ok = len(brief.talking_points) >= 2
    return CheckResult("has_talking_points", ok, f"count={len(brief.talking_points)}")


def _check_quotes_are_real(brief, account_tickets) -> CheckResult:
    """The key anti-hallucination check: every justification_quote must be an actual
    substring of the referenced ticket's subject or body, not invented."""
    ticket_lookup = {t.ticket_id: t for t in account_tickets}
    bad_quotes = []
    for flag in brief.risks_and_flags:
        quote = flag.get("justification_quote", "")
        tid = flag.get("ticket_id", "")
        if not quote:  # empty quote is fine if ticket_id == "account_data"
            continue
        ticket = ticket_lookup.get(tid)
        if ticket is None:
            bad_quotes.append(f"{tid}: ticket not found")
            continue
        haystack = f"{ticket.subject} {ticket.body}"
        if quote not in haystack:
            bad_quotes.append(f"{tid}: quote not found verbatim")
    ok = len(bad_quotes) == 0
    return CheckResult("quotes_are_verbatim", ok, "; ".join(bad_quotes) if bad_quotes else "")


def _check_no_fabricated_numbers(brief, account) -> CheckResult:
    """Loose check: if a dollar figure is mentioned in the summary, it should correspond
    to the account's real ARR — allowing for common abbreviations like $120k or $1.2M."""
    import re
    summary = brief.executive_summary
    dollar_figures = re.findall(r"\$[\d,.]+[kKmM]?", summary)
    if not dollar_figures:
        return CheckResult("arr_figure_consistent", True, "no dollar figure mentioned")

    arr = account.arr_usd
    for fig in dollar_figures:
        num_str = fig[1:]  # strip '$'
        multiplier = 1
        if num_str[-1] in "kK":
            multiplier = 1_000
            num_str = num_str[:-1]
        elif num_str[-1] in "mM":
            multiplier = 1_000_000
            num_str = num_str[:-1]
        try:
            value = float(num_str.replace(",", "")) * multiplier
        except ValueError:
            continue
        # allow up to 5% rounding tolerance (e.g. "$120k" for $120,000 exactly, or minor rounding)
        if abs(value - arr) / arr <= 0.05:
            return CheckResult("arr_figure_consistent", True, f"{fig} matches ARR ${arr:,.0f}")

    return CheckResult("arr_figure_consistent", False, f"figures {dollar_figures} don't match ARR ${arr:,.0f}")


def build_account_test_cases() -> list[TestCaseResult]:
    accounts = load_accounts()
    all_tickets = load_tickets()
    account_lookup = {a.account_id: a for a in accounts}

    # spread across health statuses for coverage
    case_ids = []
    for status in ("At Risk", "Healthy", "Needs Attention"):
        match = next((a.account_id for a in accounts if a.health_status == status), None)
        if match:
            case_ids.append(match)
    # top up to 5 with arbitrary accounts if fewer than 3 statuses matched
    for a in accounts:
        if len(case_ids) >= 5:
            break
        if a.account_id not in case_ids:
            case_ids.append(a.account_id)

    results = []
    for acc_id in case_ids[:5]:
        account = account_lookup[acc_id]
        account_tickets = tickets_for_account(acc_id, all_tickets)
        brief = generate_account_brief(acc_id)
        checks = [
            _check_has_exec_summary(brief),
            _check_has_talking_points(brief),
            _check_quotes_are_real(brief, account_tickets),
            _check_no_fabricated_numbers(brief, account),
        ]
        results.append(TestCaseResult(case_id=acc_id, task="account_brief", checks=checks))

    # --- adversarial cases ---

    # 1. Account with zero tickets in the period (tests graceful handling of sparse data)
    no_ticket_account = next(
        (a.account_id for a in accounts if len(tickets_for_account(a.account_id, all_tickets)) == 0),
        None,
    )
    if no_ticket_account:
        account = account_lookup[no_ticket_account]
        account_tickets = tickets_for_account(no_ticket_account, all_tickets)
        brief = generate_account_brief(no_ticket_account)
        checks = [
            _check_has_exec_summary(brief),
            _check_has_talking_points(brief),
            _check_quotes_are_real(brief, account_tickets),
        ]
        results.append(TestCaseResult(case_id="adversarial_no_tickets", task="account_brief", checks=checks))

    # 2. Nonexistent account ID — should raise cleanly, not crash the harness
    try:
        generate_account_brief("ACC-99999-DOES-NOT-EXIST")
        raised_correctly = False
        detail = "did not raise"
    except ValueError:
        raised_correctly = True
        detail = "raised ValueError as expected"
    results.append(TestCaseResult(
        case_id="adversarial_nonexistent_account",
        task="account_brief",
        checks=[CheckResult("raises_valueerror_on_bad_id", raised_correctly, detail)],
    ))

    return results