# Spec Hawk — Review Checklist (inline-fallback copy)

Used by SKILL.md Step 2 when the dedicated reviewer is unavailable.
**Keep the marked contract exactly synchronized with `agents/automation-qa-reviewer.md`; each artifact is independently installable.**

<!-- BEGIN SHARED REVIEW CONTRACT -->

## Discovery before review

Repo-agnostic: do not assume folder names, tag names, shared-package names, or config conventions — discover them first.

1. Read `package.json` — project name, test runner, schema lib (Zod/Yup/etc.), any in-house shared package.
2. Find the config/constants module (e.g. `globalVariables.ts`, `config/`, `constants.ts`) — how env values, base URLs, and test-management IDs (TestRail section IDs, etc.) are sourced.
3. If present, read the linter config (`biome.json`, `.eslintrc*`) and root `CLAUDE.md` / `README` for repo conventions.
4. Search file paths to confirm the test layout — commonly `testCases/` (or `tests/`, `e2e/`) for specs and a `supports/` (or `helpers/`, `lib/`) area split into services / models / utils. Learn the repo's actual names; the checklist uses common names as examples only.

Ground every finding in the repo's actual conventions, not in these examples.

## Review checklist

Each finding must include the relevant checklist number. Where an item names a specific folder, tag, or package, treat it as the *common convention* — substitute whatever the active repo actually uses (per Discovery).

### 1. Layout & structure
- Test files (`*.spec.ts`) live under the repo's spec folder, grouped by domain/feature, and the domain matches an existing folder in the repo.
- Business logic / HTTP / DB access lives in a services layer, types in a models layer, helpers in a utils layer. Test files call into these layers, not inline the logic.
- File size ≤ 300 lines. Flag larger files with concrete split suggestions ("split by endpoint group", "extract assertions helper", etc.).

### 2. Tagging & test-management
- If the repo uses tags, every `test(...)` title carries one priority tag (e.g. `@smoke`, `@regression`, `@critical`, `@high`, `@low`) AND one domain/area tag, following the repo's tag scheme.
- Test-management IDs (TestRail section IDs, etc.) come from the repo's config/constants module — never hardcoded numbers.
- If the suite reports to a test-management system, the reporting hook (e.g. a `test.afterAll` annotation) is present.

### 3. Schema & assertions
- Response bodies are validated with the repo's schema lib (Zod or equivalent) — not only `expect(status).toBe(200)`.
- Negative-path coverage present: at least one 4xx or 5xx scenario per endpoint.
- No leftover `console.log`.

### 4. Code quality
- No in-place object mutation — copies are returned/spread instead.
- No hardcoded secrets, API keys, bearer tokens, or endpoint URLs. Must come from env + per-environment config.
- Reuse the repo's shared helpers/package (decimals, HTTP, db, secrets) rather than reimplementing.
- Test isolation: no shared mutable state across tests.

### 5. Linting / formatting
- Spot obvious style issues: unused imports, mixed indentation, double-spacing. Do not run the linter — note that the repo's check command (e.g. `npm run check`/`lint`) should be run.

### 6. Naming conventions
- `test.describe(...)`: `"<Feature in Title Case> - <Suite type>"`
  - Good: `"Get wallet addresses - Business"`, `"Post merchants - Validation"`
- `test(...)` title: must convey **four pieces of meaning** — HTTP method, path, expected outcome, and the condition / scenario. Punctuation and phrasing are flexible as long as a reader can extract `method`, `path`, `outcome`, and `when <condition>` from the title.
  - Good (any of these): `"GET [/v1/addresses/{{:wallet_address}}] response [failed] when API key is not exist"`, `"GET /v1/addresses response failed when API key is missing"`, `"GET: /v1/addresses → 401 when API key is missing"`
  - Bad: `"test wallet"`, `"check unauthorized"`, `"happy path"` — missing one or more of method / path / outcome / condition, so unreadable in a CI report.
  - Flag only when a piece of meaning is missing or ambiguous, not when punctuation differs from any single example.
- `test.step(...)`: `"<Action phrase> > should <expected behavior>"`
  - Good: `"Call GET wallet addresses > should be able to call API"`, `"Verify API Response > should be equal 401 Unauthorized and error response api key is unauthorized"`
- Reader test: a teammate seeing only the test title in a CI report should know *what endpoint, what outcome, and under what condition*.

### 7. Duplication & reuse opportunities
- For each helper / inline logic in the target, search sibling files under the services / utils / models layers for similar implementations.
- Also check whether the repo's shared package already exports the same thing (search its `node_modules/<package>/` if present).
- Watch especially for: HTTP request boilerplate, decimal math, db/cache access, schema/type definitions duplicated across models.
- Report as: `"Function X here duplicates <path>:<line>. Suggest reuse via …"`.

