# Eval Report
Generated: 2026-09-04T11:13:47.599765+00:00

**14/14 passed** | average score: 1.0

| Case | Task | Score | Passed |
|------|------|-------|--------|
| TKT-10000 | triage | 1.0 | ✅ |
| TKT-10010 | triage | 1.0 | ✅ |
| TKT-10050 | triage | 1.0 | ✅ |
| TKT-10100 | triage | 1.0 | ✅ |
| TKT-10200 | triage | 1.0 | ✅ |
| adversarial_vague_ticket | triage | 1.0 | ✅ |
| adversarial_unknown_product | triage | 1.0 | ✅ |
| ACC-3336 | account_brief | 1.0 | ✅ |
| ACC-3033 | account_brief | 1.0 | ✅ |
| ACC-7893 | account_brief | 1.0 | ✅ |
| ACC-4654 | account_brief | 1.0 | ✅ |
| ACC-4610 | account_brief | 1.0 | ✅ |
| adversarial_no_tickets | account_brief | 1.0 | ✅ |
| adversarial_nonexistent_account | account_brief | 1.0 | ✅ |

## Details

### TKT-10000 (triage) — score 1.0
- ✅ valid_urgency_value — got 'P4'
- ✅ valid_category_value — got 'Feature Request'
- ✅ has_substantive_reasoning — len=343
- ✅ has_draft_response — len=608
- ✅ no_template_artifacts
- ✅ kb_doc_exists_in_dataset — matched 'databridge-pro.md'
- ✅ no_fabricated_kb_urls

### TKT-10010 (triage) — score 1.0
- ✅ valid_urgency_value — got 'P4'
- ✅ valid_category_value — got 'How-To'
- ✅ has_substantive_reasoning — len=391
- ✅ has_draft_response — len=928
- ✅ no_template_artifacts
- ✅ kb_doc_exists_in_dataset — matched 'cloudsync.md'
- ✅ no_fabricated_kb_urls

### TKT-10050 (triage) — score 1.0
- ✅ valid_urgency_value — got 'P2'
- ✅ valid_category_value — got 'Bug'
- ✅ has_substantive_reasoning — len=369
- ✅ has_draft_response — len=828
- ✅ no_template_artifacts
- ✅ kb_doc_exists_in_dataset — matched 'authentication-sso.md'
- ✅ no_fabricated_kb_urls

### TKT-10100 (triage) — score 1.0
- ✅ valid_urgency_value — got 'P4'
- ✅ valid_category_value — got 'How-To'
- ✅ has_substantive_reasoning — len=356
- ✅ has_draft_response — len=1073
- ✅ no_template_artifacts
- ✅ kb_doc_exists_in_dataset — matched 'securevault.md'
- ✅ no_fabricated_kb_urls

### TKT-10200 (triage) — score 1.0
- ✅ valid_urgency_value — got 'P4'
- ✅ valid_category_value — got 'Feature Request'
- ✅ has_substantive_reasoning — len=331
- ✅ has_draft_response — len=583
- ✅ no_template_artifacts
- ✅ kb_doc_exists_in_dataset — matched 'workflowengine.md'
- ✅ no_fabricated_kb_urls

### adversarial_vague_ticket (triage) — score 1.0
- ✅ valid_urgency_value — got 'P4'
- ✅ valid_category_value — got 'Bug'
- ✅ has_substantive_reasoning — len=321
- ✅ has_draft_response — len=602
- ✅ no_fabricated_kb_urls

### adversarial_unknown_product (triage) — score 1.0
- ✅ valid_urgency_value — got 'P2'
- ✅ valid_category_value — got 'Bug'
- ✅ has_substantive_reasoning — len=330
- ✅ has_draft_response — len=1093
- ✅ no_fabricated_kb_urls
- ✅ kb_doc_exists_in_dataset — matched 'cloudsync.md'

### ACC-3336 (account_brief) — score 1.0
- ✅ has_exec_summary — ~4 sentences, len=474
- ✅ has_talking_points — count=5
- ✅ quotes_are_verbatim
- ✅ arr_figure_consistent — $500,000 matches ARR $500,000

### ACC-3033 (account_brief) — score 1.0
- ✅ has_exec_summary — ~4 sentences, len=416
- ✅ has_talking_points — count=5
- ✅ quotes_are_verbatim
- ✅ arr_figure_consistent — $120,000 matches ARR $120,000

### ACC-7893 (account_brief) — score 1.0
- ✅ has_exec_summary — ~3 sentences, len=373
- ✅ has_talking_points — count=5
- ✅ quotes_are_verbatim
- ✅ arr_figure_consistent — $24,000 matches ARR $24,000

### ACC-4654 (account_brief) — score 1.0
- ✅ has_exec_summary — ~4 sentences, len=453
- ✅ has_talking_points — count=5
- ✅ quotes_are_verbatim
- ✅ arr_figure_consistent — $96,000 matches ARR $96,000

### ACC-4610 (account_brief) — score 1.0
- ✅ has_exec_summary — ~5 sentences, len=434
- ✅ has_talking_points — count=5
- ✅ quotes_are_verbatim
- ✅ arr_figure_consistent — $48,000. matches ARR $48,000

### adversarial_no_tickets (account_brief) — score 1.0
- ✅ has_exec_summary — ~5 sentences, len=408
- ✅ has_talking_points — count=5
- ✅ quotes_are_verbatim

### adversarial_nonexistent_account (account_brief) — score 1.0
- ✅ raises_valueerror_on_bad_id — raised ValueError as expected
