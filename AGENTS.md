# AGENTS.md

## Purpose

This file stores stable project context for future agents working on `dq-alert-benchmark`.

Its purpose is to prevent the main ways an AI-assisted implementation can quietly degrade the project:

- wasting time rediscovering project scope and terminology
- implementing behavior that conflicts with the benchmark specification
- silently scaling the benchmark down while presenting it as complete
- creating inconsistent rules across code, configs, docs, artifacts, and reported results
- hiding blockers, failed checks, or partial work behind vague progress updates

This file is a guardrail document. It does not replace the benchmark specification.

## Source of Truth and Precedence

Use the following precedence order whenever documents, code, configs, comments, or legacy scaffold files disagree:

1. `docs/documentation.md`
2. `docs/implementation_plan.md`
3. `AGENTS.md`
4. `docs/architecture_v2.md`
5. `docs/architecture.md`
6. `README` text, code comments, partial implementations, legacy configs, old outputs, old notes

Rules:

- `documentation.md` is the authoritative benchmark contract.
- `implementation_plan.md` is the authoritative execution checklist for coders.
- `AGENTS.md` is the stable operational context for future agents.
- `architecture_v2.md` is explanatory architecture context, not a source of benchmark semantics.
- Lower-precedence material must never override higher-precedence material.
- If implementation requires a real semantic change, update `documentation.md` first or in the same patch. Never change behavior first and explain it later.

## Current Repository Reality

Agents must assume that this repository may contain scaffold code, configs, tests, or outputs from an older benchmark framing.

Important consequences:

- existing code is not proof that the behavior is still correct
- existing config names are not proof that the benchmark contract still uses those names
- existing outputs are not proof that they are paper-scale compliant
- older pilot paths, synthetic samples, legacy detector names, or temporary calibration policies must be treated as suspect until checked against `documentation.md`

Legacy scaffold content must be treated as implementation material to be reviewed and corrected, not as ground truth.

## Project Snapshot

`dq-alert-benchmark` is a reproducible benchmark for `profile-based`, `batch-based`, `tabular` data-quality alerting on public datasets.

The project is designed as a controlled comparison of detector families under a locked protocol:

- fixed public snapshots
- fixed calibration and evaluation rules
- fixed fault-family definitions
- fixed alert matching rules
- fixed metrics
- fixed baseline set
- fixed transparent-injection, audited-clean, and external-validation evidence policy
- fixed artifact and reproducibility requirements

The scientific purpose is to answer:

1. which `profile-based` detector families are strongest for which benchmarked data-quality failure modes
2. what trade-offs exist across recall, precision, delay, localization, duplicate burden, clean-data false positives, and runtime
3. how stable rankings remain across the included operational domains when the protocol is held fixed
4. how well rankings and thresholds transfer from the injected matrix to untouched clean data and the fixed external-validation tracks

This project is not:

- a universal benchmark for all data-quality systems
- a row-level detector benchmark
- a repair framework
- a root-cause analysis system
- a streaming benchmark
- a deep-learning project
- a domain-specific semantics engine for arbitrary hidden business rules

## Locked Benchmark Scope

Agents should assume the following are fixed unless `documentation.md` is intentionally revised.

### Domains

- `NYC TLC` as a core domain
- `BTS On-Time` as a core domain
- `Chicago Food` as a core domain
- `NYC Parking Violations` as a core domain
- `NYC HPD Housing Complaints and Violations` as a core domain
- `Chicago Building Permits` as a core domain
- `NYC 311` as an external validation case study
- `Austin 311` as an external validation case study
- `BTS audit-backed supplementary appendix` using frozen `BTS` plus frozen `FAA OPSNET` extract

### Fault Families

- `null_spike`
- `range_violation`
- `duplicate_burst`
- `freshness_lag`
- `fk_break`

### Locked Baselines

- `Calibration Threshold Lower Bound`
- `Constraint-Rule Baseline`
- `History-Based Robust Profile Baseline`
- `EWMA-CUSUM Sequential Baseline`
- `Isolation Forest Baseline`

