# Master Critical Path Codespace Operations

## Purpose

The Codespace is the reproducible engineering and evidence-intake workstation for Master Critical Path. It is not the authoritative archive by itself and it is not allowed to turn private source documents into public Git content.

## Branches

- Preserved baseline: `project-owners/master-critical-path-baseline-2026-09-12`
- Main implementation branch: `project-owners/master-critical-path-v1`
- Codespace staging branch: `project-owners/master-critical-path-codespace`

The baseline branch is immutable. The Codespace branch exists to validate workstation/bootstrap/audit infrastructure before the implementation branch is fast-forwarded to the proven configuration.

## Workstation creation

Create/open the Codespace from `project-owners/master-critical-path-codespace` while this staging branch is active. The repository dev container installs Node 24, Python 3.12, stable Rust, GitHub CLI, Tauri Linux build prerequisites, SQLite, PDF text tooling, ShellCheck, ripgrep, and normal archive utilities.

The `postCreateCommand` runs `scripts/codespace-bootstrap.sh`.

Bootstrap performs the following operations:

1. refuses to initialize on the wrong branch;
2. creates a private persistent vault under `/workspaces/.mcp-private/sovereignCritical`;
3. creates a local ignored `.mcp-data` symlink into that vault;
4. creates typed private drop-in folders;
5. creates the Python virtual environment and installs ontology/test dependencies;
6. installs frontend dependencies without generating a package lock;
7. fetches Rust dependencies;
8. installs the MCP pre-push Git hook;
9. runs the full MCP audit.

## Private evidence vault

The source-data root is:

```text
/workspaces/.mcp-private/sovereignCritical/
  incoming/
    transcripts/
    degree-audits/
    registration/
    syllabi/
    lms/
    financial-aid/
    loans/
    scholarships/
    university-account/
    transfer-credit/
    advisor-records/
    other/
  originals/
  normalized/
  quarantine/
  exports/
  backups/
  audit/
  manifest/
```

The repository exposes this same private root as `.mcp-data`, but `.mcp-data` is Git-ignored and must never be committed.

Files under `/workspaces` survive normal stop/start operations and container rebuilds, but deletion of the Codespace deletes its private data. Therefore the Codespace is a working evidence vault, not the sole long-term copy of an institutional record.

## Drop-in artifact intake

The preferred human workflow is to copy original files, unchanged, into the appropriate folder under:

```text
.mcp-data/incoming/
```

Then run one scanner:

```bash
python scripts/intake-dropbox.py
```

The scanner recursively finds the files, derives the artifact type from the first typed folder, and calls the content-addressed intake service. A file placed directly in `incoming/` or in an unknown folder is still preserved, but is classified as `unclassified` until later reconciliation.

Single-artifact intake remains available when an explicit issuer or known effective date needs to be supplied:

```bash
bash scripts/intake-artifact.sh <file> <type> [issuer] [effective-date]
```

The effective-date argument is optional. Normal drop-in operation does not require the operator to know or type a date.

The intake pipeline:

- calculates SHA-256;
- derives an immutable artifact ID from the hash;
- preserves the original bytes under content-addressed `originals/sha256/...` storage;
- keeps ingestion time separate from document/effective chronology;
- extracts conservative date candidates from exact dates in filenames, labelled document text, and embedded PDF/OOXML metadata;
- resolves a date only when a strong candidate is unambiguous;
- marks conflicting strong dates `ambiguous` and missing strong dates `unresolved`;
- never substitutes the current/ingestion date for an unresolved document date;
- writes private metadata and a date-resolution record;
- appends one idempotent JSONL manifest entry;
- classifies the artifact as `Evidence Located` only;
- never promotes parser output, filename interpretation, or extracted dates to institutionally verified truth.

## First source bundle

The first source bundle should be dropped into these private folders:

