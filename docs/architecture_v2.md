# Architecture v2

## Purpose

This file defines the current architecture view for `dq-alert-benchmark` in a way that is consistent with the authoritative benchmark specification.

It exists because the older `architecture.md` is intentionally limited to a runtime-only diagram prompt, while the current project now has additional benchmark-critical architecture concerns:

- snapshot-first acquisition
- monitored scope catalogs
- calibration cleanliness
- fixed baseline execution
- external validation tracks
- supplementary `BTS` audit-backed appendix
- artifact and release-gate outputs

## Source of Truth

Use the following precedence when this file is read together with other project documents:

1. `docs/documentation.md`
2. `docs/implementation_plan.md`
3. `AGENTS.md`
4. `docs/architecture_v2.md`
5. `docs/architecture.md`

This file explains the architecture implied by the spec. It does not override the spec.

## System Boundary

The benchmark system includes:

- public dataset acquisition and snapshot freeze
- canonicalization into fact tables and support tables
- canonical batch index generation
- monitored scope catalog publication
- calibration and evaluation split generation
- calibration cleanliness screening
- fault injection and incident ground-truth generation
- canonical batch profiling
- detector execution on the locked batch-profile interface
- alert normalization, matching, and metric computation
- external validation and supplementary weak-label validation
- aggregation, statistics, artifact packaging, and release-gate verification

The benchmark system does not include:

- data repair
- root-cause analysis
- unrestricted raw-row detector APIs
- hidden labels or benchmark-private side channels
- deep-model training pipelines
- streaming online alerting

## Architecture Summary

The project should be understood as two related architectures:

1. `Project Architecture`
   - the full benchmark system needed to produce a paper-scale release
2. `Runtime Core Architecture`
   - the narrower dataflow from canonical data to alerts, matches, and metrics

Both views are valid, but they answer different questions.

## 1. Project Architecture

The full project architecture consists of nine layers.

### 1.1 Specification and Contracts Layer

Responsibilities:

- lock domains, fault families, baselines, metrics, and run matrix
- define schemas, manifests, and output contracts
- enforce source-of-truth precedence

Primary artifacts:

- benchmark specification
- implementation checklist
- benchmark constants
- `Pydantic` models
- `Pandera` schemas

### 1.2 Acquisition and Snapshot Layer

Responsibilities:

- reproducibly acquire public source snapshots
- freeze source references, snapshot identifiers, and checksums
- freeze support tables used by the benchmark contract
- apply domain inclusion gates

Primary inputs:

- `NYC TLC`
- `BTS On-Time`
- `Chicago Food`
- `NYC 311`
- `FAA OPSNET`

Primary artifacts:

- raw snapshots
- raw snapshot manifests
- support-table manifests
- domain inclusion gate reports

### 1.3 Canonicalization and Scope Layer

Responsibilities:

- canonicalize each admitted domain into one fact table plus declared support tables
- build the full canonical batch index, including zero-row scheduled batches
- publish monitored scope catalogs per domain

Primary artifacts:

- canonical fact tables
- support tables
- canonical batch index
- monitored scope catalogs

### 1.4 Split and Calibration Layer

Responsibilities:

- sort batches chronologically
- create the calibration prefix and evaluation pool
- screen the calibration prefix for cleanliness
- freeze split definitions

Primary artifacts:

- frozen calibration split definitions
- frozen evaluation split definitions
- calibration cleanliness reports

### 1.5 Condition Generation Layer

Responsibilities:

- generate benchmark conditions from the evaluation pool
- apply the five fault families
- enforce severity-band validity
- materialize incident truth and injection manifests

Primary artifacts:

- dirty canonical data
- dirty batch indices when needed
- injection manifests
- incident records
- realized-severity manifests

### 1.6 Profiling and Detection Layer

Responsibilities:

- compute canonical batch profiles
- run the five locked baselines
- admit third-party detectors only through the same public contract
- calibrate thresholds using clean calibration scores only

Primary artifacts:

- calibration profiles
- evaluation profiles
- calibration scores
- evaluation scores
- threshold artifacts
- alert records

### 1.7 Evaluation and Metrics Layer

Responsibilities:

- normalize detector-native outputs into the canonical alert schema
- apply deterministic single-alert reduction where required
- match alerts to incidents using the locked matching policy
- compute primary and supplementary metrics

Primary artifacts:

- alerts
- matches
- metrics
- runtime manifests
- schema-validation reports

### 1.8 Validation and Analysis Layer

Responsibilities:

- produce per-domain benchmark tables
- produce shared-core leaderboard tables
- produce `fk_break` extension tables
- run inferential statistics on shared-core matched cells
- publish `NYC 311` external validation outputs
- publish the `BTS` audit-backed supplementary appendix

Primary artifacts:

- per-domain tables
- shared-core leaderboard tables
- `fk_break` extension tables
- inferential statistics outputs
- `NYC 311` validation outputs
- `BTS` appendix outputs

### 1.9 Artifact and Release Layer

Responsibilities:

- package code, configs, manifests, checksums, split definitions, and outputs
- provide detector submission utilities
- verify the paper-scale release gate

Primary artifacts:

- release bundles
- containerized runtime environment
- hardware and runtime boundary manifests
- detector adapter templates
- output-schema validators
- release-gate verification reports

## 2. Project Architecture Flow

The full benchmark system follows this ordered flow:

