import { isTauri } from "@tauri-apps/api/core";
import {
  isPermissionGranted,
  requestPermission,
  sendNotification,
} from "@tauri-apps/plugin-notification";
import { useMemo, useState } from "react";

type SurfaceId =
  | "command"
  | "critical-path"
  | "swim-lanes"
  | "courses"
  | "scholarships"
  | "evidence"
  | "truth"
  | "changes";

type NavItem = {
  id: SurfaceId;
  label: string;
  glyph: string;
  description: string;
};

const NAV_ITEMS: NavItem[] = [
  {
    id: "command",
    label: "Command",
    glyph: "⌂",
    description: "Next actions, blockers, deadlines and risk",
  },
  {
    id: "critical-path",
    label: "Critical Path",
    glyph: "◇",
    description: "Dependency graph and controlling sequence",
  },
  {
    id: "swim-lanes",
    label: "Swim Lanes",
    glyph: "≡",
    description: "Responsibility domains and cross-lane contracts",
  },
  {
    id: "courses",
    label: "Courses",
    glyph: "▤",
    description: "Course offerings, syllabi, assignments and proof",
  },
  {
    id: "scholarships",
    label: "Scholarships",
    glyph: "◆",
    description: "Criteria, windows, paperwork and eligibility",
  },
  {
    id: "evidence",
    label: "Evidence",
    glyph: "▣",
    description: "Source artifacts and verification queue",
  },
  {
    id: "truth",
    label: "Truth",
    glyph: "◎",
    description: "Assertion provenance, contradiction and derivation",
  },
  {
    id: "changes",
    label: "Changes",
    glyph: "↻",
    description: "Audit history and proof of work",
  },
];

const SWIM_LANES = [
  "Academic",
  "Financial Aid / Funding",
  "Scholarships",
  "Personal Finance",
  "Employment",
  "Institutional Administration",
  "Documentation",
  "Transportation / Logistics",
  "Projects / Research",
  "Legal / Compliance",
  "Personal Operations",
] as const;

const WATERMARK =
  "MCP-WM/1.2 · baseline 9e15068d · phase ONTOLOGY-NORMALIZATION · drift 0";

function StatusPill({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "neutral" | "good" | "warning" | "critical" | "info";
}) {
  return <span className={`status-pill status-pill--${tone}`}>{children}</span>;
}

function MetricCard({
  eyebrow,
  value,
  note,
  tone = "neutral",
}: {
  eyebrow: string;
  value: string;
  note: string;
  tone?: "neutral" | "good" | "warning" | "critical" | "info";
}) {
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <p className="eyebrow">{eyebrow}</p>
      <strong>{value}</strong>
      <p>{note}</p>
    </article>
  );
}

function EmptyTruthState({ title, body }: { title: string; body: string }) {
  return (
    <div className="empty-state" role="status">
      <div className="empty-state__mark" aria-hidden="true">
        ◎
      </div>
      <div>
        <h3>{title}</h3>
        <p>{body}</p>
      </div>
    </div>
  );
}