### Public-Code Reference Detector Appendix

- `ECOD`
- `COPOD`
- `Extended Isolation Forest`
- `kNN`
- `LOF`
- `One-Class SVM`

### Locked Units and Conditions

- operational unit: `batch`
- truth unit: `incident`
- reporting unit: `alert`
- experiment cell: `condition = domain x fault_family x severity x duration x seed`
- each dirty run contains exactly `one` incident from exactly `one` fault family
- durations: `one_window`, `sustained`
- severities: `low`, `medium`, `high`
- seeds per condition: `5`

### Locked Primary Metrics

- `incident_recall`
- `incident_precision`
- `incident_f1`
- `detection_delay_norm_mean`
- `localization_accuracy_hierarchical`
- `duplicate_burden`
- `clean_run_fp_batch`
- `runtime_per_1m_rows`

### Locked Benchmark Size

- `NYC TLC`: `150` dirty runs + `1` clean evaluation run
- `BTS On-Time`: `150` dirty runs + `1` clean evaluation run
- `Chicago Food`: `120` dirty runs + `1` clean evaluation run
- `NYC Parking Violations`: `120` dirty runs + `1` clean evaluation run
- `NYC HPD Housing Complaints and Violations`: `120` dirty runs + `1` clean evaluation run
- `Chicago Building Permits`: `120` dirty runs + `1` clean evaluation run
- `786` total benchmark runs
- `3930` detector executions for the `5` locked baselines
- `4716` detector executions for the `6` public-code reference detectors
- `8646` detector executions for the full `11`-detector empirical comparison release

## Canonical Benchmark Contract

Agents must preserve these benchmark truths:

- Detectors consume canonical `batch profiles`, not raw rows directly.
- Conclusions are scoped only to detectors that operate on canonical batch profiles plus any declared public support tables.
- Feature families are fixed by the spec, including `row_count`, `null_ratio`, `duplicate_ratio`, `min/max`, `range_violation_ratio`, and `invalid_fk_ratio`.
- The canonical batch index includes zero-row scheduled batches.
- Monitored scope catalogs are part of the public benchmark contract, not an implementation detail.
- Calibration uses the first `30%` of chronological batches with a minimum of `24`, then applies cleanliness screening.
- Thresholds are derived from clean calibration scores only.
- Dirty conditions are sampled only from the evaluation pool.
- Injection is required to be transparent: operator-bank definitions, realized manifests, and side-effect reporting are part of the contract.
- Injection operators must carry evidence-backed rationale via literature, official audit, incident, or declared engineering-archetype mapping.
- Each `domain x fault_family` pair must target at least `3` operators whenever the fault semantics admit three or more realistic constructions; smaller banks must be explicitly marked and justified.
- Each core domain includes an audited clean track for false-positive and threshold-portability interpretation.
- Clean-track audit strength is part of the contract: paper-scale releases audit at least `60` sampled batch-scope units per core domain, stratify across the clean-track timeline, and publish the resulting one-sided exact `95%` upper confidence bound.
- The primary leaderboard is locked to `percentile_95`.
- Detector configurations and injector definitions are predeclared and must not be revised after observing dirty-run, clean-track, or external-validation outcomes for the same released snapshot.
- The primary leaderboard scores a single primary alert per batch; detectors with native multi-alert behavior must publish a supplementary native-output appendix.
- External validation tracks are reported separately from the primary leaderboard.
- The `BTS` appendix uses weak labels and discrepancy windows. It is supplementary and must never be merged into the primary leaderboard.
- Transfer analysis is supplementary but required for paper-scale claim boundaries.
- Paper-scale empirical releases must ship the six-detector public-code reference appendix; otherwise empirical comparison is incomplete.
- Paper-scale releases must publish domain-scale disclosure tables for every admitted core-domain snapshot.
- Third-party detectors must obey the same public contract as built-in baselines.

## Project Glossary

Use benchmark vocabulary consistently. Do not invent near-synonyms when the spec already defines a term.