### 8. Function complexity & readability
Each function should do **one clear thing** that a teammate can understand from its name and signature without reading the body. Smells:

- **Length** — roughly more than 40–50 lines, especially with multiple sections doing different things. Suggest extracting helpers named after each section's intent.
- **Deep nesting** — more than 2–3 levels of `if` / `for` / `try`. Suggest early returns / guard clauses, or extracting the inner block.
- **Too many parameters** — more than ~4 positional args, or several behavior-changing boolean flags. Suggest an options object, splitting the function, or separating the variant paths.
- **Mixed abstraction levels** — high-level orchestration next to low-level details (e.g. building an HTTP request inline next to business assertions). Suggest extracting the low-level part into the services / utils layer.
- **Magic numbers / strings** — `if (status === 401)`, `setTimeout(fn, 3000)` etc. without a named constant or shared lookup. Suggest naming the value or pulling it from a shared constants module / config.
- **Unclear naming** — `data`, `result`, `tmp`, `doStuff()`, `process()`. Suggest intent-revealing names tied to the test step they support.
- **Doing more than one thing** — a name using "and", or a body with a clear seam (setup + call + verify in one helper). Suggest splitting along the seam.

**Reader test:** would a teammate seeing this function for the first time understand *what it does* and *why* without scrolling, mental-modeling, or asking? The numbers are guides — flag readability problems even in short functions; don't flag long functions that are genuinely linear and easy to follow.

These findings typically land at **MEDIUM** (refactor needed for maintainability) or **LOW** (minor smell). Use **HIGH** only when the complexity makes the test behavior actually ambiguous (e.g. a deeply-nested branch hides a missing assertion).

### 9. Race-prone shared test data (parallel workers)
Checks whether the config runs multiple workers or `fullyParallel: true` — if so, tests in different files can execute concurrently and collide on shared external state (DB rows, wallet addresses, merchant IDs, emails). This class of bug is invisible in a single-test run and only shows up under full-suite/regression runs — "passes alone, flakes in CI" is the signature symptom. Do not wave this off as flakiness; trace it to a concrete collision before dismissing it.

- Check the runner config (`playwright.config.ts` or equivalent) for `fullyParallel: true` or `workers > 1`. If the suite is forced fully serial (`workers: 1`, no `fullyParallel`), this check is low-priority — note it and move on.
- Otherwise, search across all spec files in the reviewed folder (and, budget permitting, the wider `testCases/` tree) for the same hardcoded literal used as the *target of a create/update/delete* — a fixed env var (`ENV.WALLET_ADDRESS_*`, `ENV.MERCHANT_ID_*`), a literal address/email/ID, or a fixture field reused as a unique key.
- Flag when the same literal appears in **two or more spec files** AND at least one of those tests creates, deletes, or mutates the record behind it (`afterEach`/`afterAll` cleanup, a duplicate-detection test doing create-then-create-again, an update-then-verify sequence). Two workers touching the same identifier concurrently is a real race, not a hypothetical — flag it even if the current diff's tests are currently green.
- Report the exact colliding locations: every `file:line` where the literal is used to create/mutate, so the user can see the collision pair, not just one side.
- Suggested fix: give each spec file (or each test that persists data) its own dedicated identifier/address/ID pulled from config, so no two concurrently-runnable tests target the same external record. Cross-file serialization (`test.describe.configure({ mode: "serial" })` is file-scoped only) is a fallback, not the first suggestion — it slows the whole suite down for one collision.
- Severity: **CRITICAL** — this is "broken isolation that contaminates other tests" per the severity table, even though it manifests as intermittent rather than deterministic failure.

## Severity definitions

| Level | Use when |
|---|---|
| **CRITICAL** | Test will give a false pass/fail; security or secret leak; broken isolation that contaminates other tests |
| **HIGH** | Missing test-management wiring, missing schema validation, no negative-path coverage, hardcoded endpoints / secrets |
| **MEDIUM** | Wrong folder/layer, file > 300 lines, weak assertion, duplicated logic that belongs in the services layer |
| **LOW** | Missing tag, missing import from the shared package, formatting issues the linter would catch |
| **NIT** | Naming, comment wording, minor readability |

## Output format

Return exactly one markdown report with this structure. Omit any severity section that has no findings.

````
## automation-qa-reviewer — review of <target>

**Summary:** <one or two sentences: overall health + biggest concern>

### CRITICAL
- **<file>:<line>** — [checklist #N] <problem>
  Suggested:
  ```ts
  <code snippet showing the fix>
  ```

### HIGH
- **<file>:<line>** — [checklist #N] <problem>
  Suggested: <snippet or short instruction>

### MEDIUM
- ...

### LOW
- ...

### NIT
- ...
````

<!-- END SHARED REVIEW CONTRACT -->
