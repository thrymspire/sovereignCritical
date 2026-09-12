# Master Critical Path — Phase 1 Truth Audit

**Audit start:** 2026-09-12  
**Working branch:** `project-owners/master-critical-path-v1`  
**Policy:** Legacy repository claims remain provisional until corroborated. Institutional records and authoritative program sources control.

This audit records atomic claims and their verification state. It does not silently overwrite legacy data.

## Status Vocabulary

- `VERIFIED_EXTERNAL` — supported by a current authoritative public source.
- `CONTRADICTED_EXTERNAL` — a current authoritative public source conflicts with the repository claim.
- `PARTIALLY_VERIFIED` — part of the claim is supported but important qualifiers differ.
- `USER_RECORD_REQUIRED` — depends on the owner's private institutional/account record and cannot be established from public sources.
- `NOT_YET_PUBLISHED` — a future institutional value is not currently available from an authoritative source.
- `NEEDS_REVIEW` — ambiguous or multiple rules may apply.

---

## A. University of Alaska Fairbanks

### UAF-TRUTH-001 — 2026–2027 Fairbanks undergraduate resident tuition

**Legacy claim:** README references an in-state/eCampus resident rate of `$289/credit`.

**Status:** `CONTRADICTED_EXTERNAL`

**Authoritative source:** University of Alaska Fairbanks 2026–2027 Catalog, Tuition, Fees and Costs.  
Source: https://catalog.uaf.edu/costs-financial-aid/tuition/

**Verified current rule:**

- Fairbanks undergraduate F100–F499 resident tuition: **$310/credit**.
- Community Campus F100–F299 resident tuition: **$251/credit**.
- Tuition depends on course level, campus, and residency classification.

**Consequence:** Any projected tuition liability using `$289/credit` must be recalculated from actual registered course attributes and current fee rules.

### UAF-TRUTH-002 — eCampus courses receive resident tuition treatment

**Status:** `VERIFIED_EXTERNAL`

**Authoritative sources:**

- https://www.uaf.edu/admissions/apply/ecampus.php/
- https://www.uaf.edu/admissions/residency.php

**Verified current rule:** UAF states that eCampus-supported courses are charged resident tuition; the residency page states eCampus and CIS courses remain assessed at the resident rate regardless of residency status.

**Consequence:** The ontology must model `delivery/campus` independently from `residency`, because course-specific resident-rate treatment is a rule rather than a global student attribute.

### UAF-TRUTH-003 — Fall 2026 academic calendar dates

**Status:** `VERIFIED_EXTERNAL`

**Authoritative source:** https://catalog.uaf.edu/calendar/

Current UAF 2026–2027 calendar identifies:

- Fall 2026 last day of instruction: **December 5, 2026**.
- Final examinations: **December 7–12, 2026**.
- Faculty grade-posting deadline: **December 16, 2026 at noon**.

**Legacy conflict:** Repository logic references a `December 19, 2026` grade gate as though it were an institutional finalization date.

**Status of Dec. 19 gate:** `CONTRADICTED_EXTERNAL` if represented as UAF's official grade-posting deadline; it may remain as an internal planning milestone only if relabeled accordingly.

### UAF-TRUTH-004 — Spring 2027 commencement

**Status:** `VERIFIED_EXTERNAL`

The current 2026–2027 UAF academic calendar lists **Saturday, May 1, 2027** as commencement.

### UAF-TRUTH-005 — May 6, 2028 commencement/conferral claim

**Legacy claim:** README presents `Saturday, May 6, 2028` as a definite UAF commencement date.

**Status:** `NOT_YET_PUBLISHED`

At the time of this audit, the public UAF catalog source retrieved for current institutional dates covers 2026–2027. No authoritative 2027–2028 calendar was established in this audit.

**Consequence:** May 6, 2028 must be represented as a provisional projection until an official UAF 2027–2028 calendar is captured.

### UAF-TRUTH-006 — Full-time undergraduate definition

**Status:** `VERIFIED_EXTERNAL`

The 2026–2027 UAF catalog identifies undergraduate full-time enrollment as **12 or more credits**.

**Important boundary rule:** This UAF definition must not be conflated with federal in-school deferment rules, which use at-least-half-time enrollment.

### UAF-TRUTH-007 — UA Foundation/private scholarship application deadline

