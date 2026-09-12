#!/usr/bin/env python3
"""Export the provenance-first Master Critical Path JSON Schema.

Run from the `gantt_ontology` directory after installing the package:

    python tools/export_mcp_schema.py

The generated schema is deterministic with respect to the installed Pydantic
model and is intended for adapters, desktop/mobile boundaries, and validation.
"""

from __future__ import annotations

import json
from pathlib import Path

from gantt_ontology.mcp_domain import MCPDomainEnvelope


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "schema" / "mcp_domain_schema.json"


def main() -> None:
    schema = MCPDomainEnvelope.model_json_schema(by_alias=True)
    OUT.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