function CommandSurface() {
  return (
    <>
      <section className="metric-grid" aria-label="Operational state">
        <MetricCard
          eyebrow="Critical path"
          value="Withheld"
          note="Not calculated from provisional legacy claims."
          tone="warning"
        />
        <MetricCard
          eyebrow="Evidence graph"
          value="Ready"
          note="Source → evidence → assertion lineage model is active."
          tone="good"
        />
        <MetricCard
          eyebrow="Legacy truth"
          value="Provisional"
          note="Existing repository fields import as Tier-5 claims."
          tone="info"
        />
        <MetricCard
          eyebrow="Contract execution"
          value="Guarded"
          note="High-impact uncertain effects require review."
          tone="neutral"
        />
      </section>

      <section className="workbench-grid">
        <article className="surface-card surface-card--wide">
          <header className="surface-card__header">
            <div>
              <p className="eyebrow">Next executable actions</p>
              <h2>Truth reconciliation before prioritization</h2>
            </div>
            <StatusPill tone="warning">EVIDENCE GATE</StatusPill>
          </header>
          <div className="action-row">
            <div className="action-index">01</div>
            <div>
              <h3>Ingest institutional records</h3>
              <p>
                Transcript, degree audit, course schedule and syllabi become immutable
                source artifacts before downstream academic/funding rules execute.
              </p>
            </div>
            <span className="action-state">Ready after file service</span>
          </div>
          <div className="action-row">
            <div className="action-index">02</div>
            <div>
              <h3>Resolve contradictory course identities</h3>
              <p>
                Preserve both legacy claim sets, then promote only the set supported by
                the applicable term registration record and syllabi.
              </p>
            </div>
            <span className="action-state">Blocked by evidence</span>
          </div>
          <div className="action-row">
            <div className="action-index">03</div>
            <div>
              <h3>Recalculate boundary contracts</h3>
              <p>
                Degree progress, funding, scholarship and notification consequences run
                only after their input assertions satisfy authority requirements.
              </p>
            </div>
            <span className="action-state">Waiting</span>
          </div>
        </article>

        <article className="surface-card">
          <header className="surface-card__header">
            <div>
              <p className="eyebrow">Truth controls</p>
              <h2>Promotion rules</h2>
            </div>
          </header>
          <dl className="definition-list">
            <div>
              <dt>Institutional fact</dt>
              <dd>Tier 1 + evidence required</dd>
            </div>
            <div>
              <dt>Derived fact</dt>
              <dd>Explicit source assertion lineage</dd>
            </div>
            <div>
              <dt>Legacy claim</dt>
              <dd>Tier 5 until corroborated</dd>
            </div>
            <div>
              <dt>Suggestion</dt>
              <dd>Never silently becomes truth</dd>
            </div>
          </dl>
        </article>
      </section>
    </>
  );
}

function CriticalPathSurface() {
  return (
    <section className="surface-card surface-card--fill">
      <header className="surface-card__header">
        <div>
          <p className="eyebrow">Dependency engine</p>
          <h2>Critical path is intentionally not rendered yet</h2>
        </div>
        <StatusPill tone="warning">TRUTH BLOCK</StatusPill>
      </header>
      <EmptyTruthState
        title="No authoritative controlling sequence yet"
        body="Rendering a critical path from contradictory course, funding and deadline claims would turn scheduling precision into false certainty. The graph surface is reserved and will activate when the evidence-aware rule engine has admissible inputs."
      />
    </section>
  );
}

function SwimLaneSurface() {
  return (
    <section className="surface-card surface-card--fill">
      <header className="surface-card__header">
        <div>
          <p className="eyebrow">Operational responsibility domains</p>
          <h2>Canonical swim lanes</h2>
        </div>
        <StatusPill tone="info">STRUCTURAL</StatusPill>
      </header>
      <div className="lane-list">
        {SWIM_LANES.map((lane, index) => (
          <article className="lane-row" key={lane}>
            <span className="lane-index">{String(index + 1).padStart(2, "0")}</span>
            <div>
              <h3>{lane}</h3>
              <p>Inbound/outbound contracts will appear here after rule migration.</p>
            </div>
            <StatusPill>Awaiting contracts</StatusPill>
          </article>
        ))}
      </div>
    </section>
  );
}