**Status:** `VERIFIED_EXTERNAL`

The UAF 2026–2027 academic calendar lists **February 15, 2027** as the deadline for UA Foundation and privately funded scholarship applications.

---

## B. Federal Student Aid / Loan Rehabilitation

### FSA-TRUTH-001 — Direct/FFEL rehabilitation payment count

**Status:** `VERIFIED_EXTERNAL`

**Authoritative source:** Federal Student Aid, Student Loan Rehabilitation for Borrowers in Default.  
Source: https://studentaid.gov/articles/rehab/

For Direct Loan and FFEL borrowers, successful rehabilitation requires **nine on-time voluntary payments during a period of 10 consecutive months**.

**Correction to legacy semantics:** This is not accurately modeled as an invariant requiring nine strictly consecutive monthly payments for Direct/FFEL loans. Federal Student Aid explicitly notes that one payment may be missed within the 10-month period.

The owner's actual agreement, payment amount, loan types, start date, and payment history remain `USER_RECORD_REQUIRED`.

### FSA-TRUTH-002 — Monthly rehabilitation payment amount

**Legacy claim:** `$5/month`.

**Status:** `USER_RECORD_REQUIRED`

Federal Student Aid explains that a standard rehabilitation payment is generally based on 15% of annual discretionary income divided by 12, while an alternative reasonable and affordable payment can be established under applicable procedures.

The owner's `$5` amount cannot be established from public policy alone and requires the signed rehabilitation agreement or DRG record.

### FSA-TRUTH-003 — Aid eligibility after successful rehabilitation

**Status:** `VERIFIED_EXTERNAL`

Federal Student Aid states that after successful rehabilitation the default status is removed, collections stop, and the borrower becomes eligible to receive federal student aid again, subject to otherwise applicable eligibility rules.

**Correction:** This should be modeled as `federal aid default barrier removed`, not as a guaranteed future Pell award.

### FSA-TRUTH-004 — Credit-report effect of rehabilitation

**Legacy claim:** completion permanently deletes defaults from all credit bureaus and effectively clears the entire adverse history.

**Status:** `PARTIALLY_VERIFIED`

**Authoritative source:** https://studentaid.gov/articles/default/

Federal Student Aid states that after the ninth rehabilitation payment, the Department of Education sends a request to credit reporting agencies to remove the record of default. However, earlier late payments reported by the prior servicer can remain on credit history.

**Consequence:** Replace absolute language such as `complete deletion`, `permanently deletes defaults from all credit bureaus`, or claims implying deletion of delinquency history with the narrower verified rule.

### FSA-TRUTH-005 — In-school deferment threshold

**Legacy claim:** full-time enrollment (`>=12 credits`) creates an in-school deferment mandate.

**Status:** `CONTRADICTED_EXTERNAL`

**Authoritative source:** Federal Student Aid default guidance and federal-servicer guidance identify **at least half-time enrollment** as the relevant enrollment threshold for in-school deferment eligibility/reporting.

UAF's 12-credit full-time definition is a separate institutional rule.

**Consequence:** The ontology needs distinct predicates for `UAF_FULL_TIME`, `FEDERAL_HALF_TIME`, and any scholarship-specific enrollment threshold.

### FSA-TRUTH-006 — `$0 IDR` as an automatic result of in-school deferment

**Status:** `CONTRADICTED_EXTERNAL / UNSUPPORTED DERIVATION`

In-school deferment and an income-driven repayment payment calculation are separate mechanisms. A deferment can postpone required payments while eligible; it does not deterministically imply a `$0` IDR payment.

**Consequence:** Remove any boundary contract `half/full-time enrollment -> $0 IDR` unless a specific servicer/IDR determination supplies that fact.

---

## C. Federal Pell Grant

### PELL-TRUTH-001 — Lifetime eligibility maximum

**Status:** `VERIFIED_EXTERNAL`

**Authoritative source:** Federal Student Aid financial-aid dictionary and 2026–2027 Federal Student Aid Handbook.

Federal Pell Grant lifetime eligibility is limited to **600% LEU**, approximately 12 full-time semesters/six years.

### PELL-TRUTH-002 — Owner has exactly 400% LEU remaining

**Status:** `USER_RECORD_REQUIRED`

This is an individual account fact. It must come from the owner's StudentAid.gov record, ISIR/aid documentation, or an institutional financial-aid record.

