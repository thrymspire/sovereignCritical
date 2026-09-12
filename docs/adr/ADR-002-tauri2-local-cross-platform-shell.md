# ADR-002: Tauri 2 Cross-Platform Local Application Shell

**Status:** Accepted  
**Date:** 2026-09-12  
**Decision owner:** Project owner / Master Critical Path governance

## Motion / Proposal

Adopt **Tauri 2** as the target application shell for Master Critical Path, with a web-rendered frontend, Rust-owned platform integration boundary, local persistence, and explicit Android hooks.

Material 3 will be implemented as a **design-system/token contract**, not by depending on one specific Material Web component library.

## Requirements Driving the Decision

The project owner requires:

- Windows, Linux, and macOS desktop support;
- direct local program execution;
- no externally exposed production HTTP service;
- future Android application hooks;
- native notifications;
- local file/evidence access;
- a modern Material 3-class user interface;
- preservation of a platform-neutral ontology/rule/evidence core;
- migration from the existing HTML cockpit without discarding useful frontend work.

## Evidence

As of 2026-09-12:

- Tauri 2 officially supports Linux, macOS, Windows, Android, and iOS from a single application architecture: https://v2.tauri.app/
- Tauri's notification plugin supports Windows, Linux, macOS, Android, and iOS: https://v2.tauri.app/plugin/notification/
- Tauri mobile plugins support Android-native Kotlin/Java implementations and shared desktop/mobile Rust APIs: https://v2.tauri.app/develop/plugins/develop-mobile/
- Current Tauri core release information documents the 2.11 line and current security fixes: https://tauri.app/release/
- Google's `material-components/material-web` repository states that Material Web is in maintenance mode pending new maintainers. Therefore the project should consume Material 3 principles/tokens without binding core UI architecture to that package's lifecycle: https://github.com/material-components/material-web

## Alternatives Considered

### Existing direct-open HTML only

**Advantages**

- current application already launches from disk;
- no packaging/runtime dependency;
- simplest deployment model.

**Rejected as final architecture because**

- direct browser file access is awkward for durable local persistence and evidence-file workflows;
- native notifications and future Android integration become fragmented;
- current build duplicates a multi-megabyte generated HTML artifact three times;
- source/data boundaries are compiled together by regex replacement.

The legacy HTML remains a migration reference and temporary fallback, not the target shell.

### Electron

**Advantages**

- mature ecosystem;
- broad Node/browser compatibility.

**Rejected because**

- ships a larger browser/runtime surface than this local operational system needs;
- Android is not a natural continuation of the desktop architecture;
- Tauri better matches the owner's future mobile requirement.

### Flutter

**Advantages**

- strong cross-platform support;
- first-class Material 3 widgets;
- Android path is excellent.

**Rejected for this repository because**

- it would discard essentially all existing browser UI work;
- frontend migration cost is much higher;
- the current system and future graph/evidence inspectors fit a DOM/webview architecture well.

Flutter remains a valid contingency if Tauri mobile or accessibility constraints later become blocking.

## Frontend Strategy

The frontend should be framework-capable but domain-independent.

Initial target:

- TypeScript;
- React for dense stateful operational surfaces;
- Vite for development/build tooling;
- CSS custom properties representing Material 3 semantic design tokens;
- no CDN dependencies in production;
- no Material component dependency permitted to become an authoritative domain dependency.

Material 3 requirements will be encoded through:

- semantic color roles;
- typography roles;
- elevation/surface roles;
- state layers;
- focus/keyboard behavior;
- density variants;
- shape tokens;
- motion tokens with reduced-motion handling;
- responsive navigation patterns;
- accessible contrast and target sizes.

The cockpit may preserve its distinctive visual identity, but visual novelty must never obscure truth state, criticality, evidence status, or dependencies.

## Platform Boundary

The application will separate:

1. frontend presentation;
2. application/query services;
3. truth/evidence/rule domain;
4. local persistence;
5. import/file services;
6. search/indexing;
7. notification scheduling;
8. platform integration.

Tauri/Rust code owns privileged platform operations. Frontend code requests narrow commands/capabilities rather than receiving unrestricted filesystem or shell access.

## Network Contract

Production operation must not bind an application HTTP server to LAN interfaces.

Remote-origin capabilities must remain disabled unless an explicit future requirement is reviewed through an ADR.

Any future online corroboration or scholarship discovery feature must be an explicit outbound client capability with a narrow allowlist and provenance capture. It must not turn the application into a network service.

## Android Contract

Android support may be deferred as a packaged target, but architecture must preserve:

- shared domain identifiers;
- shared persistence schema/migrations where practical;
- shared notification-policy representation;
- mobile-safe application commands;
- platform-specific implementation behind stable interfaces;
- ability to add Kotlin plugin implementations without rewriting domain rules.

Desktop-only assumptions are prohibited from the domain layer.

## Risks

### Rust/Tauri adds build complexity

Mitigated through CI and a minimal privileged command surface.

### Webview differences across operating systems

Mitigated by testing the supported desktop targets and avoiding browser-specific behavior not covered by the platform matrix.

### Mobile UI needs different information density

Expected. The ontology and application services are shared; presentation does not need to be identical. Android should emphasize next actions, evidence capture, alerts, and task inspection rather than reproducing a desktop-wide graph on a small screen.

### Material ecosystem churn

Mitigated by owning semantic design tokens and accessibility behavior rather than outsourcing the design contract to one component package.

## Decision

Accepted.

Tauri 2 is the target local cross-platform shell. React/TypeScript/Vite is the initial frontend target. Material 3 is an owned design-system contract. Android remains an architectural target from the beginning even if its packaged UI is delivered later.

## Verification Required Before Superseding Legacy UI

The new shell must demonstrate:

1. direct packaged launch;
2. no LAN listener in production;
3. local persistence and migrations;
4. evidence-file selection and read-only preview path;
5. ontology/query service integration;
6. native desktop notification capability;
7. keyboard-accessible navigation;
8. responsive task inspector;
9. critical-path and truth-state presentation;
10. reproducible build in CI.

Only after these pass should the legacy giant HTML output cease to be a supported fallback.
