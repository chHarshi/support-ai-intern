# Design Note

## Failure modes

**1. Hallucinated specifics.** The triage agent initially invented a support-article URL
and fake permission scope names not present in the KB — filling gaps with plausible
fabrication instead of admitting the gap. Caught via manual output review, not the eval
harness alone. Fixed with an explicit grounding instruction in the system prompt ("only
use facts verbatim from the KB excerpts"). In production I'd add an automated check that
verifies any URL/scope/error-code in the output actually appears in retrieved context —
the same pattern used for the `quotes_are_verbatim` check in Task 2.

**2. Weak retrieval on ambiguous queries.** TF-IDF is lexical, not semantic, so
vocabulary mismatches ("won't sync" vs "sync failure") can return a low-relevance top
match with no confidence signal. Confirmed with an adversarial ticket about a product
not in the KB at all — it still returned a weak match instead of "no match found."
Fix: add a similarity threshold, and consider embedding-based retrieval.

**3. Eval-harness bugs.** My own Task 2 check flagged a correct output ("$120k") as
failing because it only recognized "$120,000." A reminder that eval code needs its own
scrutiny — too strict erodes trust, too loose hides regressions. Fixed by normalizing
numeric abbreviations before comparing.

## Latency vs. quality

I used Llama 3.3 / gpt-oss-120b via Groq's free tier instead of a larger paid model —
zero-cost iteration and fast inference, at the cost of tighter rate limits and slightly
less nuanced reasoning on ambiguous urgency calls. If latency were the hard constraint,
I'd pin to one fast model with no retries, keep the KB index cached at startup (already
done), and stream draft_response back after classification fields resolve first.

## Data sensitivity

Ticket/account data includes PII (contact names, titles, company names) sent to a
third-party API. In production I'd: redact/tokenize PII before it leaves our
infrastructure, use a provider with a no-training data agreement, log only redacted
prompts, and only include fields the task actually needs (e.g. triage doesn't need
primary_contact).

## Scaling

At 10x volume, the free-tier API rate limit breaks first — well before the retrieval or
data-loading code, which scales with KB size, not ticket count. Fix: paid tier with
higher limits, a request queue with backpressure instead of synchronous calls, and
batched account-brief generation for QBR prep instead of on-demand.