### PELL-TRUTH-003 — `$29,580` is a guaranteed Pell “reserve”

**Legacy claim:** `400% LEU intact = $29,580 reserve`.

**Status:** `CONTRADICTED_EXTERNAL / UNSUPPORTED DERIVATION`

**Authoritative sources:**

- https://fsapartners.ed.gov/knowledge-center/library/dear-colleague-letters/2026-01-30/2026-27-federal-pell-grant-maximum-and-minimum-award-amounts
- https://studentaid.gov/articles/dont-miss-out-on-pell-grants/

For 2026–2027, the maximum scheduled Pell Grant is **$7,395**. Actual awards are individual and depend on eligibility, enrollment intensity, SAI/Max/Min Pell rules, cost of attendance, award year, and remaining LEU. Future award-year maximums may differ.

Multiplying remaining LEU by one year's maximum does not create a guaranteed cash reserve or entitlement value.

**Consequence:** Represent remaining LEU as a capacity constraint and each award year as a separately derived estimate/award, never as a fixed bank balance.

### PELL-TRUTH-004 — Year-round Pell

**Status:** `VERIFIED_EXTERNAL`

Eligible students may receive up to 150% of their scheduled Pell award within an award year under year-round Pell rules, subject to eligibility and enrollment conditions.

**Consequence:** Summer Pell should be modeled as a conditional award calculation, not a predetermined disbursement.

---

## D. The CIRI Foundation

### CIRI-TRUTH-001 — Current Higher Education scholarship application windows

**Legacy claim:** general CIRI deadlines described as June 1 / December 1 and `$6,000/year`.

**Status:** `CONTRADICTED_EXTERNAL`

**Current authoritative source:** https://thecirifoundation.org/scholarships/

TCF currently lists Higher Education scholarship application windows as:

- **April 1 – June 30**
- **October 1 – December 31**

The foundation's home page currently identifies the next higher-education window as **October 1 – December 31, 2026**.

### CIRI-TRUTH-002 — Current Higher Education award formula

**Status:** `VERIFIED_EXTERNAL`

TCF states that, following its 2025 updates:

- undergraduate award: **$200 per credit hour**;
- graduate award: **$400 per credit hour**;
- up to **$3,000 per term** for 15+ credits;
- 12 credits would correspond to up to **$2,400 per term** under the stated formula;
- up to **$9,000/year** with summer school, subject to funding and eligibility.

This replaces the repository's simplistic `$6,000/year ($3k/semester)` rule.

### CIRI-TRUTH-003 — General eligibility

**Status:** `VERIFIED_EXTERNAL`

Current TCF general Higher Education requirements include:

- CIRI original shareholder or lineal descendant;
- high school diploma or GED;
- enrolled in an eligible degree/pre-requisite program;
- accredited institution;
- minimum **2.0 GPA**.

### CIRI-TRUTH-004 — Application documentation/process

**Status:** `VERIFIED_EXTERNAL`

TCF requires applicants to establish eligibility and use its online scholarship portal. It states that emailed documents are not accepted and that all application materials are due by the deadline, with a documented schedule/transcript attestation process for certain delayed records.

**Ontology consequence:** CIRI should be represented with explicit `EligibilityCriterion`, `ApplicationWindow`, `RequiredDocument`, `SubmissionChannel`, `AwardFormula`, `LifetimeFundingLimit`, and `ExceptionProcedure` nodes rather than a single funding row.

---

## E. Central Council of Tlingit & Haida Indian Tribes of Alaska

### TH-TRUTH-001 — College Student Assistance (CSA) eligibility

**Status:** `VERIFIED_EXTERNAL`

**Authoritative source:** https://tlingitandhaida.gov/service/college-student-assistance-csa-scholarship/

Current published CSA criteria include:

- enrollment in Tlingit & Haida;
- origin from a Southeast Alaska community and applicability of the compacted service-area rules;
- enrollment/attendance at an accredited college or university;
- pursuit of an associate degree or higher;
- cumulative GPA of **2.0**;
- U.S. residence.

### TH-TRUTH-002 — CSA required documents

**Status:** `VERIFIED_EXTERNAL`

Current published documentation includes:

- unofficial transcript;
- class schedule **or** Certified Enrollment Verification confirming term attendance;
- school invoice/statement showing charges for the application term.

