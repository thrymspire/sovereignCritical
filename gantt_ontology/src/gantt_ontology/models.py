"""
Canonical Pydantic models mirroring gantt_ontology_schema.json.

All fields are optional unless required by the schema.
No business logic, no scheduling engine, no data import.
Pure structure + validation + serialization.
"""

from __future__ import annotations

from datetime import date as Date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class DurationUnit(str, Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"


class ConstraintType(str, Enum):
    AS_SOON_AS_POSSIBLE = "AsSoonAsPossible"
    AS_LATE_AS_POSSIBLE = "AsLateAsPossible"
    MUST_START_ON = "MustStartOn"
    MUST_FINISH_ON = "MustFinishOn"
    START_NO_EARLIER_THAN = "StartNoEarlierThan"
    START_NO_LATER_THAN = "StartNoLaterThan"
    FINISH_NO_EARLIER_THAN = "FinishNoEarlierThan"
    FINISH_NO_LATER_THAN = "FinishNoLaterThan"


class DependencyType(str, Enum):
    FS = "FS"  # Finish-to-Start
    SS = "SS"  # Start-to-Start
    FF = "FF"  # Finish-to-Finish
    SF = "SF"  # Start-to-Finish


class ResourceType(str, Enum):
    WORK = "Work"
    MATERIAL = "Material"
    COST = "Cost"


class SchedulingMode(str, Enum):
    AUTO = "Auto"
    MANUAL = "Manual"
    HYBRID = "Hybrid"


class BoundaryType(str, Enum):
    PROJECT = "ProjectBoundary"
    PHASE = "PhaseBoundary"
    SPRINT = "SprintBoundary"
    TIME = "TimeBoundary"
    SCOPE = "ScopeBoundary"
    CONSTRAINT = "ConstraintBoundary"
    CUTLINE = "Cutline"


class WorkstreamType(str, Enum):
    SWIMLANE = "Swimlane"
    FUNCTIONAL = "FunctionalLane"
    ORGANIZATIONAL = "OrganizationalLane"
    PHASE = "PhaseLane"
    BAND = "Band"
    TRACK = "Track"


class CostAccrual(str, Enum):
    START = "Start"
    PRORATED = "Prorated"
    END = "End"


class Timescale(str, Enum):
    HOUR = "Hour"
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"
    QUARTER = "Quarter"
    YEAR = "Year"


class DayOfWeek(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


# ---------------------------------------------------------------------------
# Shared value objects
# ---------------------------------------------------------------------------

class Duration(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    value: float
    unit: DurationUnit


class WorkingTimeSlot(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    day_of_week: DayOfWeek = Field(alias="dayOfWeek")
    start: str  # HH:MM
    end: str


class NonWorkingPeriod(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    date: Date
    name: Optional[str] = None
    is_holiday: bool = Field(default=False, alias="isHoliday")


class ResourceAvailability(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_date: Date = Field(alias="from")
    to_date: Date = Field(alias="to")
    units: float


class ResourceAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    resource_id: str = Field(alias="resourceId")
    units: Optional[float] = None
    cost: Optional[float] = None


class TaskBaselineEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    task_id: str = Field(alias="taskId")
    start: Optional[Date] = None
    finish: Optional[Date] = None
    duration: Optional[Duration] = None


# ---------------------------------------------------------------------------
# Core ontology classes
# ---------------------------------------------------------------------------

class Meta(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: str = Field(default="1.0.0", alias="schemaVersion")
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    tenant_id: Optional[str] = Field(default=None, alias="tenantId")
    parameter_set_id: Optional[str] = Field(default=None, alias="parameterSetId")
    data_dictionary_version: Optional[str] = Field(default=None, alias="dataDictionaryVersion")
    validation_rules_version: Optional[str] = Field(default=None, alias="validationRulesVersion")


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    start_date: Optional[Date] = Field(default=None, alias="startDate")
    finish_date: Optional[Date] = Field(default=None, alias="finishDate")
    calendar_id: Optional[str] = Field(default=None, alias="calendarId")
    scheduling_mode: Optional[SchedulingMode] = Field(default=None, alias="schedulingMode")
    priority: Optional[int] = Field(default=None, ge=0, le=1000)
    wbs_root: Optional[str] = Field(default=None, alias="wbsRoot")


class Calendar(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    name: str
    working_time: List[WorkingTimeSlot] = Field(default_factory=list, alias="workingTime")
    non_working_time: List[NonWorkingPeriod] = Field(default_factory=list, alias="nonWorkingTime")
    resource_calendar: bool = Field(default=False, alias="resourceCalendar")
    task_calendar: bool = Field(default=False, alias="taskCalendar")


class Resource(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    name: str
    type: ResourceType
    resource_pool: Optional[str] = Field(default=None, alias="resourcePool")
    calendar_id: Optional[str] = Field(default=None, alias="calendarId")
    availability: List[ResourceAvailability] = Field(default_factory=list)
    capacity: Optional[float] = None
    cost_rate: Optional[float] = Field(default=None, alias="costRate")
    cost_accrual: Optional[CostAccrual] = Field(default=None, alias="costAccrual")
    max_units: Optional[float] = Field(default=None, alias="maxUnits")


class Workstream(BaseModel):
    """
    Structural layout container.
    Covers Swimlane, Workstream, Functional/Organizational/Phase Lane, Band, Track.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    type: WorkstreamType = WorkstreamType.SWIMLANE
    order: Optional[int] = None
    parent_workstream_id: Optional[str] = Field(default=None, alias="parentWorkstreamId")
    color: Optional[str] = None
    collapsed: bool = False


class Task(BaseModel):
    """
    Full Task / Activity / Work Package / Summary Task / Milestone parameter set.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    wbs_code: Optional[str] = Field(default=None, alias="wbsCode")
    wbs_level: Optional[int] = Field(default=None, alias="wbsLevel", ge=0)
    parent_task_id: Optional[str] = Field(default=None, alias="parentTaskId")
    is_summary: bool = Field(default=False, alias="isSummary")
    is_milestone: bool = Field(default=False, alias="isMilestone")
    workstream_id: Optional[str] = Field(default=None, alias="workstreamId")
    track_id: Optional[str] = Field(default=None, alias="trackId")

    # Temporal parameters
    start_date: Optional[Date] = Field(default=None, alias="startDate")
    finish_date: Optional[Date] = Field(default=None, alias="finishDate")
    duration: Optional[Duration] = None
    effort: Optional[Duration] = None
    workload: Optional[float] = None
    percent_complete: Optional[float] = Field(default=None, alias="percentComplete", ge=0, le=100)
    remaining_duration: Optional[Duration] = Field(default=None, alias="remainingDuration")

    actual_start: Optional[Date] = Field(default=None, alias="actualStart")
    actual_finish: Optional[Date] = Field(default=None, alias="actualFinish")
    baseline_start: Optional[Date] = Field(default=None, alias="baselineStart")
    baseline_finish: Optional[Date] = Field(default=None, alias="baselineFinish")
    baseline_duration: Optional[Duration] = Field(default=None, alias="baselineDuration")

    # Constraints
    constraint_type: Optional[ConstraintType] = Field(default=None, alias="constraintType")
    constraint_date: Optional[Date] = Field(default=None, alias="constraintDate")

    priority: Optional[int] = Field(default=None, ge=0, le=1000)
    critical_path_membership: Optional[bool] = Field(default=None, alias="criticalPathMembership")
    total_float: Optional[Duration] = Field(default=None, alias="totalFloat")
    free_float: Optional[Duration] = Field(default=None, alias="freeFloat")

    assignments: List[ResourceAssignment] = Field(default_factory=list)
    calendar_id: Optional[str] = Field(default=None, alias="calendarId")
    manual: bool = False
    notes: Optional[str] = None


class Dependency(BaseModel):
    """
    Predecessor / Successor relationship with type, lag, lead, criticality.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    predecessor_id: str = Field(alias="predecessorId")
    successor_id: str = Field(alias="successorId")
    type: DependencyType
    lag: Optional[Duration] = None
    lead: Optional[Duration] = None
    is_critical: Optional[bool] = Field(default=None, alias="isCritical")


class Baseline(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    name: str
    captured_at: Optional[datetime] = Field(default=None, alias="capturedAt")
    task_baselines: List[TaskBaselineEntry] = Field(default_factory=list, alias="taskBaselines")


class Boundary(BaseModel):
    """
    Project / Phase / Sprint / Time / Scope / Constraint boundaries + Cutline.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    type: BoundaryType
    name: Optional[str] = None
    date: Optional[Date] = None          # for Cutline or single-date boundaries
    start_date: Optional[Date] = Field(default=None, alias="startDate")
    finish_date: Optional[Date] = Field(default=None, alias="finishDate")
    color: Optional[str] = None
    style: Optional[str] = None


# ---------------------------------------------------------------------------
# Demographics & Invariants value objects
# ---------------------------------------------------------------------------

class InvariantItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    label: str
    value: str
    detail: Optional[str] = None


class AcademicStandingItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    label: str
    value: str


class CareerMilestoneItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    milestone: str
    detail: str


class FundingItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    provider: str
    type: Optional[str] = None
    term: Optional[str] = None
    amount: float
    action: Optional[str] = None
    link: Optional[str] = None
    secured: bool = False


class DemographicsProfile(BaseModel):
    """
    Normalized empirical invariants, academic standing audit,
    career milestone arc, and funding pipeline opportunities.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    invariants: List[InvariantItem] = Field(default_factory=list)
    academic_standing: List[AcademicStandingItem] = Field(default_factory=list, alias="academicStanding")
    career_arc: List[CareerMilestoneItem] = Field(default_factory=list, alias="careerArc")
    funding: List[FundingItem] = Field(default_factory=list)


class ConfigurationProfile(BaseModel):
    """
    Tenant / Parameter-Set level configuration.
    Holds visual, layout, scheduling, and rule metadata.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: Optional[str] = None
    name: Optional[str] = None
    tenant_id: Optional[str] = Field(default=None, alias="tenantId")

    scheduling: Optional[dict] = None
    visual: Optional[dict] = None
    layout: Optional[dict] = None
    validation_rules: List[str] = Field(default_factory=list, alias="validationRules")
    constraint_rules: List[str] = Field(default_factory=list, alias="constraintRules")
    scheduling_rules: List[str] = Field(default_factory=list, alias="schedulingRules")
    demographics: Optional[DemographicsProfile] = None


# ---------------------------------------------------------------------------
# Root document
# ---------------------------------------------------------------------------

class GanttOntology(BaseModel):
    """
    Root canonical document.
    This is the shape that all future data must be normalized into.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    meta: Meta
    project: Project
    calendars: List[Calendar] = Field(default_factory=list)
    resources: List[Resource] = Field(default_factory=list)
    workstreams: List[Workstream] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    dependencies: List[Dependency] = Field(default_factory=list)
    baselines: List[Baseline] = Field(default_factory=list)
    boundaries: List[Boundary] = Field(default_factory=list)
    configuration: Optional[ConfigurationProfile] = None
    demographics: Optional[DemographicsProfile] = None

    def to_canonical_dict(self) -> dict:
        """Serialize to plain dict using camelCase aliases (schema form)."""
        return self.model_dump(by_alias=True, exclude_none=True, mode="json")

    @classmethod
    def from_canonical_dict(cls, data: dict) -> "GanttOntology":
        """Deserialize from a dict that already conforms to the schema."""
        return cls.model_validate(data)