- `batch`: one scheduled operational data slice processed by a detector
- `alert`: one detector output associated with one batch and one scope
- `incident`: one injected or externally validated data-quality event spanning one or more consecutive batches
- `condition`: one benchmark cell `domain x fault_family x severity x duration x seed`
- `calibration prefix`: the screened-clean prefix used to fit detectors and derive thresholds
- `evaluation pool`: batches after the calibration prefix from which dirty conditions are sampled
- `canonical batch index`: the full scheduled batch timeline, including zero-row scheduled batches
- `monitored scope catalog`: the published list of monitored columns, keys, ranges, support tables, and sampling frames
- `support table`: a public frozen reference table used by the benchmark contract

## Project Architecture

Workspace layout:

- `.`
  - main implementation scaffold for the benchmark artifact
- `docs/`
  - benchmark-level documents inside the scaffold
  - authoritative spec lives in `documentation.md`
  - implementation checklist lives in `implementation_plan.md`
  - explanatory architecture docs live in `architecture.md` and `architecture_v2.md`

Implementation scaffold layout:

- `src/dqbench`
  - Python package root for benchmark implementation
  - benchmark runtime code should live here
- `configs/`
  - config-driven control plane
  - expected areas: datasets, faults, detectors, calibrations, experiments
- `data/`
  - local data workspace
  - expected areas: raw, external, interim, processed, ground_truth
- `outputs/`
  - generated benchmark outputs
  - expected areas: runs, reports, figures
- `scripts/`
  - acquisition, checks, orchestration, and reporting entry points
- `tests/`
  - verification layer
  - expected grouping: contracts, evaluation, injection, orchestration
- `refs/`
  - external references, copied notes, benchmark support material

Runtime architecture intent:

1. acquire and freeze public snapshots
2. canonicalize data and build the canonical batch index
3. publish monitored scope catalogs
4. generate frozen calibration and evaluation splits
5. inject benchmark faults and record incident-level ground truth
6. compute canonical batch profiles
7. run locked baselines or admissible third-party detectors on the same interface
8. match alerts to incidents and compute locked metrics
9. aggregate tables, statistics, and artifact outputs

## Implementation Order Agents Must Respect

Do not jump ahead and improvise. Follow the dependency order from `implementation_plan.md`.

1. freeze constants, identifiers, schemas, and contracts
2. implement dataset acquisition and raw snapshot manifests
3. canonicalize domains and publish monitored scope catalogs
4. freeze calibration and evaluation split generation plus cleanliness reports
5. implement fault injection, transparent manifests, and audited clean-track artifacts
6. implement canonical batch profiling
7. implement the five locked baselines
8. implement alert normalization, matching, and metrics
9. implement `NYC 311`, `Austin 311`, and the `BTS` supplementary appendix
10. implement orchestration, transfer analysis, aggregation, statistics, and release packaging

If a phase depends on artifacts from an earlier phase, do not fake or hand-wave the earlier phase just to keep moving.

## Code and Documentation Conventions

- Use the `src` layout. Production Python code belongs under `src/dqbench`.
- Keep implementation config-driven. Dataset, detector, fault, calibration, and experiment behavior should live in `configs/` and manifests when possible.
- Prefer deterministic execution. Freeze seeds, snapshot identifiers, split definitions, manifests, and checksums wherever the spec requires them.
- Follow `snapshot-first` reproducibility. Do not center benchmark logic around live API calls when frozen public snapshots are required.
- Favor explicit schemas and manifests over implicit behavior.
- Keep baseline naming scientifically honest. A representative family baseline is not a vendor engine unless the spec explicitly says so.
- Keep dependencies inspectable and minimal unless the spec or implementation explicitly requires expansion.
- Keep tests aligned to benchmark contracts rather than generic unit-test vanity.
- Keep all artifact names and metric names consistent with the spec. Do not create alternate spellings for the same concept.
- When changing benchmark semantics, update docs and code in the same work, not in separate drifting patches.

## Non-Negotiable Rules

