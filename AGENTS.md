# AGENTS.md

## Purpose

This file stores stable project context for future agents working on `dq-alert-benchmark`.

Its job is to prevent four failure modes:

- wasting time rediscovering what the project is
- implementing behavior that conflicts with the benchmark specification
- silently scaling the benchmark down while presenting it as complete
- creating inconsistent rules across code, configs, docs, and outputs

This file is a guardrail document, not a replacement for the benchmark spec.

## Source of Truth and Precedence

Use the following precedence order whenever documents, code, configs, or comments disagree:

1. `/home/dtl/Documents/thes/docs/documentation.md`
2. `/home/dtl/Documents/thes/docs/implementation_plan.md`
3. `/home/dtl/Documents/thes/AGENTS.md`
4. scaffold docs under `/home/dtl/Documents/thes/thesuetvnu/docs`
5. README text, code comments, partial implementations, old notes

Rules:

- `documentation.md` is the authoritative benchmark contract.
- `implementation_plan.md` is the authoritative execution checklist for coders.
- `AGENTS.md` is the stable operational context for future agents.
- If lower-precedence material conflicts with higher-precedence material, higher-precedence material wins.
- If implementation requires a real scope change, update `documentation.md` first or in the same patch. Never change behavior first and explain it later.

## Project Snapshot

`dq-alert-benchmark` is a reproducible benchmark for `profile-based`, `batch-based`, `tabular` data-quality alerting on public datasets.

The project is designed to compare detector families under a locked protocol:

- fixed public snapshots
- fixed calibration/evaluation split policy
- fixed fault-family definitions
- fixed alert matching rules
- fixed metrics
- fixed baseline set
- fixed artifact and reproducibility requirements

The scientific purpose is to answer:

1. which `profile-based` detector families are strongest for which benchmarked failure modes
2. what trade-offs exist across recall, precision, delay, localization, duplicate burden, clean-data false positives, and runtime
3. how stable rankings remain across the included operational domains

This project is not:

- a universal benchmark for all data-quality systems
- a row-level detector benchmark
- a repair framework
- a root-cause analysis system
- a streaming benchmark
- a deep-learning project
- a domain-specific semantics engine for arbitrary custom business rules

## Locked Benchmark Scope

Agents should assume the following are fixed unless `documentation.md` is intentionally revised.

### Domains

- `NYC TLC` as a core domain
- `BTS On-Time` as a core domain
- `Chicago Food` as a core domain
- `NYC 311` as an external validation case study
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

- `NYC TLC`: `150` dirty runs + `1` clean run
- `BTS On-Time`: `150` dirty runs + `1` clean run
- `Chicago Food`: `120` dirty runs + `1` clean run
- `423` total benchmark runs
- `2115` detector executions for the `5` locked baselines

## Canonical Benchmark Contract

Agents must preserve these benchmark truths:

- Detectors consume canonical `batch profiles`, not raw rows directly.
- Feature families are fixed by the spec, including `row_count`, `null_ratio`, `duplicate_ratio`, `min/max`, `range_violation_ratio`, and `invalid_fk_ratio`.
- Monitored scope catalogs are part of the public benchmark contract, not an implementation detail.
- Calibration uses the first `30%` of chronological batches with a minimum of `24`, then applies cleanliness screening.
- Thresholds are derived from clean calibration scores only.
- Dirty conditions are sampled only from the evaluation pool.
- External validation tracks are reported separately from the primary leaderboard.
- The `BTS` appendix uses weak labels and discrepancy windows. It is supplementary and must never be merged into the primary leaderboard.
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

- `/home/dtl/Documents/thes/docs`
  - benchmark-level documents outside the implementation scaffold
  - authoritative spec lives in `documentation.md`
  - implementation checklist lives in `implementation_plan.md`
- `/home/dtl/Documents/thes/thesuetvnu`
  - main implementation scaffold for the benchmark artifact

Implementation scaffold layout inside `thesuetvnu`:

- `/home/dtl/Documents/thes/thesuetvnu/src/dqbench`
  - Python package root for benchmark implementation
  - benchmark runtime code should live here
- `/home/dtl/Documents/thes/thesuetvnu/configs`
  - config-driven control plane
  - expected areas: datasets, faults, detectors, calibrations, experiments
- `/home/dtl/Documents/thes/thesuetvnu/data`
  - local data workspace
  - expected areas: raw, external, interim, processed, ground_truth
- `/home/dtl/Documents/thes/thesuetvnu/outputs`
  - generated benchmark outputs
  - expected areas: runs, reports, figures
- `/home/dtl/Documents/thes/thesuetvnu/scripts`
  - acquisition, checks, orchestration, and reporting entry points
- `/home/dtl/Documents/thes/thesuetvnu/tests`
  - verification layer
  - expected grouping: contracts, evaluation, injection, orchestration
- `/home/dtl/Documents/thes/thesuetvnu/docs`
  - supporting internal scaffold documentation
