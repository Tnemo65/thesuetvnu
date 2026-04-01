# Final Benchmark Specification

## 1. Benchmark Definition

`dq-alert-benchmark` is a reproducible benchmark for profile-based, batch-based tabular data-quality alerting on public datasets. The benchmark uses a transparent synthetic-injection track to generate incident-level ground truth, an audited clean track to evaluate false positives on untouched data, and separate external-validation tracks to evaluate transfer beyond the injected matrix. Detector families are evaluated with incident-aware, delay-aware, localization-aware, false-positive-aware, runtime-aware, and transfer-aware reporting.

The benchmark is defined by five fixed pillars:

1. a locked protocol for calibration, injection, alerting, and matching
2. a multi-domain benchmark matrix on public datasets
3. a fixed baseline set with explicit provenance levels
4. a multi-track evidence policy combining transparent injection, audited clean evaluation, and separate external validation
5. a reproducible artifact with frozen snapshots, seeds, splits, and outputs

The benchmark is a controlled comparison of detector families that can operate on the canonical benchmark profile interface. It is not a universal benchmark for all data-quality systems, all domain semantics, or all alerting settings.

## 2. Scientific Questions

The benchmark is designed to answer four questions:

1. Which profile-based detector families are strongest for which benchmarked data-quality failure modes?
2. How do detection quality, detection delay, localization quality, false positives on clean data, duplicate alert burden, and runtime trade off?
3. How stable are detector rankings across the included operational domains when the evaluation protocol is held fixed?
4. How well do rankings and thresholds transfer from the injected benchmark matrix to untouched clean data and the fixed external-validation tracks?

## 3. Fixed Scope

The benchmark locks the following scope decisions:

- The benchmark studies `tabular data-quality alerting`, not model training.
- The operational data unit is the `batch`.
- Detectors consume canonical `batch profiles`, not raw rows directly.
- Conclusions are scoped to detectors that can operate on canonical batch profiles plus any declared public support tables.
- Ground truth is recorded at `incident` level.
- Each dirty run contains exactly `one` incident from exactly `one` fault family.
- Evaluation matches alerts to incidents and reports multiple primary metrics rather than a single composite score.
- The primary benchmark uses `six` core domains and `two` external validation case studies.
- The benchmark separates `transparent synthetic`, `audited clean`, and `external validation` evidence rather than treating any one track as sufficient on its own.

The benchmark does not study:

- data repair
- root-cause analysis
- streaming online detection
- unstructured data
- training new deep models
- unrestricted row-level detector APIs or hidden domain-specific side channels outside the benchmark contract

## 4. Domains

### 4.1 Core Domains

| Domain | Primary data source | Support data | Batch unit | Role |
|---|---|---|---|---|
| `NYC TLC` | Yellow Taxi trip records | Taxi zone lookup | Daily | Core domain for transportation operations and reference-backed integrity checks |
| `BTS On-Time` | Airline On-Time Performance | Carrier and airport support tables | Daily | Core domain for operational reporting and history-aware monitoring |
| `Chicago Food` | Food inspection records | Official schema and score semantics | Weekly | Core domain for public-health inspection data and duplicate-oriented validation |
| `NYC Parking Violations` | Parking Violations Issued | Official schema export and data dictionary fields published through NYC Open Data | Daily | Core domain for large-volume civic enforcement operations with strong completeness, timeliness, and duplication monitoring value |
| `NYC HPD Housing Complaints and Violations` | HPD housing maintenance complaints and violation files | HPD open-data documentation and violation-file reference documentation | Daily | Core domain for recurring housing-quality enforcement workflows with complaint-to-violation lifecycle semantics |
| `Chicago Building Permits` | Building permits | Official schema export and permit-field documentation | Daily | Core domain for recurring regulatory permitting operations with strong validity, completeness, and timeliness monitoring value |

The six core domains support claims about heterogeneous public operational domains represented in this release. They are not intended to stand in for every operational domain such as healthcare, finance, or private enterprise data pipelines.

### 4.2 External Validation Domain

| Domain | Role | Reporting policy |
|---|---|---|
| `NYC 311` | External validation case study for weak-label and natural issue analysis in New York City service-request operations | Reported separately from the primary leaderboard |
| `Austin 311` | External validation case study for weak-label and natural issue analysis in a second public service-request ecosystem | Reported separately from the primary leaderboard |

### 4.3 Official Source References