- Always follow `docs/documentation.md` when implementing benchmark logic.
- Never silently scale down the benchmark and present it as paper-scale complete.
- Never implement a lite, proxy, fallback, mock, approximate, or substitute version of a required algorithm, baseline, metric, artifact, or contract and present it as the specified implementation.
- If the required implementation cannot be completed exactly, fail loudly, mark the slice as blocked or partial, and explain the gap explicitly. Do not silently swap in a different method just to keep the pipeline running.
- Never claim a benchmark slice is complete if required artifacts, metrics, manifests, schema validation, tests, or release-gate checks for that slice are still missing.
- Never convert a paper-scale requirement into a pilot-only shortcut unless the user explicitly approves that downgrade.
- Never hide unresolved errors behind warnings, TODOs, silent defaults, best-effort behavior, or undocumented fallback paths.
- Never replace a locked baseline, domain, metric, fault family, artifact requirement, or scoring rule without updating the spec.
- Never let detectors use raw-row access, hidden labels, benchmark-private metadata, or side channels if the public contract does not allow it.
- Never merge `NYC 311` external validation or the `BTS` appendix into the primary leaderboard or inferential ranking tables.
- Never treat weak labels as exact incident ground truth.
- Never skip calibration cleanliness just because the acquisition pipeline is inconvenient.
- Never omit audited clean-track protocol, injection manifests, or transfer-analysis outputs when the spec requires them.
- Never retune detector configurations or injector definitions after observing dirty-run, clean-track, or external-validation outcomes for the same released snapshot.
- Never publish an empirical comparison release without the required public-code reference-detector appendix.
- Never omit required domain-scale disclosure tables or outputs.
- Never omit operator-evidence maps or required native-output appendices when the spec requires them.
- Never omit monitored scope catalogs, manifests, checksums, schema validation, or hardware/runtime policy when the spec requires them.
- Never report pilot-scale shortcuts as if they satisfy the full release gate.
- Never use placeholders that look final. If something is partial, mark it clearly as partial.
- Never allow code, docs, configs, schemas, and reported results to drift apart while still presenting the work as spec-compliant.

## Human-In-The-Loop Rules

Agents must stop and ask the user before proceeding when any of the following occurs:

- a required dependency, dataset, support table, backend, or public source is unavailable
- a required algorithm cannot be implemented exactly as specified
- a failing test, schema validation error, contract violation, or runtime error indicates the current implementation is not trustworthy
- two documents or two parts of the codebase conflict in a way that affects benchmark semantics
- the only available path forward would require scope reduction, fallback behavior, proxy logic, default substitution, or skipping a required artifact
- a detector, metric, matching rule, calibration rule, injection rule, or runtime boundary is ambiguous in a way that could change reported results
- a release-gate requirement cannot currently be satisfied
- a baseline would need to be renamed, replaced, weakened, or partially implemented to keep progress moving
- results would need to be reported with caveats strong enough to affect their scientific interpretation

When one of these stop conditions is hit:

1. stop implementation work on the affected slice
2. summarize the blocker honestly and concretely
3. state what requirement would be violated by continuing
4. ask the user how they want to proceed

Do not choose a workaround unilaterally when the workaround would lower benchmark fidelity.

## Progress Reporting Rules

Agents must report progress explicitly during implementation work.

For every meaningful work step or patch, the agent must communicate:

- what was implemented, changed, or verified
- what remains unfinished
- whether the current slice is complete, partial, or blocked
- any blocker, risk, failed check, or assumption that affects confidence

Reporting rules:

- Never report only the successful part while omitting unfinished required work.
- Never imply completion when only a subset of the required slice has been implemented.
- If a task is partial, say it is partial and list the missing pieces.
- If a task is blocked, say it is blocked and state exactly why.
- If tests, validation, or runtime checks were not run, say so explicitly.
- If a check failed, report the failure explicitly instead of summarizing the work as done.

Minimum reporting format for implementation updates:

1. completed in this step
2. not yet completed
3. blockers or risks

## Common Failure Patterns To Avoid

Agents should actively guard against these mistakes:

