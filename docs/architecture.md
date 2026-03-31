# Architecture Drawing Prompt

Use the prompt below when asking an AI tool to refine the architecture of this project.
It is intentionally limited to the **runtime system flow** from **data preparation** to **metrics**.

## Prompt

```text
Refine the current architecture diagram for dq-alert-benchmark into a final polished version.

The goal is a clean, professional software architecture flow that shows only the runtime system from data preparation to metrics.
Do not show CLI entry points, shell scripts, tests, docs, config files, manifests as external actors, or any reporting/statistical analysis after metrics.

This must look like an architecture diagram, not a code call graph.
Do not use source-code function names anywhere.
Do not use compact class-like labels or CamelCase-only labels as the primary wording.
Use full, human-readable labels with spaces.

Examples:
- Use `Dataset Adapters`, not `DatasetAdapters`
- Use `Canonical Dataframe`, not `CanonicalDataframe`
- Use `Batch Splitter`, not `BatchSplitter`
- Use `Incident Records`, not `IncidentRecords`
- Use `Metrics Output`, not `MetricsOutput`

Important fixes to apply to the current draft:

1. Replace all compact labels with full readable labels that contain spaces.
2. Use full stage names:
- Data Preparation
- Fault Injection & Ground Truth
- Batch Profiling
- Detection & Alert Generation
- Incident-Aware Evaluation & Metrics
3. Keep a strict visual grammar:
- Processing components = rounded rectangles
- Data artifacts = ellipses, documents, or datastore-style shapes
- Stage containers = dashed boxes
4. Place `Incident-Aware Evaluation & Metrics` near the center-bottom, directly under `Detection & Alert Generation`, to reduce very long vertical connector lines.
5. Ensure `Dirty Batch Index` flows into `Metrics Engine`, not into `Matching Engine`.
6. Insert `Match Results` as an explicit artifact between `Matching Engine` and `Metrics Engine`.
7. Reduce crossing lines and unnecessary long side-routing wherever possible.

Use exactly these stages and blocks:

1. Data Preparation
- Dataset Adapters
- Canonical Dataframe
- Batch Index
- Batch Splitter
- Calibration Dataframe
- Evaluation Seed Dataframe

Required flow:
- Dataset Adapters -> Canonical Dataframe
- Dataset Adapters -> Batch Index
- Canonical Dataframe + Batch Index -> Batch Splitter
- Batch Splitter -> Calibration Dataframe
- Batch Splitter -> Evaluation Seed Dataframe

2. Fault Injection & Ground Truth
- Fault Injector
- Dirty Dataframe
- Dirty Batch Index
- Incident Records

Required flow:
- Evaluation Seed Dataframe + Batch Index -> Fault Injector
- Fault Injector -> Dirty Dataframe
- Fault Injector -> Dirty Batch Index
- Fault Injector -> Incident Records

3. Batch Profiling
- Profiling Engine
- Calibration Profiles
- Evaluation Profiles

Required flow:
- Calibration Dataframe -> Profiling Engine -> Calibration Profiles
- Dirty Dataframe -> Profiling Engine -> Evaluation Profiles

4. Detection & Alert Generation
- Detection Engine
- Calibration Scores
- Evaluation Scores
- Thresholding Policy
- Alert Records

Required flow:
- Calibration Profiles -> Detection Engine -> Calibration Scores
- Evaluation Profiles -> Detection Engine -> Evaluation Scores
- Calibration Scores -> Thresholding Policy
- Evaluation Scores + Thresholding Policy -> Alert Records

5. Incident-Aware Evaluation & Metrics
- Matching Engine
- Match Results
- Metrics Engine
- Metrics Output

Required flow:
- Alert Records + Incident Records -> Matching Engine
- Matching Engine -> Match Results
- Match Results + Dirty Batch Index -> Metrics Engine
- Metrics Engine -> Metrics Output

Important semantic constraints:
- The system is batch-based.
- Fault injection creates the ground-truth incidents.
- Detectors generate alert records from profiled batches.
- Evaluation is incident-aware, not only row-level.
- Matching depends on Alert Records and Incident Records.
- Metrics depend on Match Results plus Dirty Batch Index.
- The diagram should emphasize transformation of data artifacts across stages.

Output requirements:
- One single architecture diagram
- Full labels with spaces
- No abbreviations as primary labels
- No function names
- No CLI, no scripts, no docs, no tests, no reporting after metrics
- Neutral technical visual style
- Clean layout with minimal line crossings
```

## Scope Reminder

- Include: runtime system flow from data preparation to metrics.
- Exclude: CLI, scripts, tests, docs, config plumbing, acquisition plumbing, aggregate reporting, and statistical post-analysis.