- `NYC TLC`: https://home4.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- `NYC TLC` user guide: https://www.nyc.gov/assets/tlc/downloads/pdf/trip_record_user_guide.pdf
- `NYC TLC` yellow trip data dictionary: https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf
- `NYC TLC` taxi zone lookup: https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
- `BTS On-Time` release information: https://www.transtats.bts.gov/releaseinfo.asp
- `BTS On-Time` database information: https://www.transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EGI&Yv0x=D
- `BTS On-Time` PREZIP archive: https://transtats.bts.gov/PREZIP/
- `Chicago Food` official schema export: https://data.cityofchicago.org/api/views/j8a4-a59k/rows.pdf
- `NYC Parking Violations` open data dataset: https://data.cityofnewyork.us/d/pvqr-7yc4
- `NYC HPD` open data portal: https://www.nyc.gov/site/hpd/about/open-data.page
- `NYC HPD` open violations dataset: https://data.cityofnewyork.us/d/csn4-vhvf
- `Chicago Building Permits` official schema export: https://data.cityofchicago.org/api/views/ydr8-5enu/rows.pdf
- `NYC 311` open data portal: https://data.cityofnewyork.us/Social-Services/311-Service-Requests-for-2010-to-present-New-York-/ar4e-ihmq/about
- `NYC 311` service-request location accuracy assessment: https://www.nyc.gov/assets/oti/downloads/pdf/reports/311-location-accuracy-assessment-2022.pdf
- `NYC 311` reporting FAQ: https://www.nyc.gov/site/311reporting/faq/faq.page
- `Austin 311` department page: https://www.austintexas.gov/department/311
- `Austin 311` service-request portal: https://311.austintexas.gov/
- `Austin 311` developer resources: https://www.austintexas.gov/department/developer-resources
- `FAA ASPM Help` main page: https://www.aspm.faa.gov/aspmhelp/index/Main_Page.html
- `FAA OPSNET` overview: https://www.aspm.faa.gov/aspmhelp/index/Operations_Network_%28OPSNET%29.html
- `DOT OIG` audit on BTS flight delay and cancellation data: https://www.oig.dot.gov/library-item/46490

### 4.4 Domain Inclusion Gate

A dataset is admissible to the paper-scale benchmark only if it satisfies all of the following conditions:

- public acquisition is reproducible through a documented URL or portal workflow
- a public schema reference or data dictionary exists
- the canonicalized snapshot contains at least `80` scheduled batches
- the canonicalized snapshot contains at least `24` calibration batches and at least `40` evaluation batches
- the primary event timestamp and update cadence are documented
- if the benchmark uses support tables, those support tables are public, frozen, checksumed, and achieve at least `95%` clean join coverage on the corresponding key
- the released benchmark snapshot is a contiguous official public window rather than a row-sampled, hand-filtered, or convenience subset

For every admitted core-domain snapshot, the release must additionally publish:

- total canonical fact-row count
- batch-row-count summary with `p05`, `p50`, `p95`, and `max`
- the number of monitored table-scoped and column-scoped targets in the monitored scope catalog

For the locked domains in this specification, the minimum admissible paper-scale window is:

- `NYC TLC`: one contiguous `24-month` window of official monthly trip-record releases
- `BTS On-Time`: one contiguous `24-month` window of official monthly `PREZIP` releases
- `Chicago Food`: one contiguous `104-week` window of the official weekly-updated public dataset
- `NYC Parking Violations`: one contiguous `24-month` event-time window from the full official open-data extract
- `NYC HPD Housing Complaints and Violations`: one contiguous `24-month` event-time window from the full official open-data extract
- `Chicago Building Permits`: one contiguous `24-month` event-time window from the full official open-data extract

Paper-scale releases must use the full official extract for the frozen window. Releases must not downsample rows, prefilter to hand-picked topical subsets, or prune batches for convenience before canonicalization, except for documented column pruning needed to build the canonical fact table.

### 4.5 External Validation Protocol

The `NYC 311` external validation track is executed on one frozen `12-month` snapshot and produces two fixed descriptive reports:

- a `location-quality` case study grounded in the official service-request location accuracy assessment and the 311 reporting FAQ
- a `service-process timeliness` case study grounded in official `Created`, `Closed`, and `Average Days to Close` reporting definitions

The `Austin 311` external validation track is executed on one frozen `12-month` snapshot and produces two fixed descriptive reports:

- a `service-process timeliness` case study grounded in the official Austin 3-1-1 service-request lifecycle and Open311 query interface
- a `request-status consistency` case study grounded in the official Austin 3-1-1 request-status workflow and documented service-request access endpoints

External validation tracks use the same alert schema as the primary benchmark, but they are excluded from the primary leaderboard and from inferential ranking tables.

When weak labels or externally documented issue windows are available in an external-validation domain, the release must additionally report descriptive hit-rate and lead-lag summaries against those weak labels. These summaries remain supplementary and do not alter the primary leaderboard.

Paper-scale releases must use the full official `NYC 311` extract for the frozen `12-month` window. They must not prefilter to hand-picked complaint types, boroughs, or agency slices before case-study construction. Any case-study slice reported from `NYC 311` must be derived from the full frozen window under a published deterministic slice rule.

Paper-scale releases must use the full official `Austin 311` extract or the full official Open311 query surface for the frozen `12-month` window. They must not prefilter to hand-picked service-request categories, districts, or departments before case-study construction. Any case-study slice reported from `Austin 311` must be derived from the full frozen window under a published deterministic slice rule.

### 4.6 BTS Audit-Backed Supplementary Validation

The benchmark includes one fixed audit-backed supplementary validation appendix on the `BTS On-Time` core domain. This appendix is reported separately from the injected-condition leaderboard and is designed to strengthen external validity without claiming exact natural-incident ground truth.

The appendix uses:

- one frozen `12-month` `BTS On-Time` snapshot from the primary benchmark
- one frozen `FAA OPSNET` finalized monthly reference extract acquired through the documented public portal workflow
- one fixed discrepancy-window manifest motivated by the `DOT OIG` audit on `BTS` completeness and consistency controls

The appendix produces three fixed outputs:

- an `airport-month disruption consistency` report comparing overlapping `BTS` and `OPSNET` aggregate disruption patterns on aligned airports
- a `reported-cause discrepancy` report on overlapping delay-cause groupings where public definitions permit a cautious alignment
- a weak-label `hit-rate` and `lead-lag` summary over predeclared discrepancy windows derived from the two reports above

For this appendix, supplementary weak-label metrics are fixed as:

- `weak_label_hit_rate = hit_discrepancy_windows / total_discrepancy_windows`
- `weak_label_lead_lag_median = median(first_alert_position - discrepancy_window_start_position)` over hit discrepancy windows

This appendix is supplementary because the reference signals are weak labels rather than exact incident annotations. Its outputs are not merged into the primary leaderboard or inferential ranking tables.

## 5. Benchmark Units

The benchmark uses four fixed units:

- `Batch`: the operational data slice processed by detectors
- `Alert`: one detector output associated with one batch and one scope
- `Incident`: one injected or externally validated data-quality event spanning one or more consecutive batches
- `Condition`: one fully specified benchmark cell `domain x fault_family x severity x duration x seed`

### 5.1 Canonical Batch Index

For every snapshot, the benchmark materializes the full expected batch schedule from the first batch boundary to the last batch boundary in the snapshot range. Scheduled batches with no fact rows remain in the canonical batch index and are represented by profile rows with `row_count = 0`.

This rule is part of the benchmark contract because `freshness_lag` must be observable at the batch timeline itself rather than only through downstream aggregate effects.

### 5.2 Canonical Batch Profile Interface

Every detector receives the same canonical batch-profile interface. The minimum locked feature family is:

- `row_count`
- `null_ratio__<column>` for monitored completeness columns
- `duplicate_ratio`
- `min__<column>` and `max__<column>` for monitored numeric columns
- `range_violation_ratio__<column>` for monitored validity columns
- `invalid_fk_ratio__<column>` for monitored reference-backed columns

Feature availability is domain-specific, but feature semantics are fixed across domains.

### 5.3 Monitored Scope Catalog

Every paper-scale release must publish a monitored scope catalog for each domain. The catalog is part of the benchmark contract and enumerates:

- monitored completeness columns
- monitored numeric validity columns and the source of their valid ranges
- duplicate definition or duplicate-key policy
- monitored foreign-key columns and their declared public support tables
- batch schedule and calendar construction policy
- the admissible target-scope sampling frame for each fault family

## 6. Fault Families

| Fault family | Data-quality dimension | Target scope | Target profile feature | Severity rule |
|---|---|---|---|---|
| `null_spike` | Completeness | Column | `null_ratio` of the target column | Robust effect-size band on target feature |
| `range_violation` | Validity | Column | `range_violation_ratio` of the target column | Robust effect-size band on target feature |
| `duplicate_burst` | Uniqueness | Table | `duplicate_ratio` | Robust effect-size band on target feature |
| `freshness_lag` | Timeliness | Table | delayed or missing batch units relative to expected schedule | Lag length in batch units |
| `fk_break` | Referential integrity | Column with validated reference metadata | `invalid_fk_ratio` of the target column | Robust effect-size band on target feature |

The full benchmark suite covers all five fault families.

The primary cross-domain leaderboard uses the four shared-core families:

- `null_spike`
- `range_violation`
- `duplicate_burst`
- `freshness_lag`

The `fk_break` family is reported as a reference-backed extension on domains that expose public support tables with stable key semantics.

### 6.1 Domain-Fault Matrix

| Domain | null_spike | range_violation | duplicate_burst | freshness_lag | fk_break |
|---|---|---|---|---|---|
| `NYC TLC` | Yes | Yes | Yes | Yes | Yes |
| `BTS On-Time` | Yes | Yes | Yes | Yes | Yes |
| `Chicago Food` | Yes | Yes | Yes | Yes | No |
| `NYC Parking Violations` | Yes | Yes | Yes | Yes | No |
| `NYC HPD Housing Complaints and Violations` | Yes | Yes | Yes | Yes | No |
| `Chicago Building Permits` | Yes | Yes | Yes | Yes | No |
| `NYC 311` | Validation only | Validation only | Validation only | Validation only | No |
| `Austin 311` | Validation only | Validation only | Validation only | Validation only | No |

## 7. Batching and Windowing

The benchmark locks the following batch policies:

- `NYC TLC`: daily batches
- `BTS On-Time`: daily batches
- `Chicago Food`: weekly batches
- `NYC Parking Violations`: daily batches
- `NYC HPD Housing Complaints and Violations`: daily batches
- `Chicago Building Permits`: daily batches
- `NYC 311`: daily batches for case-study analysis
- `Austin 311`: daily batches for case-study analysis

Duration is locked as follows:

- `one_window`: the incident affects exactly one consecutive batch
- `sustained`: the incident affects exactly three consecutive batches

The primary seed set contains `5` random seeds per condition.

## 8. Severity Definition

For `null_spike`, `range_violation`, `duplicate_burst`, and `fk_break`, severity is defined by a robust standardized effect on the target profile feature:

```text
severity_effect = |g_dirty - median(g_clean)| / (1.4826 * MAD(g_clean) + eps)
```

Severity bands are fixed as:

- `low`: `2 <= severity_effect < 4`
- `medium`: `4 <= severity_effect < 8`
- `high`: `severity_effect >= 8`

For `freshness_lag`, severity is defined operationally by lag length in batch units:

