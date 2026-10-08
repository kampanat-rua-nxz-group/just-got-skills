---
name: spec-to-qa
description: Use when deriving or reviewing QA scenarios from product designs, API specifications, sequence diagrams, or related requirements documents.
---

# Spec to QA

Turn supplied product and technical documents into evidence-traceable QA scenarios. Use independent analysis to broaden coverage and structured debate to resolve a specific uncertainty. The source documents remain authoritative; model agreement is not proof.

## Workflow

1. **Resolve the evidence.** Identify the provided design, API spec, sequence diagrams, acceptance criteria, and related references. Read the relevant project instructions and existing QA conventions. Search only as needed to resolve references. Record document names, versions or dates when available.
2. **Build a shared flow model.** Identify actors, services, endpoints, request/response fields, state transitions, dependencies, success paths, failure paths, retries, callbacks, and ownership boundaries. Trace each statement to a document section, diagram step, endpoint, or field. Keep explicit requirements separate from inference and unknowns.
3. **Choose the review mode.**
   - Use **independent opinions** for broad scenario discovery, coverage review, or separate readings of a flow. Each pass should analyze the same evidence independently before seeing other responses.
   - Use **debate** for a focused ambiguity or decision with at least two plausible interpretations. Start with independent positions, expose the evidence and counterarguments, then capture each final position and what evidence would change it.
   - If the runtime provides Fusion Harness, `/fh-opinion` and `/fh-debate` are optional ways to run these modes. Otherwise use available agent/model capabilities, or perform clearly separated independent passes yourself. Do not claim multiple agents or models were used unless they were.
4. **Synthesize scenarios.** Merge duplicates while preserving distinct conditions and failure outcomes. Cover happy paths, field validation, business rules, state and idempotency, dependency failures, timeouts/retries, async callbacks, ordering, concurrency, authorization, and boundary values when applicable. Do not invent expected behavior to fill gaps.
5. **Report traceability and gaps.** For each scenario, include:
   - ID or concise title
   - Source reference(s)
   - Preconditions / test data
   - Action or request sequence
   - Expected result, only when specified
   - Type: explicit, inferred, or blocked by ambiguity
   - Priority or risk, when useful

   End with document conflicts, assumptions, unanswered questions, and suggested tests that would distinguish competing interpretations. Mark undocumented expected results as `TBD` and identify the decision owner when the documents indicate one.
6. **Choose the deliverable with the user’s conventions.** Provide a concise review in chat unless asked to create an artifact. If the user wants a use-case mind map, use `usecase-map` for its established taxonomy and output format. Do not write into the project or create TestRail/Jira items unless asked.

## Evidence and safety rules

- Cite precise source locations where possible: filename plus heading, endpoint/field, or sequence step. For code-backed claims, include file and line.
- Label interpretation as inference. If sources conflict, show both references and leave the expected result unresolved until clarified.
- Keep separate models’ positions visible when disagreement matters; do not turn a majority vote into a requirement.
- Use read-only inspection for document analysis. Do not edit source documents, implementation, tests, or external systems as part of scenario discovery.
- For security, payment, balance, or other high-impact flows, use the documents to expose risks, then require QA/domain-owner review before accepting inferred behavior.

## Prompt patterns

**Independent review:**

> From the supplied design, API spec, and sequence diagrams, derive QA scenarios for `<flow>`. Cite each scenario to its source. Separate explicit requirements, inference, and TBD behavior. Include preconditions, action sequence, expected result where specified, and risk. Identify document conflicts and uncovered branches. Do not modify files.

**Focused debate:**

> The documents differ on `<behavior>`: `<source A says ...>` and `<source B says ...>`. Compare the evidence and plausible interpretations. State what QA can assert now, what remains TBD, and the smallest test or clarification that would distinguish the interpretations. Preserve each final position; do not invent a consensus.
