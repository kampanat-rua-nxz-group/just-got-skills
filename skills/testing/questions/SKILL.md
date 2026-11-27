---
name: questions
description: Use when the user wants a design, API specification, sequence diagram, or requirements document reviewed for gaps and ambiguities and answered as pinpointed questions for its authors, such as before refinement or test design, or invokes /questions.
argument-hint: "[document path, link, or pasted text]"
---

# questions — pinpointed questions on a design or spec

Review the supplied documents through a QA lens and return questions for their authors. Each question points at the exact spot it comes from. Return questions only; derive test scenarios with the `scenario` skill.

Return at least two questions, and aim for three or more. Never pad the list. When a full pass finds fewer than two real questions, return the ones you found and list the areas you checked and found complete.

## Workflow

1. **Read every supplied document in full**: designs, API specs, sequence diagrams, acceptance criteria, and their linked references. Note each document's name and version or date. Stay read-only.
2. **Look for what a test cannot be written without.**
   - **Undefined results:** error status, error code, and message; empty, null, and omitted values; defaults.
   - **Limits:** minimum and maximum, length, precision and rounding, currency, time zones, and date formats.
   - **Allowed values:** enums, case sensitivity, required versus optional, and pagination and sorting.
   - **Contradictions:** between sections, between the spec and a diagram, and between the text and an example payload.
   - **Flow and state:** missing transitions, retries, timeouts, idempotency, concurrency, async callbacks, ordering, and partial failure or rollback.
   - **Access:** roles, ownership, rate limits, and personal data.
   - **Vague words:** "valid", "appropriate", "should", "fast", "usually", "etc.". Ask for the number or the rule.
   - **Testability:** how a result is observed, test data and environment needs, feature flags, and backward compatibility.
3. **Check before you keep a question.** Search all supplied documents for the answer. Drop the question when a document answers it. When two documents answer it differently, keep it as a contradiction and cite both places.
4. **Rank the questions.**
   - **Blocking** — no expected result or test can be written until it is answered.
   - **Important** — a test can be written, but its assertion may be wrong.
   - **Minor** — wording or completeness that does not change a test.
   
   Lead with Blocking. Return at most 10 unless the user asks for all, and give the count of the rest.
5. **Offer the next step.** When the service code or a test environment could show the current behavior, say so and offer the `probe` skill. Its answer is observed behavior, so the question still goes to the author.

## Output

Write the questions in the language of the source documents unless the user asks for another.

```
### Q1. <one-sentence question> — Blocking
- **Where:** <document> › <section, endpoint, field, or diagram step> (line or page when known)
- **Quote:** "<the exact text the question is about>"
- **Why it matters:** <the test or behavior that depends on the answer>
- **Options:** (a) <one plausible answer>; (b) <another>
- **Ask:** <the owner the document names, or the role: PO, backend, design>
```

Use **Options** to make each question quick to answer. Leave it out when you cannot name a plausible answer. For a contradiction, give both places under **Where** and both quotes.

End with:

- **Checked and complete** — the areas from step 2 that need no question.
- **Not reviewed** — any document or link you could not open.