- `low`: one batch unit of lag or one missing batch in the incident window
- `medium`: two batch units of lag or two missing batches in the incident window
- `high`: three batch units of lag or three missing batches in the incident window

Injector parameters are tuned per domain and fault family so that the realized dirty profiles fall into the locked severity bands.

### 8.1 Severity Interpretation and Injection Contract

Severity bands are benchmark-control constructs on the designated target feature. They are not claims of equal business impact across domains.

Every paper-scale release must publish, for every `domain x fault_family` pair:

- the operator bank and operator identifiers admissible for that pair
- the injection operator family
- the parameter ranges and seed semantics
- the operator-evidence map linking each released operator to either prior data-quality or anomaly-benchmark literature, an official audit or incident reference, or a declared engineering archetype with written justification
- the predeclared maximum generation attempts per condition
- the edit-budget policy or batch-manipulation policy
- plausibility guards on non-target features
- the target-scope selection policy from the monitored scope catalog

At paper scale, every released `domain x fault_family` pair must expose at least `3` operator identifiers whenever the fault semantics admit three or more realistic constructions. If only `1` or `2` operators are released for a pair, the release must mark that pair as `limited_construction` in the monitored scope catalog and justify the limitation explicitly in the benchmark notes.

Accepted conditions must distribute exposure across the admissible operator bank under a deterministic and approximately balanced rule over the fixed seed set. For any fixed `domain x fault_family x severity x duration` slice, operator exposure counts must differ by at most `1` across admissible operators. Releases must not hand-pick a single favorable operator for an entire slice.

Accepted conditions must also distribute target-batch positions approximately evenly across the evaluation timeline. For any fixed `domain x fault_family` pair, accepted conditions aggregated over the released severity-duration-seed grid must produce evaluation-pool quartile counts that differ by at most `1`. Releases must not concentrate incidents near the end of the snapshot or other favorable timeline regions.

A condition is admissible only if:

- the target batches are sampled randomly from the evaluation pool under the published target-scope sampling frame
- the realized dirty target feature falls inside the locked severity band
- the release records the realized pre-injection and post-injection target-feature values
- the release records the realized non-target side effects and any acceptance or rejection rule used during injection generation

Injector parameter ranges, acceptance rules, and maximum generation attempts must be frozen before detector execution begins. Dirty-run results, clean-track results, and external-validation outcomes must not be used to revise the released injector definition for the same snapshot.

The paper-scale artifact must publish machine-readable injection manifests and realized-severity manifests that let a third party reconstruct:

- the seed used for each accepted condition
- the selected operator identifier
- the selected target scope and target batches
- the realized target-feature shift
- the realized non-target side-effect summary
- the accepted-condition generation-attempt count

The paper-scale artifact must additionally publish an operator-level injection robustness appendix containing:

- accepted-condition counts by operator
- evaluation-timeline quartile counts by operator
- rejected-candidate counts and rejection reasons by operator
- acceptance-rate summaries by operator
- leave-one-operator-out robustness summaries whenever a `domain x fault_family` pair exposes more than one operator

For `freshness_lag`, the release must explicitly state whether lag is implemented as delayed arrival, omitted batch materialization, or both.

## 9. Calibration and Evaluation Protocol

The protocol is fixed as follows:

1. Freeze a public snapshot for each benchmark domain.
2. Canonicalize each dataset into a single fact table plus any declared support tables.
3. Sort batches chronologically.
4. Reserve the first `30%` of batches, with a minimum of `24` batches, as the clean calibration prefix.
5. Deterministically reserve the earliest contiguous `20%` of the post-calibration region, with a minimum of `12` batches, as the untouched clean holdout.
6. Use the remaining post-calibration batches as the dirty evaluation pool.
7. Fit every detector only on clean calibration profiles.
8. Derive alert thresholds from clean calibration scores only.
9. Sample dirty conditions from the dirty evaluation pool only.
10. Measure clean-run false positives on the untouched clean holdout per core domain.

### 9.1 Calibration Cleanliness Contract

The clean calibration prefix is an operational benchmark construct and must be screened rather than assumed. Each release must publish a calibration cleanliness report that records:

- the candidate calibration range
- exact schema or support-table failures removed from calibration
- any excluded batches and the deterministic exclusion rule
- the final count of screened-clean calibration batches

If fewer than `24` screened-clean calibration batches remain after this procedure, the snapshot is inadmissible to the paper-scale benchmark.

### 9.2 Threshold Sensitivity Appendix

The primary leaderboard remains locked to the `percentile_95` calibration policy. Each paper-scale release must additionally publish a threshold-sensitivity appendix over the fixed operating-point grid `p90`, `p95`, and `p99`. This appendix is supplementary and does not alter the primary leaderboard.

### 9.3 Audited Clean Track

Per core domain, the benchmark includes one untouched clean evaluation copy used for clean-run false-positive measurement. This clean track is part of the benchmark contract rather than an optional convenience slice.

The clean track is the deterministic untouched clean holdout defined in the protocol above. It is reserved before dirty-condition generation and must not be chosen post hoc for convenience or reported quality.

Each paper-scale release must additionally publish an audited clean-track protocol that records:

