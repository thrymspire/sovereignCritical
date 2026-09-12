"""Deterministic adapter from the legacy Gantt document to MCP truth records.

The adapter does **not** decide that legacy values are true. It preserves the
legacy document as a source and emits field-level Tier-5 provisional assertions
with evidence locators back to the original document. That makes existing data
queryable and auditable while preventing migration code from laundering old
claims into authoritative state.

This module intentionally performs no web lookup, no institutional inference,
and no destructive normalization.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Any, Iterable, Iterator, Tuple

from .mcp_domain import (
    Assertion,
    AuthorityTier,
    ClaimType,
    Evidence,
    MCPDomainEnvelope,
    Source,
    SourceKind,
    VerificationState,
)


DEFAULT_LEGACY_GRAPH_REF = "data/gantt_ontology.json"
DEFAULT_REPOSITORY_URI = "git@github.com:thrymspire/sovereignCritical.git"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def legacy_document_sha256(document: dict[str, Any]) -> str:
    """Return a deterministic content hash for the parsed legacy document.

    This is a normalized-document hash, not a claim about the exact source-file
    byte hash. Import pipelines that possess the raw artifact should retain the
    raw SHA-256 separately in ``ImportArtifact``.
    """

    return hashlib.sha256(_canonical_json(document).encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9._:-]+", "-", value).strip("-")
    return result[:120] or "value"


def _stable_id(prefix: str, *parts: str) -> str:
    payload = "\x1f".join(parts)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}-{digest}"


def _iter_leaf_values(value: Any, path: str = "") -> Iterator[Tuple[str, Any]]:
    """Yield deterministic field-level values from nested JSON-compatible data.

    Dictionaries are recursively flattened. Lists are retained as one value
    because list ordering is usually semantically meaningful in the legacy
    schedule and exploding them would invent collection semantics not present
    in the source schema.
    """

    if isinstance(value, dict):
        for key in sorted(value):
            child_path = f"{path}.{key}" if path else str(key)
            yield from _iter_leaf_values(value[key], child_path)
        return

    if path:
        yield path, value


def _record_subject(collection: str, record: dict[str, Any], index: int) -> str:
    record_id = record.get("id")
    if record_id is not None:
        return f"legacy:{_slug(collection)}:{_slug(str(record_id))}"
    return f"legacy:{_slug(collection)}:index-{index}"


def _iter_legacy_records(document: dict[str, Any]) -> Iterable[tuple[str, str, dict[str, Any]]]:
    """Yield (collection, subject_id, record) in deterministic order."""

    # Singleton records first.
    for key in ("meta", "project", "configuration", "demographics"):
        value = document.get(key)
        if isinstance(value, dict):
            subject = f"legacy:{_slug(key)}:{_slug(str(value.get('id', 'document')))}"
            yield key, subject, value

    # Canonical legacy collections. Unknown top-level arrays are deliberately
    # included too, so later schema extensions are preserved rather than lost.
    handled = {"meta", "project", "configuration", "demographics"}
    for key in sorted(document):
        if key in handled:
            continue
        value = document[key]
        if not isinstance(value, list):
            continue
        for index, item in enumerate(value):
            if isinstance(item, dict):
                yield key, _record_subject(key, item, index), item
            else:
                # Preserve primitive collection values as synthetic records.
                yield key, f"legacy:{_slug(key)}:index-{index}", {"value": item}


def legacy_gantt_to_mcp_envelope(
    document: dict[str, Any],
    *,
    acquired_at: datetime,
    repository_uri: str = DEFAULT_REPOSITORY_URI,
    legacy_graph_ref: str = DEFAULT_LEGACY_GRAPH_REF,
    source_title: str = "Legacy Master Critical Path canonical Gantt document",
    source_version: str | None = None,
) -> MCPDomainEnvelope:
    """Wrap all legacy fields as provenance-backed provisional assertions.

    The same document and metadata produce stable source/evidence/assertion IDs.
    ``acquired_at`` is deliberately supplied by the caller because acquisition
    time is an event, not a deterministic property of source content.
    """

    normalized_sha256 = legacy_document_sha256(document)
    source_id = f"source-legacy-{normalized_sha256[:20]}"

    source = Source(
        id=source_id,
        kind=SourceKind.LEGACY_REPOSITORY,
        authorityTier=AuthorityTier.TIER_5_PROVISIONAL,
        title=source_title,
        issuer="sovereignCritical repository",
        uri=repository_uri,
        acquiredAt=acquired_at,
        version=source_version,
        sha256=normalized_sha256,
        originalArtifactRef=legacy_graph_ref,
        notes=(
            "Normalized-document SHA-256. All assertions emitted from this source "
            "remain provisional until corroborated by stronger evidence."
        ),
    )

    evidence_records: list[Evidence] = []
    assertions: list[Assertion] = []

    for collection, subject_id, record in _iter_legacy_records(document):
        for field_path, value in _iter_leaf_values(record):
            locator = f"$.{collection}"
            record_id = record.get("id")
            if record_id is not None:
                locator += f"[id={record_id!s}]"
            locator += f".{field_path}"

            value_json = _canonical_json(value)
            assertion_id = _stable_id(
                "assertion-legacy",
                source_id,
                subject_id,
                field_path,
                value_json,
            )
            evidence_id = _stable_id("evidence-legacy", assertion_id, locator)

            evidence_records.append(
                Evidence(
                    id=evidence_id,
                    sourceId=source_id,
                    locator=locator,
                    capturedValue=value,
                    acquiredAt=acquired_at,
                    verificationState=VerificationState.EVIDENCE_LOCATED,
                    notes="Evidence of what the legacy repository claims, not proof that the claim is true.",
                )
            )
            assertions.append(
                Assertion(
                    id=assertion_id,
                    subjectId=subject_id,
                    predicate=field_path,
                    objectValue=value,
                    claimType=ClaimType.PROVISIONAL_ASSERTION,
                    authorityTier=AuthorityTier.TIER_5_PROVISIONAL,
                    verificationState=VerificationState.CLAIMED,
                    evidenceIds=[evidence_id],
                    confidence=0.0,
                    notes=(
                        "Imported verbatim from the legacy scheduling graph. "
                        "Must not be promoted without corroboration."
                    ),
                )
            )

    return MCPDomainEnvelope(
        createdAt=acquired_at,
        legacyGraphRef=legacy_graph_ref,
        sources=[source],
        evidence=evidence_records,
        assertions=assertions,
    )