function CoursesSurface() {
  return (
    <section className="surface-card surface-card--fill">
      <header className="surface-card__header">
        <div>
          <p className="eyebrow">Academic ontology</p>
          <h2>Course + syllabus ingestion surface</h2>
        </div>
        <StatusPill tone="good">SCHEMA READY</StatusPill>
      </header>
      <div className="schema-grid">
        {[
          ["Course identity", "institution · code · section · term · modality · credits"],
          ["Instructor", "contact · office hours · communication expectations"],
          ["Assignments", "due time · points · weight · submission · rubric · proof"],
          ["Policies", "grading · attendance · late work · makeup · integrity"],
          ["Objectives", "learning outcomes linked to assignments and evidence"],
          ["Artifacts", "original syllabus preserved with field-level provenance"],
        ].map(([title, detail]) => (
          <article className="schema-tile" key={title}>
            <h3>{title}</h3>
            <p>{detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function ScholarshipSurface() {
  return (
    <section className="surface-card surface-card--fill">
      <header className="surface-card__header">
        <div>
          <p className="eyebrow">Funding ontology</p>
          <h2>Scholarship criteria are contracts, not sticky notes</h2>
        </div>
        <StatusPill tone="good">MODEL READY</StatusPill>
      </header>
      <div className="schema-grid">
        {[
          ["Eligibility", "GPA · enrollment · program · residency · sponsor rules"],
          ["Windows", "opening · priority · final deadlines kept distinct"],
          ["Paperwork", "transcript · schedule · invoice · essay · recommendations"],
          ["Award formula", "per-credit · term maximum · annual/lifetime maximum"],
          ["Derived state", "candidate eligibility · missing criteria · deadline risk"],
          ["Boundary effects", "award/denial can recalculate funding and task priority"],
        ].map(([title, detail]) => (
          <article className="schema-tile" key={title}>
            <h3>{title}</h3>
            <p>{detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function EvidenceSurface() {
  return (
    <section className="surface-card surface-card--fill">
      <header className="surface-card__header">
        <div>
          <p className="eyebrow">Proof of completion</p>
          <h2>Evidence queue</h2>
        </div>
        <StatusPill tone="warning">FILE SERVICE NEXT</StatusPill>
      </header>
      <EmptyTruthState
        title="No source artifacts loaded into the new runtime"
        body="The file service will preserve originals, hash artifacts, capture source metadata and attach field-level evidence. Legacy repository text is already importable as evidence of what the old graph claimed, not evidence that those claims were true."
      />
    </section>
  );
}

function TruthSurface() {
  return (
    <section className="surface-card surface-card--fill">
      <header className="surface-card__header">
        <div>
          <p className="eyebrow">Provenance inspector</p>
          <h2>Source → Evidence → Assertion → Effect</h2>
        </div>
        <StatusPill tone="good">INVARIANTS TESTED</StatusPill>
      </header>
      <div className="truth-chain" aria-label="Truth lineage pipeline">
        {[
          ["Source", "Authority tier + immutable artifact"],
          ["Evidence", "Field locator + captured value"],
          ["Assertion", "Claim type + verification state"],
          ["Derivation", "Explicit assertion lineage"],
          ["Contract", "Guarded cross-domain propagation"],
          ["Decision", "Auditable downstream consequence"],
        ].map(([title, detail], index) => (
          <div className="truth-node" key={title}>
            <span className="truth-node__index">{index + 1}</span>
            <strong>{title}</strong>
            <small>{detail}</small>
          </div>
        ))}
      </div>
    </section>
  );
}

function ChangesSurface() {
  return (
    <section className="surface-card surface-card--fill">
      <header className="surface-card__header">
        <div>
          <p className="eyebrow">Proof of work</p>
          <h2>Current engineering checkpoint</h2>
        </div>
        <StatusPill tone="good">DRIFT 0</StatusPill>
      </header>
      <div className="change-list">
        <div className="change-row">
          <time>Phase 0</time>
          <strong>Baseline preserved</strong>
          <span>Untouched branch at 9e15068d</span>
        </div>
        <div className="change-row">
          <time>Phase 1</time>
          <strong>High-impact truth audit begun</strong>
          <span>Contradictions recorded rather than overwritten</span>
        </div>
        <div className="change-row">
          <time>Phase 2</time>
          <strong>Provenance domain implemented</strong>
          <span>Evidence, assertions, rules, syllabus, scholarship, imports</span>
        </div>
        <div className="change-row">
          <time>Control</time>
          <strong>Ontology CI green</strong>
          <span>Unit tests + strict legacy validation + JSON Schema checks</span>
        </div>
      </div>
    </section>
  );
}

function Surface({ active }: { active: SurfaceId }) {
  switch (active) {
    case "command":
      return <CommandSurface />;
    case "critical-path":
      return <CriticalPathSurface />;
    case "swim-lanes":
      return <SwimLaneSurface />;
    case "courses":
      return <CoursesSurface />;
    case "scholarships":
      return <ScholarshipSurface />;
    case "evidence":
      return <EvidenceSurface />;
    case "truth":
      return <TruthSurface />;
    case "changes":
      return <ChangesSurface />;
  }
}

export function App() {
  const [activeSurface, setActiveSurface] = useState<SurfaceId>("command");
  const [query, setQuery] = useState("");
  const [notificationState, setNotificationState] = useState(
    "Native notification check not run",
  );

  const activeItem = useMemo(
    () => NAV_ITEMS.find((item) => item.id === activeSurface) ?? NAV_ITEMS[0],
    [activeSurface],
  );

  async function verifyNativeNotification(): Promise<void> {
    if (!isTauri()) {
      setNotificationState("Browser preview: native notification bridge unavailable");
      return;
    }

    try {
      let granted = await isPermissionGranted();
      if (!granted) {
        granted = (await requestPermission()) === "granted";
      }

      if (!granted) {
        setNotificationState("Notification permission not granted");
        return;
      }

      sendNotification({
        title: "Master Critical Path",
        body: "Native notification boundary is operational.",
      });
      setNotificationState("Native notification sent successfully");
    } catch (error) {
      setNotificationState(
        `Notification bridge error: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }

  return (
    <div className="app-shell">
      <header className="top-app-bar">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">
            MCP
          </div>
          <div>
            <p className="eyebrow">Local operational system</p>
            <h1>Master Critical Path</h1>
          </div>
        </div>

        <label className="global-search">
          <span aria-hidden="true">⌕</span>
          <input
            aria-label="Search Master Critical Path"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search tasks, evidence, assertions, courses, scholarships…"
            type="search"
            value={query}
          />
          <kbd>Ctrl K</kbd>
        </label>

        <div className="top-actions">
          <button className="icon-action" type="button" onClick={verifyNativeNotification}>
            <span aria-hidden="true">◉</span>
            Verify alerts
          </button>
          <div className="truth-badge" title="Legacy repository assertions are provisional">
            <span className="truth-badge__dot" />
            Evidence-first
          </div>
        </div>
      </header>

      <aside className="navigation-rail" aria-label="Primary navigation">
        <div className="nav-items">
          {NAV_ITEMS.map((item) => {
            const active = item.id === activeSurface;
            return (
              <button
                aria-current={active ? "page" : undefined}
                className={`nav-item${active ? " nav-item--active" : ""}`}
                key={item.id}
                onClick={() => setActiveSurface(item.id)}
                title={item.description}
                type="button"
              >
                <span className="nav-item__glyph" aria-hidden="true">
                  {item.glyph}
                </span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
        <div className="nav-footer">
          <StatusPill tone="good">LOCAL</StatusPill>
          <small>No production LAN service</small>
        </div>
      </aside>

      <main className="workspace">
        <header className="workspace-header">
          <div>
            <div className="breadcrumb">Master Critical Path / {activeItem?.label}</div>
            <h2>{activeItem?.label}</h2>
            <p>{activeItem?.description}</p>
          </div>
          <div className="workspace-header__status">
            <span>Truth policy</span>
            <strong>Legacy = provisional</strong>
          </div>
        </header>

        <div className="watermark" role="status">
          <span className="watermark__signal" aria-hidden="true" />
          {WATERMARK}
        </div>

        <Surface active={activeSurface} />
      </main>

      <aside className="context-panel" aria-label="Operational context">
        <section>
          <p className="eyebrow">Current gate</p>
          <h2>Evidence before execution</h2>
          <p>
            High-impact academic and funding calculations stay dormant until their
            input claims have admissible provenance.
          </p>
        </section>

        <section className="context-section">
          <h3>Boundary health</h3>
          <div className="context-stat">
            <span>Truth model</span>
            <StatusPill tone="good">Implemented</StatusPill>
          </div>
          <div className="context-stat">
            <span>Legacy adapter</span>
            <StatusPill tone="good">Tested</StatusPill>
          </div>
          <div className="context-stat">
            <span>Institutional files</span>
            <StatusPill tone="warning">Not loaded</StatusPill>
          </div>
          <div className="context-stat">
            <span>Rule execution</span>
            <StatusPill>Guarded</StatusPill>
          </div>
        </section>

        <section className="context-section">
          <h3>Notification boundary</h3>
          <p className="mono-note">{notificationState}</p>
        </section>

        <section className="context-section context-section--bottom">
          <p className="eyebrow">Search preview</p>
          <p className="mono-note">
            {query.trim()
              ? `Query staged: “${query.trim()}” · index service not connected yet`
              : "No query staged"}
          </p>
        </section>
      </aside>
    </div>
  );
}