- the untouched clean evaluation range used for the domain
- the deterministic rule used to keep the clean track disjoint from injected conditions
- the predeclared random audit sampling rule over clean batches or monitored scopes
- any official corroboration source or manual-review procedure used to assess sampled clean batches
- the uncertainty or exclusion policy applied when a sampled clean batch cannot be confidently characterized

A `batch-scope` unit is one monitored scope instance, either `table` or `column`, evaluated in one clean-track batch. The audit protocol must sample at least `60` randomly selected batch-scope units per core domain, stratified over the clean-track time range with at least `15` sampled units from each chronological quartile. If the audit finds zero confirmed data-quality issues in those `60` units, the release must report the corresponding one-sided exact `95%` `Clopper-Pearson` upper confidence bound on the hidden-issue rate. If confirmed issues are found, the release must either exclude the affected clean-track units under the published rule or explicitly downgrade the clean-track claim in the release notes.

When a domain exposes both `table`-scoped and `column`-scoped monitored targets, the clean-track audit must include both scope levels and publish sampled-unit counts by scope level.

The audited clean track is used to support `clean_run_fp_batch`, `clean_run_fp_alert`, and threshold-portability interpretation. It does not create extra incident-recall labels.

Per core domain, the release matrix contains:

- `4 shared fault families x 3 severities x 2 durations x 5 seeds = 120` dirty runs
- `fk_break extension`: `3 severities x 2 durations x 5 seeds = 30` dirty runs on domains with validated support tables

This yields:

- `NYC TLC`: `150` dirty runs + `1` clean evaluation run
- `BTS On-Time`: `150` dirty runs + `1` clean evaluation run
- `Chicago Food`: `120` dirty runs + `1` clean evaluation run
- `NYC Parking Violations`: `120` dirty runs + `1` clean evaluation run
- `NYC HPD Housing Complaints and Violations`: `120` dirty runs + `1` clean evaluation run
- `Chicago Building Permits`: `120` dirty runs + `1` clean evaluation run

Across the full paper-scale matrix, this corresponds to:

- `720` shared-core dirty conditions
- `60` `fk_break` extension conditions
- `6` clean evaluation runs
- `786` total benchmark runs
- `3930` detector executions for the five locked baselines
- `4716` detector executions for the six public-code reference detectors
- `8646` detector executions across the full `11`-detector empirical comparison release

## 10. Alert and Incident Semantics

Each detector produces at most one alert record per batch. Every alert record must contain:

- detector identifier
- domain identifier
- batch identifier
- scope level
- scope reference
- scalar score
- calibration policy identifier

Detectors that natively emit multiple alerts per batch must apply a documented deterministic reduction to the single primary alert record used for leaderboard scoring. Richer detector-native outputs may be published as auxiliary artifacts but are not consumed by the primary metrics.

The primary leaderboard therefore scores `single primary operational alerting per batch`, not unrestricted detector-native alert streams. Any detector that natively emits more than one alert per batch must additionally publish a supplementary native-output appendix on its unreduced outputs under the same scope-compatibility table and matching semantics. This appendix is supplementary and does not alter the locked primary leaderboard.

Every incident record must contain:

- fault family
- domain identifier
- severity
- duration
- target scope
- incident start batch
- incident end batch
- detection window start batch
- detection window end batch

For `null_spike`, `range_violation`, `duplicate_burst`, and `fk_break`, the detection window is identical to the incident interval. For `freshness_lag`, the detection window is also identical to the incident interval because the canonical batch index retains expected zero-row batches.

## 11. Scope Compatibility and Matching

The primary benchmark uses two scoring scopes:

- `column`
- `table`

`fk_break` incidents remain column-scoped in the primary evaluation and carry reference metadata for diagnostics.

Compatibility is fixed as follows:

| Incident scope | Valid alert scope | Matching credit |
|---|---|---|
| `column` | exact `column` match | `1.0` |
| `column` | parent `table` match | `0.5` |
| `table` | exact `table` match | `1.0` |
| `table` | `column` match | `0.0` |

Matching uses `greedy earliest-valid-unmatched` logic inside the incident detection window. After the first matched alert for an incident:

- any additional valid alerts for the same incident count toward `duplicate_burden`
- unmatched alerts count against precision
- incidents with no valid matched alert count against recall

## 12. Locked Baselines

All baselines operate on the same batch-profile interface and the same calibration/evaluation split. Support-table lookups are allowed only when the domain and fault family explicitly require them.

The shared calibration policy for the primary benchmark is:

- `percentile_95` threshold on clean calibration scores for each `detector x domain x snapshot`

### 12.1 Baseline Provenance

| Baseline | Detector family | Provenance level | Implementation contract | Notes |
|---|---|---|---|---|
| `Calibration Threshold Lower Bound` | static threshold lower bound | Internal benchmark baseline | Score each batch by the maximum standardized deviation from clean calibration statistics across profile features | Establishes a minimum useful baseline |
| `Constraint-Rule Baseline` | rule-based and expectation-style validation | Representative family baseline | Evaluate declared batch-profile rules and support-table checks, then emit a scalar violation score and the top violated scope | Represents production-style constraint validation without claiming any single vendor engine |
| `History-Based Robust Profile Baseline` | history-aware profile monitoring | Representative family baseline grounded in prior literature | Score each batch by rolling robust deviation from recent historical batch profiles with fixed history window and no label supervision | Captures temporal monitoring behavior under a transparent protocol |
| `EWMA-CUSUM Sequential Baseline` | sequential change monitoring | Standard SPC baseline grounded in quality-control literature | Track standardized profile deviations with fixed two-sided `EWMA` and `CUSUM` recursions, then emit the maximum sequential excursion and responsible scope | Captures low-amplitude sustained shifts that static thresholding can miss |
| `Isolation Forest Baseline` | classical unsupervised anomaly detection | Standard implementation baseline | Use the `scikit-learn` implementation of `IsolationForest` on batch-profile vectors fit on clean calibration data | Serves as the canonical nonparametric ML baseline |