Tlingit & Haida states that uploaded documents should be PDFs and that documents should be provided by the school.

### TH-TRUTH-003 — CSA application periods

**Status:** `VERIFIED_EXTERNAL`

Current published semester periods:

- Fall: **August 1 – December 15**
- Spring: **December 16 – May 31**

CSA is not available for summer semesters.

Quarter-system windows are separately published and should not be conflated with semester windows.

### TH-TRUTH-004 — Alumni Scholarship Assistance Program (ASAP)

**Status:** `VERIFIED_EXTERNAL`

Current published rules include:

- application window: **July 1 – September 15**;
- one-time per academic year;
- enrolled in Tlingit & Haida;
- accredited college/university;
- associate degree or higher;
- cumulative GPA of **3.0**;
- U.S. residence;
- T&H enrollment number;
- unofficial transcript;
- class schedule or Certified Enrollment Verification verifying full-time attendance.

**Legacy conflict:** repository wording that treats Tlingit & Haida programs as a single `$5,500/year` rolling grant with `Sept. 15 / Nov. 1` deadlines does not match the currently published program-specific criteria and windows.

---

## F. Ketchikan Indian Community

### KIC-TRUTH-001 — Current higher-education grant amount/deadlines/requirements

**Legacy claim:** `$8,000/year ($4k/semester)` with `Dec. 1 / July 1` windows.

**Status:** `USER_RECORD_REQUIRED / NEEDS_REVIEW`

A current authoritative KIC higher-education program page establishing those exact values was not retrieved during this audit. Secondary/public references confirm KIC operates education programs, but that is not enough to validate the specific award, deadlines, or paperwork requirements.

**Required evidence:** current KIC Education & Training program documentation, application instructions, award letter, email, or current official webpage/PDF.

Do not propagate the legacy `$8,000/year` value into funding forecasts until corroborated.

---

## G. Immediate Ontology Consequences

The audit establishes several required distinctions:

1. `InstitutionalFullTimeThreshold` is not the same entity/rule as `FederalDefermentHalfTimeThreshold`.
2. `PellRemainingLEU` is not a cash asset and must not be typed as `FundingBalance`.
3. `ScholarshipAwardFormula` must be separate from `ScholarshipMaximum` and `ScholarshipProjection`.
4. `ApplicationWindow`, `PriorityDeadline`, `FinalDeadline`, and `DocumentDueDate` must be separate temporal entities.
5. `DefaultRecordRemoved` is not equivalent to `AllNegativeCreditHistoryRemoved`.
6. `FederalAidEligibilityRestored` is not equivalent to `PellAwardGuaranteed`.
7. `PlanningMilestone` must not masquerade as `InstitutionalDeadline`.
8. Program rules must include source version/effective date because scholarship and tuition rules change.

---

## H. Required Owner-Supplied Tier-1 Evidence

The following high-impact claims cannot be made authoritative from public web sources and should be supplied through source-preserving drop-in ingestion when available:

- current official transcript;
- current UAF degree audit;
- Fall 2026 registration/course schedule;
- course syllabi;
- current UAF account/bursar statement;
- current financial-aid offer/determination;
- StudentAid.gov aid summary showing LEU and loan status;
- signed loan rehabilitation agreement and payment history;
- current scholarship award/application records;
- current KIC higher-education documentation;
- any institutional record establishing housing/funding obligations represented in the legacy graph.

The application must be able to ingest these artifacts later without requiring the canonical graph or UI to be rewritten.

---

## I. Truth-Audit Watermark

`MCP-WM/1.1 | baseline:9e15068d453284e027cf6413ef9fc2871ee17f70 | branch:project-owners/master-critical-path-v1 | phase:TRUTH-AUDIT | decision:PUBLIC-HIGH-IMPACT-CLAIMS-AUDITED | evidence:MIXED-PUBLIC-VERIFIED-PRIVATE-PENDING | critical:EVIDENCE-PROVENANCE-ONTOLOGY | drift:0 | checkpoint:2026-09-12T13:55-07:00`

## J. Next Critical Action

Introduce an additive evidence/provenance ontology that can wrap the existing legacy scheduling graph without prematurely rewriting legacy claim values. The first migration must preserve all raw source values, assign provisional status by default, and make contradictions first-class rather than silently choosing winners.
