# Gantt Ontology — Canonical Parameterization Schema & Codebase

**Role:** Ontology Engineer  
**Mandate:** Parameterization · Soft-coding · Externalization · Metadata-Driven Architecture · Data-Driven Scheduling · Program–Data Independence · Schema-Driven Rendering · Configuration-Driven Execution · Multi-Tenant Abstraction · Dynamic Binding · Runtime Injection · Decoupled Logic and Core Task Parameters

This package contains **only**:
1. A separate **schema** (`schema/gantt_ontology_schema.json`)
2. A clean **codebase** of Pydantic models that mirror the schema exactly

**Explicitly absent (as required):**
- No import features
- No data absorption / ETL
- No mapping pipelines
- No hard-coded project data
- No coupling to any existing Master Critical Path HTML, CSV, or generator

Data absorption happens later. This is the target shape only.

---

## Layout

```
gantt_ontology_clean/
├── schema/
│   └── gantt_ontology_schema.json   ← authoritative canonical schema
├── src/
│   └── gantt_ontology/
│       ├── __init__.py
│       └── models.py                ← Pydantic models (serialization + validation)
├── pyproject.toml
└── README.md
```

---

## What the Schema / Models Cover

### Task / Activity Parameters
Task, Work Package, Subtask, Summary Task, Milestone  
Start Date, Finish Date, Duration, Effort, Workload, Percent Complete, Remaining Duration  
Actual Start / Finish, Baseline Start / Finish / Duration  
Constraint Type (Must Start On, Must Finish On, Start No Earlier Than, Finish No Later Than, As Soon As Possible, As Late As Possible)

### Dependency Parameters
Predecessor, Successor, Dependency Type (FS / SS / FF / SF), Lag, Lead  
Dependency Chain, Critical Path Membership, Slack / Float (Free Float, Total Float)

### Resource Parameters
Resource, Resource Pool, Resource Assignment, Resource Calendar  
Availability, Capacity, Allocation, Cost Rate, Cost Accrual  
Material Resource, Work Resource

### Structural Layout Parameters
Swimlane / Workstream / Functional Lane / Organizational Lane / Phase Lane / Band  
Track / Row / Timeline Row / Resource Track / Parallel Track  
Boundary (Project, Phase, Sprint, Time, Scope, Constraint, Cutline)  
Grouping (Hierarchy, Parent/Child, Grouping Rule, Sorting Rule, WBS Code, WBS Level)

### Visual / Rendering Parameters
Bar Style / Color / Shape, Milestone Marker, Progress Fill, Gridlines  
Timescale, Zoom Level, Calendar Format, Non-Working Time Shading  
Baseline Overlay, Critical Path Highlighting, Dependency Line Style

### Scheduling Engine Parameters
Auto-Scheduling, Manual Scheduling, Calendar, Working / Non-Working Time, Holidays  
Resource Calendars, Task Calendars, Scheduling Mode, Leveling Delay, Resource Leveling  
Priority, Critical Chain Buffer, Feeding Buffer

### Ontology / Metadata Parameters
**Classes:** Task, Milestone, Workstream, Resource, Dependency, Constraint, Boundary, Calendar, Baseline  
**Object Properties:** dependsOn, hasPredecessor, hasSuccessor, assignedTo, belongsToWorkstream, hasBoundary, hasConstraint, hasCalendar  
**Data Properties:** hasStartDate, hasFinishDate, hasDuration, hasPercentComplete, hasLag, hasLead, hasSlack, hasCost, hasPriority  
**Metadata:** Schema, Parameter Set, Configuration Profile, Tenant Profile, Data Dictionary, Validation Rules, Constraint Rules, Scheduling Rules

---

## Usage (shape data to this later)

```python
from gantt_ontology import GanttOntology, Meta, Project, Task, Dependency
from datetime import datetime, date

# This is the only shape future data should be normalized into.
doc = GanttOntology(
    meta=Meta(createdAt=datetime.utcnow()),
    project=Project(id="...", name="..."),
    tasks=[...],
    dependencies=[...],
    # etc.
)

canonical = doc.to_canonical_dict()          # schema-conformant dict
restored  = GanttOntology.from_canonical_dict(canonical)
```

Install (optional):
```bash
pip install -e .
```

---

## Design Principles Applied

| Concept                        | How it is realized                                      |
|--------------------------------|---------------------------------------------------------|
| Normalization                  | Single canonical schema                                 |
| Schema Mapping target          | JSON Schema is the contract                             |
| Canonical Model Enforcement    | Pydantic + `extra="forbid"`                             |
| Program–Data Independence      | Zero domain data inside models                          |
| Soft-coding / Externalization  | Everything lives in schema or future data files         |
| Metadata-Driven                | Meta + ConfigurationProfile carry versioning and rules  |
| No import / absorption         | Deliberately omitted                                    |

This is the clean parameterization layer. Data absorption comes later.