### 12.2 Baseline Fairness Policy

- All baselines see the same canonical batch profiles for a given condition.
- Support-table information is available only when the domain-fault pair explicitly requires it.
- Thresholds are calibrated from clean calibration scores only.
- Hyperparameter settings are fixed per detector family and do not change across fault families within a domain.
- Detector configuration manifests, preprocessing rules, adapter settings, and any reference-detector integration parameters must be frozen before any dirty-run, clean-track, or external-validation outcomes are observed for the released snapshot.
- Dirty-run results, clean-track outcomes, and external-validation outcomes must not be used to revise detector configurations for the same released snapshot.
- State-bearing baselines may initialize only from the clean calibration prefix under a documented deterministic rule.
- Each baseline emits at most one alert per batch.

### 12.3 Baseline Claim Boundaries

- The lower-bound baseline is an internal benchmark baseline.
- The constraint-rule baseline is a representative family baseline and is not claimed as any official external tool engine.
- The history-based baseline is a representative family baseline grounded in prior monitoring literature and is not claimed as author code from any single paper.
- The `EWMA-CUSUM` baseline is a standard sequential-process-control baseline and is not claimed as any vendor implementation.
- The Isolation Forest baseline is a standard implementation baseline because it uses the public `scikit-learn` implementation.
- Baseline quality claims in this benchmark are made only after considering four evidence layers together:
  - contract-valid detector execution on the locked batch-profile interface
  - performance on the transparent injected benchmark matrix
  - false-positive behavior on the audited clean track
  - descriptive transfer behavior on the external-validation tracks
- No baseline or reference detector is claimed to be universally best outside these benchmark conditions.
- Every paper-scale empirical release must additionally report the shipped public-code reference set under the same contract. The appendix-level reference set is:
  - `ECOD`
  - `COPOD`
  - `Extended Isolation Forest`
  - `kNN`
  - `LOF`
  - `One-Class SVM`
- Appendix-level public-code reference detectors are included only when they satisfy all of the following:
  - a public paper or official technical reference exists
  - a public upstream implementation exists and is executed with a pinned released version
  - the benchmark integration is a thin contract adapter rather than a local reimplementation of the detector's core scoring logic
  - either open multi-dataset benchmark evidence exists for the detector family on tabular anomaly detection, or documented deployment evidence exists in recurring data-validation practice
- If this appendix-level public-code reference set is absent, the release is incomplete for empirical comparison and must restrict its interpretation to benchmark-design documentation only.

### 12.4 Third-Party Detector Contract

Third-party detectors are admissible to the benchmark only if they obey the same public benchmark contract:

- the detector consumes the canonical batch-profile interface and any declared public support tables only
- the detector does not access hidden incident labels, unreleased snapshots, or benchmark-private metadata
- the detector emits alerts in the canonical alert schema
- the detector publishes a deterministic configuration manifest and software version

The reproducible artifact must ship supplementary `reference detector adapters` that call public third-party code under this same contract. These adapters are supplementary: they do not change the `5` locked baseline families or the locked run matrix. They remain appendix-level detectors rather than primary-leaderboard baselines, but paper-scale empirical releases must still publish the shipped public-code reference appendix under the release gate. The shipped supplementary reference set is:

- `ECOD`
- `COPOD`
- `Extended Isolation Forest`
- `kNN`
- `LOF`
- `One-Class SVM`

Their provenance, source repositories, paper links, and integration notes are tracked in [`external_reference_detectors.md`](external_reference_detectors.md).

### 12.5 Locked Scoring Definitions

The benchmark fixes the following detector definitions, with `eps = 1e-6`:

`Calibration Threshold Lower Bound`

For every numeric profile feature `j` and batch `t`:

```text
s_tj = |x_tj - median_j(calibration)| / (1.4826 * MAD_j(calibration) + eps)
score_t = max_j s_tj
```

The alert scope is taken from the feature `j` that attains the maximum score.

`Constraint-Rule Baseline`

The rule catalog is fixed to the benchmark feature families:

- completeness rules on `null_ratio`
- validity rules on `range_violation_ratio`
- duplicate rules on `duplicate_ratio`
- freshness rules on `row_count`
- referential-integrity rules on `invalid_fk_ratio` when support tables exist

Hard constraints from public schema references use zero-tolerance rules when the semantics are exact. Soft statistical constraints use fixed calibration quantiles:

- upper-bound anomaly features use `p95(calibration)`
- lower-bound `row_count` uses `p05(calibration)`

Normalized violation is defined as:

```text
upper_violation = max(0, x - u) / max(|u|, 1, eps)
lower_violation = max(0, l - x) / max(|l|, 1, eps)
score_t = max_r violation_t(r)
```

`History-Based Robust Profile Baseline`