- implementing a detector on raw tables because it feels easier than honoring the batch-profile interface
- letting synthetic injection remain opaque or hand-picked while still claiming transparent generation
- shipping a detector family under the correct name but with materially different behavior from the specified baseline
- keeping legacy scaffold names or configs and treating them as proof of correctness
- using only a subset of fault families but forgetting to label the run as partial
- skipping `fk_break` where it is required by the domain-fault matrix
- treating multi-alert detector output as leaderboard-ready without deterministic single-alert reduction
- skipping zero-row scheduled batches in the canonical batch index
- skipping calibration cleanliness, monitored scope catalogs, or support-table validation because they feel like metadata rather than benchmark logic
- deriving thresholds from dirty or evaluation data instead of screened-clean calibration scores
- using evaluation outcomes to tune hyperparameters while still claiming the locked protocol
- revising injector definitions after observing accepted dirty-run behavior instead of freezing them up front
- reporting a detector as strong without considering audited clean-track behavior or external-transfer evidence
- publishing empirical comparison claims without the required public-code reference-detector appendix
- omitting domain-scale disclosures while still implying the benchmark has convincing real-data breadth
- omitting the native multi-alert appendix for a detector whose unreduced outputs would tell a materially different story from the single-alert leaderboard view
- changing runtime measurement boundaries without updating the documented contract
- publishing attractive figures while machine-readable manifests or schema reports are missing
- substituting library defaults where the spec locks explicit hyperparameters or policies
- substituting a different detector or proxy scoring path when the required detector backend is unavailable
- reporting partial runs, incomplete artifacts, synthetic shortcuts, or pilot outputs as if they satisfy paper-scale release conditions
- cherry-picking only favorable metrics, tables, conditions, or domains while implying full benchmark coverage
- letting docs, configs, schemas, and code drift apart while still presenting results as spec-compliant
- allowing nondeterministic seeds, unfrozen splits, mutable snapshots, or ad hoc local edits to leak into benchmark results
- treating benchmark-control severity bands as business-impact labels

## Required Deliverable Mindset

When a task is marked complete, agents should expect the work to include all required forms, not just code:

- implementation code
- config or manifest artifacts where required
- schema validation outputs where required
- tests or validators where required
- machine-readable outputs where required
- documentation updates where required

Completion means the benchmark contract for that slice is satisfied, not merely that a function exists.

Done means all of the following are true for the claimed slice:

- the implementation matches the specified behavior
- required dependencies and backends are real, not simulated substitutes
- required artifacts are materialized
- relevant tests or validators pass
- docs, configs, schemas, and code agree
- no known blocker is being hidden behind a silent workaround

## Change Management Rules

If an agent discovers ambiguity, a missing decision, a conflict, or legacy scaffold behavior that appears inconsistent with the spec:

1. check `documentation.md`
2. check `implementation_plan.md`
3. check `AGENTS.md`
4. inspect existing code and configs
5. if the issue still affects benchmark semantics, implementation fidelity, or result interpretation, stop and ask the user
6. only self-resolve when the issue is minor and cannot materially change benchmark behavior or claims
7. if resolution changes benchmark semantics, update `documentation.md` first or in the same patch

Do not invent a broad interpretation when a narrow interpretation keeps the benchmark scientifically honest.

## Practical Reminders For Future Agents

- Before implementing, re-read the relevant section of `docs/documentation.md`.
- Before starting a new phase, verify that the previous phase's deliverables exist or are being created in the same work.
- Before trusting old scaffold code, configs, tests, or outputs, verify that they still match the current spec.
- Before claiming something is done, check whether the spec also requires:
  - a config artifact
  - a machine-readable output
  - a manifest or checksum
  - a calibration or injection contract
  - a schema validator
  - a test or release-gate hook
- If an error, blocker, missing backend, or unresolved ambiguity would force a downgrade, stop and ask the user instead of improvising a workaround.
- If code, docs, configs, and manifests disagree, stop and resolve the inconsistency.
- When in doubt, prefer being narrower, explicit, and reproducible rather than broader, clever, or under-specified.