1. benchmark contracts are frozen
2. public datasets and support tables are acquired and frozen
3. admitted datasets are canonicalized
4. canonical batch indices and monitored scope catalogs are published
5. calibration and evaluation splits are frozen
6. calibration cleanliness is screened and recorded
7. benchmark conditions are generated through controlled fault injection
8. canonical batch profiles are computed
9. detectors produce alerts under the locked calibration policy
10. alerts are matched to incidents and metrics are computed
11. external validation and supplementary appendix outputs are produced
12. benchmark tables, statistics, and artifact bundles are released

## 3. Runtime Core Architecture

The runtime core is narrower than the full project architecture. It begins after acquisition and contract freezing are already in place.

### 3.1 Runtime Stages

1. `Canonical Data Preparation`
2. `Calibration and Evaluation Split`
3. `Fault Injection and Ground Truth`
4. `Batch Profiling`
5. `Detection and Alert Generation`
6. `Incident-Aware Evaluation and Metrics`

### 3.2 Runtime Blocks

`Canonical Data Preparation`

- Dataset Adapters
- Canonical Fact Table
- Support Tables
- Canonical Batch Index
- Monitored Scope Catalog

`Calibration and Evaluation Split`

- Calibration Splitter
- Calibration Cleanliness Screen
- Calibration Dataframe
- Evaluation Pool Dataframe
- Calibration Cleanliness Report

`Fault Injection and Ground Truth`

- Fault Injector
- Dirty Dataframe
- Dirty Batch Index
- Incident Records
- Injection Manifest

`Batch Profiling`

- Profiling Engine
- Calibration Profiles
- Evaluation Profiles

`Detection and Alert Generation`

- Detection Engine
- Calibration Scores
- Evaluation Scores
- Thresholding Policy
- Alert Records

`Incident-Aware Evaluation and Metrics`

- Matching Engine
- Match Results
- Metrics Engine
- Metrics Output

### 3.3 Required Runtime Flow

- Dataset Adapters -> Canonical Fact Table
- Dataset Adapters -> Support Tables
- Dataset Adapters -> Canonical Batch Index
- Canonical Fact Table + Canonical Batch Index -> Calibration Splitter
- Calibration Splitter -> Calibration Cleanliness Screen
- Calibration Cleanliness Screen -> Calibration Dataframe
- Calibration Cleanliness Screen -> Evaluation Pool Dataframe
- Calibration Cleanliness Screen -> Calibration Cleanliness Report
- Evaluation Pool Dataframe + Canonical Batch Index + Monitored Scope Catalog -> Fault Injector
- Fault Injector -> Dirty Dataframe
- Fault Injector -> Dirty Batch Index
- Fault Injector -> Incident Records
- Fault Injector -> Injection Manifest
- Calibration Dataframe -> Profiling Engine -> Calibration Profiles
- Dirty Dataframe -> Profiling Engine -> Evaluation Profiles
- Calibration Profiles -> Detection Engine -> Calibration Scores
- Evaluation Profiles -> Detection Engine -> Evaluation Scores
- Calibration Scores -> Thresholding Policy
- Evaluation Scores + Thresholding Policy -> Alert Records
- Alert Records + Incident Records -> Matching Engine
- Matching Engine -> Match Results
- Match Results + Dirty Batch Index -> Metrics Engine
- Metrics Engine -> Metrics Output

## 4. Architecture Constraints

Any future diagram or implementation explanation must preserve the following:

- the system is `batch-based`
- detectors consume canonical `batch profiles`
- fault injection creates incident-level ground truth
- zero-row scheduled batches remain in the canonical batch index
- calibration cleanliness is a first-class benchmark step
- thresholds come from clean calibration scores only
- each dirty run contains exactly one incident from exactly one fault family
- external validation is separate from the primary leaderboard
- the `BTS` appendix is supplementary and weak-label-based
- all built-in baselines and third-party detectors must obey the same public detector contract

## 5. Diagram Guidance

If the team wants diagrams, produce two diagrams instead of one overloaded figure.

### Diagram A: Full Project Architecture

Use this when explaining the benchmark as a reproducible research artifact.

Include:

- contracts and schemas
- acquisition and snapshot freeze
- canonicalization and scope catalogs
- split and calibration screening
- fault injection and incidents
- profiling and detector execution
- evaluation and metrics
- external validation and `BTS` appendix
- artifact packaging and release gate

Exclude:

- source-code function names
- low-level class names
- test internals

### Diagram B: Runtime Core Architecture

Use this when explaining the operational flow from canonical data to metrics.

Include:

- canonical data preparation
- calibration/evaluation split
- fault injection and ground truth
- batch profiling
- detection and alert generation
- incident-aware evaluation and metrics

Exclude:

- acquisition plumbing
- artifact packaging
- release-gate checks
- statistical post-analysis after metrics

## 6. Recommended Naming Style

Prefer full human-readable labels with spaces:

- `Canonical Fact Table`
- `Support Tables`
- `Canonical Batch Index`
- `Calibration Cleanliness Screen`
- `Monitored Scope Catalog`
- `Incident Records`
- `Alert Records`
- `Match Results`
- `Metrics Output`

Avoid compact code-shaped labels as primary diagram wording.

## 7. Status

This file is the preferred architecture reference for current project-aligned explanations.

The older `docs/architecture.md` may still be useful as a narrow runtime-diagram prompt, but it should not be treated as the complete architecture description of the current benchmark.