The history window is fixed to `8` batches. For each evaluation batch `t`, the history set `H_t` is the previous `8` available batches drawn from the tail of the calibration prefix and earlier evaluation batches in the same run.

```text
h_tj = |x_tj - median_j(H_t)| / (1.4826 * MAD_j(H_t) + eps)
score_t = max_j h_tj
```

The alert scope is taken from the feature `j` that attains the maximum score.

`EWMA-CUSUM Sequential Baseline`

For every numeric profile feature `j` and batch `t`, first standardize against clean calibration statistics:

```text
z_tj = (x_tj - median_j(calibration)) / (1.4826 * MAD_j(calibration) + eps)
```

The baseline then runs fixed two-sided sequential recursions with `lambda = 0.3`, `k = 0.5`, and zero initialization at the start of each run:

```text
ewma_tj = lambda * z_tj + (1 - lambda) * ewma_(t-1)j
cusum_pos_tj = max(0, cusum_pos_(t-1)j + z_tj - k)
cusum_neg_tj = max(0, cusum_neg_(t-1)j - z_tj - k)
score_t = max_j max(|ewma_tj|, cusum_pos_tj, cusum_neg_tj)
```

The alert scope is taken from the feature `j` that attains the maximum score. Table-scoped profile features are treated as table-scoped monitored features under the same rule.

`Isolation Forest Baseline`

The baseline uses the `scikit-learn` `IsolationForest` implementation on the numeric profile vector with fixed hyperparameters:

- `n_estimators = 256`
- `max_samples = min(256, n_calibration_batches)`
- `max_features = 1.0`
- `bootstrap = False`
- `contamination = auto`
- `random_state = 42`

The batch score is:

```text
score_t = -decision_function(x_t)
```

## 13. Metrics and Reporting

### 13.1 Primary Metrics

The primary leaderboard metrics are locked as:

1. `incident_recall`
2. `incident_precision`
3. `incident_f1`
4. `detection_delay_norm_mean`
5. `localization_accuracy_hierarchical`
6. `duplicate_burden`
7. `clean_run_fp_batch`
8. `runtime_per_1m_rows`

### 13.2 Supplementary Metrics

The supplementary metrics are locked as:

- `detection_delay_raw_mean`
- `localization_accuracy_strict`
- `clean_run_fp_alert`
- `runtime_overhead_seconds`
- `weak_label_hit_rate`
- `weak_label_lead_lag_median`

### 13.3 Reporting Policy

The benchmark reports:

- per-domain tables on every primary metric
- a shared-core cross-domain leaderboard on matched conditions across the six core domains
- a dedicated `fk_break` extension table on domains with validated public reference tables
- a separate external validation report for `NYC 311`
- a separate external validation report for `Austin 311`
- a separate `BTS` audit-backed supplementary validation appendix
- a supplementary native-output appendix for any detector that natively emits more than one alert per batch

The benchmark does not publish a single composite score or a single overall winner.

Supplementary metrics inherit the same matching policy and denominator conventions as their primary analogues unless explicitly stated otherwise in the release notes.

### 13.4 Metric Semantics

The primary metrics are defined as:

```text
incident_recall = matched_incidents / total_incidents
incident_precision = matched_incidents / total_alerts
incident_f1 = harmonic_mean(incident_precision, incident_recall)
detection_delay_norm_mean = mean(delay_penalty_i)
localization_accuracy_hierarchical = mean(localization_credit_i)
duplicate_burden = extra_valid_alerts / total_incidents
clean_run_fp_batch = alerted_batches / clean_batches
runtime_per_1m_rows = wall_clock_seconds / (rows_processed / 1_000_000)
```

Conventions are fixed as follows:

- `incident_precision = 0` when `total_alerts = 0`
- `incident_f1 = 0` when `incident_precision + incident_recall = 0`
- `delay_penalty_i = (first_matched_alert_position_i - incident_start_position_i) / incident_window_length_i` when incident `i` is matched
- `delay_penalty_i = 1.0` when incident `i` is unmatched
- `localization_credit_i = 0.0` when incident `i` is unmatched
- `runtime_per_1m_rows` must be reported together with a fixed runtime boundary, hardware specification, thread-count policy, and cache policy

`localization_credit_i` is fixed to:

- `1.0` for an exact valid scope match
- `0.5` for a parent table alert matching a column incident
- `0.0` otherwise

## 14. Statistical Comparison

The matched experimental unit for inferential statistics is the benchmark cell:

```text
domain x fault_family x severity x duration
```

Within every matched cell, the release first aggregates detector metrics across the fixed seed set using the median. The release must additionally publish within-cell seed dispersion summaries.

For each primary metric on the shared-core leaderboard, the release reports:

- `Friedman` omnibus test across detectors
- pairwise `Wilcoxon signed-rank` tests
- `Holm` multiple-testing correction
- `median paired difference`
- `matched rank-biserial correlation`

The `fk_break` extension is reported with the same per-metric inferential protocol on the qualifying extension conditions only. External validation results are reported descriptively and are not merged into the primary inferential ranking table.

### 14.1 Transfer Analysis

Each paper-scale release must additionally publish a supplementary transfer-analysis section. This section does not alter the primary leaderboard, but it is required to support claim boundaries about benchmark-to-reality transfer.

The transfer-analysis section must report:

- a fixed `injected incident rank` per detector, defined as the mean detector rank over:
  - `incident_f1` descending
  - `detection_delay_norm_mean` ascending
  - `localization_accuracy_hierarchical` descending
- leave-one-domain-out `domain-transfer` summaries in which detector ranks on the held-out core domain are compared against detector ranks aggregated on the other five core domains using `Spearman` and `Kendall`
- `injected-to-clean` rank correlation in which the `injected incident rank` is compared against the audited clean-track detector rank induced by `clean_run_fp_batch`
- `injected-to-BTS-weak-label` rank correlation in which the `injected incident rank` is compared against the detector rank induced by `weak_label_hit_rate` on the fixed `BTS` appendix
- threshold-portability summaries showing how thresholds fit on the clean calibration prefix behave on the untouched clean track, the `NYC 311` case-study track, the `Austin 311` case-study track, and the `BTS` appendix by reporting alerted-batch rates and their absolute gaps relative to the audited clean track

`NYC 311` and `Austin 311` remain descriptive external-validation case studies and are not used for rank-correlation transfer unless this specification locks an exact scalar validation target for those tracks. If a transfer summary cannot be computed because the required fixed validation scalar is unavailable, the release must say so explicitly and still publish the remaining fixed transfer summaries. Transfer analyses are descriptive robustness checks. They do not override the locked primary leaderboard or convert weak-label validation into exact-ground-truth inference.

## 15. Artifact Policy

### 15.1 Artifact Goal

The benchmark artifact is designed for third-party reproduction of data acquisition, condition generation, detector execution, and evaluation outputs.

### 15.2 Snapshot Policy

The artifact uses a strict `snapshot-first` policy.

For every released dataset snapshot, the artifact must publish:

- dataset identifier
- snapshot identifier
- snapshot date
- source URL or source portal page
- schema version reference
- checksum for every released raw file
- support-table checksums when support tables are part of the benchmark contract

### 15.3 Public Release Contents

A paper-scale artifact release contains:

- benchmark source code
- executable configuration files for every released condition
- seed lists
- data acquisition scripts
- monitored scope catalogs
- injection manifests and realized-severity manifests
- operator-evidence maps
- calibration cleanliness reports
- audited clean-track protocol and audit outputs
- strict `Pydantic` models for configs, manifests, and non-tabular benchmark outputs
- `Pandera` schemas for canonical dataframes, batch profiles, alerts, incidents, matches, and metrics
- manifests and checksums
- frozen calibration and evaluation split definitions
- containerized runtime environment with pinned dependencies
- one-command entry points for the pilot and full paper-scale suites
- runtime measurement policy and hardware manifest
- detector adapter template and output-schema validator
- machine-readable schema-validation reports
- output schemas for alerts, incidents, matches, and metrics
- aggregated benchmark tables used in the paper
- transfer-analysis tables and summaries
- domain-scale disclosure tables
- detector-native multi-alert appendix outputs where applicable

### 15.4 Raw Data Policy

Raw data files are redistributed only when the source license permits redistribution. When redistribution is not permitted, the artifact must still publish:

- acquisition procedure
- exact source references
- checksums for verification
- expected local directory structure

### 15.5 Required Outputs Per Run

Each run must materialize the following machine-readable outputs:

- `alerts`
- `incidents`
- `matches`
- `metrics`
- `schema_validation`

Each detector submission must additionally materialize:

- detector configuration manifest
- software version manifest
- runtime environment manifest
- detector-native alert appendix outputs when native multi-alert behavior exists

Each paper-scale release must additionally materialize:

- per-domain summary tables
- shared-core cross-domain leaderboard tables
- `fk_break` extension tables
- `NYC 311` external validation case-study outputs
- `Austin 311` external validation case-study outputs
- `BTS` audit-backed supplementary validation outputs
- audited clean-track outputs
- transfer-analysis outputs
- domain-scale disclosure outputs

## 16. Paper-Scale Release Gate

A release qualifies as `paper-scale` only if all of the following hold:

- the locked design in this file is executed without scope drift
- all six core domains are executed under the locked protocol
- all released datasets satisfy the domain inclusion gate in this file
- the shared-core leaderboard is reported on matched conditions across the core domains
- the `fk_break` extension is reported on every domain with validated public support tables
- all five locked baseline families are executed
- all six public-code reference detectors are executed under the appendix contract
- all eight primary metrics are reported for every benchmark condition
- clean-run false-positive evaluation is included
- monitored scope catalogs, injection manifests, and calibration cleanliness reports are published
- operator-evidence maps and operator-level robustness appendix outputs are published
- the audited clean track is published with its protocol and audit outputs
- runtime boundary and hardware policy are published
- threshold-sensitivity appendix is published
- detector configuration manifests are frozen and not revised after observing dirty-run, clean-track, or external-validation outcomes
- inferential statistics are reported on the shared-core leaderboard
- the `NYC 311` external validation track is published with both descriptive reports
- the `Austin 311` external validation track is published with both descriptive reports
- the `BTS` audit-backed supplementary validation appendix is published
- transfer-analysis outputs are published
- the shipped public-code reference-detector appendix is published
- any detector with native multi-alert behavior publishes the supplementary native-output appendix
- all released configs and benchmark outputs pass strict schema validation
- the reproducible artifact is published with manifests, checksums, frozen splits, seeds, executable configs, aggregate tables, and detector-submission validation utilities