```text
transcripts/          current transcript, plus older transcript versions if they resolve history
degree-audits/        current degree audit/program evaluation
registration/         current Fall 2026 registration/enrollment record
syllabi/              every active Fall 2026 syllabus and every revision
lms/                   assignment/calendar/gradebook exports and authoritative deadline changes
financial-aid/         current award notice, aid status, SAP/eligibility notices
loans/                 StudentAid/servicer status, rehabilitation/deferment records when applicable
scholarships/          applications, criteria/rules, decisions, award/renewal records being relied upon
university-account/    current tuition/account statement, holds, disbursement/refund records
transfer-credit/       transfer-credit evaluations when they affect the degree path
advisor-records/       authoritative advisor/program records that change degree requirements or sequencing
other/                 anything relevant that does not fit the above yet
```

Prefer source PDFs/exports over screenshots when both exist. Keep original filenames and provide all revisions rather than replacing an older file. The hash and provenance model handles duplicates and supersession; humans should not have to perform archaeology before ingestion.

## Date reconciliation policy

Master Critical Path uses at least three separate time concepts:

- `ingestedAt`: when MCP received the bytes;
- `documentDate`: the best conservatively resolved date associated with the artifact;
- `effectiveDate`: only populated when the resolved semantic meaning is specifically an effective date.

Date candidates and their source/locator/confidence are retained under `dateResolution`. Artifact storage paths are content-addressed and therefore cannot imply a historical year merely because a file happened to be uploaded later.

This policy is intentionally conservative. Syllabus due dates, transaction dates, and dates mentioned in correspondence are not automatically treated as the artifact's document date. Ambiguity is state, not permission to guess.

## Data readiness

Run:

```bash
python scripts/data-readiness.py
```

or:

```bash
python scripts/data-readiness.py --json
```

The readiness report checks presence of the core private source bundle and reports unresolved/ambiguous artifact dates. Presence is not verification. Syllabi must later be reconciled against active registration so the system can detect a missing course syllabus instead of congratulating itself after finding one PDF.

## Live audit

Run a full local audit manually:

```bash
bash scripts/live-audit.sh --full
```

Every Git push from the Codespace runs the same full audit through the installed `pre-push` hook before network transfer. The audit includes:

- branch guard;
- whitespace integrity;
- private-artifact Git exclusion;
- repository contract presence;
- Python intake-tool compilation;
- idempotent artifact-intake and historical-date self-test;
- ShellCheck when available;
- ontology tests;
- strict legacy canonical validation;
- MCP schema generation and JSON-Schema validation;
- frontend production build;
- Tauri `cargo check`;
- clean-tree enforcement before push.

Remote GitHub Actions then provide an independent audit trail:

- `MCP Live Audit` runs on every working-branch push and stores its audit report as an Actions artifact;
- `Ontology CI` runs only when ontology-relevant paths change;
- `Application CI` runs only when application-relevant paths change;
- the Codespace workstation workflow builds the dev container itself so workstation reproducibility is verified rather than assumed.

This prevents a three-way full rebuild on every documentation edit while retaining independent server-side evidence for code changes.

## Push discipline

Normal sequence:

```bash
git status
git diff
git add <intentional files>
git commit -m "..."
git push
```

`git push` is deliberately the last step because the pre-push hook is a release gate, not a motivational poster.

Do not bypass the hook except to repair the hook itself, and document any bypass in the proof-of-work ledger.

## Source-data security rule

Never place private transcripts, financial-aid records, loan records, account statements, IDs, private correspondence, or raw institutional evidence inside the public Git repository.

Git may contain:

- schemas;
- hashes;
- artifact IDs;
- redacted fixtures;
- safe provenance metadata;
- public institutional rules;
- derived logic and tests.

The raw source bytes remain in the private evidence vault or another private archive.

## Current exit criterion

The workstation layer is ready when:

1. Codespace bootstrap succeeds;
2. local full audit is green;
3. live repository audit is green;
4. ontology CI is green when exercised;
5. application CI is green when exercised;
6. private intake is idempotent and content-addressed;
7. artifact chronology is separate from ingestion time and ambiguity is explicit;
8. private source paths remain untracked;
9. the only unresolved truth gaps are missing source artifacts or facts that genuinely require those artifacts.