- `/home/dtl/Documents/thes/thesuetvnu/refs`
  - external references, copied notes, benchmark support material

Runtime architecture intent:

1. acquire and freeze public snapshots
2. canonicalize data and build the canonical batch index
3. publish monitored scope catalogs
4. generate frozen calibration/evaluation splits
5. inject benchmark faults and record incident-level ground truth
6. compute canonical batch profiles
7. run locked baselines or third-party detectors on the same interface
8. match alerts to incidents and compute locked metrics
9. aggregate statistics and publish artifact outputs

## Implementation Order Agents Must Respect

Do not jump ahead and improvise. Follow the dependency order from `implementation_plan.md`.

1. freeze constants, identifiers, schemas, and contracts
2. implement dataset acquisition and raw snapshot manifests
3. canonicalize domains and publish monitored scope catalogs
4. freeze calibration/evaluation split generation and cleanliness reports
5. implement fault injection and incident manifests
6. implement canonical batch profiling
7. implement the five locked baselines
8. implement alert normalization, matching, and metrics
9. implement `NYC 311` external validation and the `BTS` supplementary appendix
10. implement orchestration, aggregation, statistics, and release packaging

If a phase depends on artifacts from an earlier phase, do not fake or hand-wave the earlier phase just to keep moving.

## Code and Documentation Conventions

- Use the `src` layout. Production Python code belongs under `/home/dtl/Documents/thes/thesuetvnu/src/dqbench`.
- Keep implementation config-driven. Dataset, detector, fault, calibration, and experiment behavior should live in `configs/` and manifests when possible.
- Prefer deterministic execution. Freeze seeds, snapshot identifiers, split definitions, manifests, and checksums wherever the spec requires them.
- Follow `snapshot-first` reproducibility. Do not center the benchmark around live API calls when frozen public snapshots are required.
- Favor explicit schemas and manifests over implicit behavior.
- Keep baseline naming scientifically honest. A representative family baseline is not a vendor engine unless the spec explicitly says so.
- Keep dependencies inspectable and minimal unless the spec or implementation need justifies expansion.
- Keep tests aligned to benchmark contracts rather than generic unit-test vanity.
- Keep all artifact names and metric names consistent with the spec. Do not create alternate spellings for the same concept.

## Non-Negotiable Rules

- Always follow `/home/dtl/Documents/thes/docs/documentation.md` when implementing benchmark logic.
- Never silently scale down the benchmark and present it as paper-scale complete.
- Never replace a locked baseline, domain, metric, fault family, or artifact requirement without updating the spec.
- Never let detectors use raw-row access, hidden labels, benchmark-private metadata, or side channels if the public contract does not allow it.
- Never merge `NYC 311` external validation or the `BTS` appendix into the primary leaderboard or inferential ranking tables.
- Never treat weak labels as exact incident ground truth.
- Never skip calibration cleanliness just because the acquisition pipeline is inconvenient.
- Never omit monitored scope catalogs, manifests, checksums, or schema validation if the spec requires them.
- Never report pilot-scale shortcuts as if they satisfy the full release gate.
- Never use placeholders that look final. If something is partial, mark it clearly as partial.
- Never allow a change in code behavior to drift away from docs and configs. Sync them in the same work.

## Common Failure Patterns To Avoid

Agents should actively guard against these mistakes:

- implementing a detector on raw tables because it feels easier than honoring the batch-profile interface
- using only a subset of fault families but forgetting to label the run as partial
- skipping `fk_break` where it is required by the domain-fault matrix
- treating multi-alert detector output as leaderboard-ready without deterministic single-alert reduction
- skipping zero-row scheduled batches in the canonical batch index
- deriving thresholds from dirty or evaluation data instead of screened-clean calibration scores
- changing runtime measurement boundaries without updating the documented contract
- publishing attractive figures while machine-readable manifests or schema reports are missing
- substituting library defaults where the spec locks explicit hyperparameters or policies
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

## Change Management Rules

If an agent discovers ambiguity, a missing decision, or a conflict:

1. check `documentation.md`
2. check `implementation_plan.md`
3. check `AGENTS.md`
4. inspect existing code and configs
5. if the ambiguity still matters, resolve it in the narrowest honest way
6. if resolution changes benchmark semantics, update `documentation.md` first or in the same patch

Do not invent a broad interpretation when a narrow interpretation keeps the benchmark scientifically honest.

## Practical Reminders For Future Agents

- Before implementing, re-read the relevant section of `/home/dtl/Documents/thes/docs/documentation.md`.
- Before starting a new phase, verify that the previous phase's deliverables exist or are being created in the same work.
- Before claiming something is done, check whether the spec also requires:
  - a config artifact
  - a machine-readable output
  - a manifest or checksum
  - a calibration or injection contract
  - a schema validator
  - a test or release-gate hook
- If code, docs, and manifests disagree, stop and resolve the inconsistency.
- When in doubt, prefer being narrower, explicit, and reproducible rather than broader, clever, or under-specified.
