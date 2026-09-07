"""
gantt_ontology
==============
Canonical Gantt Parameterization Ontology.

Clean, schema-driven models for:
- Task / Activity parameters
- Dependency parameters
- Resource parameters
- Structural Layout (Swimlane / Track / Boundary)
- Visual / Rendering parameters
- Scheduling Engine parameters
- Ontology / Metadata parameters

No data absorption, no import logic.
Serialization / deserialization and validation only.
"""

from .models import (
    Meta,
    Project,
    Calendar,
    Resource,
    Workstream,
    Task,
    Dependency,
    Baseline,
    Boundary,
    ConfigurationProfile,
    GanttOntology,
    Duration,
    DurationUnit,
    ConstraintType,
    DependencyType,
    ResourceType,
    SchedulingMode,
    BoundaryType,
    WorkstreamType,
    InvariantItem,
    AcademicStandingItem,
    CareerMilestoneItem,
    FundingItem,
    DemographicsProfile,
)

__version__ = "1.0.0"
__all__ = [
    "Meta",
    "Project",
    "Calendar",
    "Resource",
    "Workstream",
    "Task",
    "Dependency",
    "Baseline",
    "Boundary",
    "ConfigurationProfile",
    "GanttOntology",
    "Duration",
    "DurationUnit",
    "ConstraintType",
    "DependencyType",
    "ResourceType",
    "SchedulingMode",
    "BoundaryType",
    "WorkstreamType",
    "InvariantItem",
    "AcademicStandingItem",
    "CareerMilestoneItem",
    "FundingItem",
    "DemographicsProfile",
]
