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
4. creates the Python virtual environment and installs ontology/test dependencies;
5. installs frontend dependencies without generating a package lock;
6. fetches Rust dependencies;
7. installs the MCP pre-push Git hook;
8. runs the full MCP audit.

## Private evidence vault

The source-data root is:

```text
/workspaces/.mcp-private/sovereignCritical/
  incoming/
  originals/
  normalized/
  quarantine/
  exports/
  backups/
  audit/
  manifest/
```

The repository exposes this as `.mcp-data`, but `.mcp-data` is Git-ignored and must never be committed.

Files under `/workspaces` survive normal stop/start operations and container rebuilds, but deletion of the Codespace deletes its private data. Therefore the Codespace is a working evidence vault, not the sole long-term copy of an institutional record.

## Artifact intake

Put a source document in the private `incoming/` directory, then run:

```bash
bash scripts/intake-artifact.sh <file> <type> [issuer] [effective-date]
```

Example:

```bash
bash scripts/intake-artifact.sh \
  .mcp-data/incoming/PHIL-syllabus.pdf \
  syllabus \
  "University/instructor" \
  2026-08-24
```

The intake command:

- calculates SHA-256;
- derives an immutable artifact ID from the hash;
- preserves the original bytes in `originals/<year>/<artifact-id>/`;
- writes private metadata;
- appends one idempotent JSONL manifest entry;
- classifies the artifact as `Evidence Located` only;
- never promotes parser output or filename interpretation to verified truth.

Recommended artifact types for the first source bundle:

```text
transcript
degree-audit
fall-2026-registration
syllabus
financial-aid-award
financial-aid-status
federal-loan-status
rehabilitation-status
scholarship-record
scholarship-application
scholarship-award
```

## Data readiness

Run:

```bash
python scripts/data-readiness.py
```

or:

```bash
python scripts/data-readiness.py --json
```

The readiness report checks presence of the core private source bundle. Presence is not verification. Syllabi must later be reconciled against active registration so the system can detect a missing course syllabus instead of congratulating itself after finding one PDF.

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
- `Application CI` runs only when application-relevant paths change.

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
6. private intake is idempotent;
7. private source paths remain untracked;
8. the only unresolved truth gaps are missing source artifacts or facts that genuinely require those artifacts.
