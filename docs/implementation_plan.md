# Implementation Plan

Checklist này là bản triển khai chi tiết cho coder follow khi xây `dq-alert-benchmark`.

Nguồn chân lý duy nhất cho checklist này là:

- `docs/documentation.md`

Checklist này:

- không dựa vào hiện trạng code hiện tại
- không mở rộng scope ngoài spec
- không thay spec bằng prompt implement
- được sắp theo thứ tự phụ thuộc để tránh miss việc

Quy ước audit:

- Chỉ tick khi repo hiện tại đã có bằng chứng rõ ràng bằng code, config, contract, test, hoặc doc governance đã khóa xong.
- Nếu mới chỉ là scaffold, partial flow, hoặc chưa được verify đủ mức checklist yêu cầu thì để trống.

## Cách dùng

- Chỉ bắt đầu phase tiếp theo khi deliverables của phase hiện tại đã được khóa.
- Không đánh dấu xong nếu chưa có artifact machine-readable hoặc test tương ứng khi checklist yêu cầu.
- Nếu phát hiện vướng mắc làm thay đổi scope, cập nhật `documentation.md` trước hoặc đồng thời với implementation.

## Phase 0. Freeze Benchmark Contract

### 0.1 Benchmark constants

- [x] Khóa toàn bộ benchmark constants thành machine-readable config hoặc constants module:
  - [x] `6` core domains
  - [x] `2` external validation domains
  - [x] `1` BTS audit-backed supplementary appendix
  - [x] `5` fault families
  - [x] `5` locked baselines
  - [x] `6` public-code reference detectors
  - [x] `8` primary metrics
  - [x] `5` seeds per condition
  - [x] `2` durations
  - [x] `3` severities
- [x] Khóa toàn bộ benchmark identifiers:
  - [x] `domain`
  - [x] `fault_family`
  - [x] `severity`
  - [x] `duration`
  - [x] `scope_level`
  - [x] `batch_unit`
  - [x] `calibration_policy`

### 0.2 Run matrix and release gate

- [x] Khóa run matrix:
  - [x] `NYC TLC`: `150` dirty runs + `1` clean run
  - [x] `BTS On-Time`: `150` dirty runs + `1` clean run
  - [x] `Chicago Food`: `120` dirty runs + `1` clean run
  - [x] `NYC Parking Violations`: `120` dirty runs + `1` clean run
  - [x] `NYC HPD Housing Complaints and Violations`: `120` dirty runs + `1` clean run
  - [x] `Chicago Building Permits`: `120` dirty runs + `1` clean run
  - [x] `786` total benchmark runs
  - [x] `3930` detector executions cho `5` locked baselines
  - [x] `4716` detector executions cho `6` public-code reference detectors
  - [x] `8646` detector executions cho full `11`-detector empirical comparison release
- [x] Chuyển paper-scale release gate thành checklist machine-checkable.
- [x] Chuyển artifact requirements thành checklist machine-checkable.

### 0.3 Contracts and schemas

- [x] Định nghĩa strict `Pydantic` models cho:
  - [x] snapshot manifest
  - [x] monitored scope catalog
  - [x] calibration cleanliness report
  - [x] injection manifest
  - [x] detector configuration manifest
  - [x] runtime manifest
  - [x] schema validation report
- [x] Định nghĩa `Pandera` schemas cho:
  - [x] canonical dataframe
  - [x] support tables
  - [x] canonical batch index
  - [x] calibration profiles
  - [x] evaluation profiles
  - [x] alerts
  - [x] incidents
  - [x] matches
  - [x] metrics
- [x] Khóa canonical output schemas cho:
  - [x] `alerts`
  - [x] `incidents`
  - [x] `matches`
  - [x] `metrics`
  - [x] `schema_validation`
- [x] Khóa third-party detector contract:
  - [x] input chỉ gồm canonical batch profiles + declared public support tables
  - [x] không truy cập hidden labels hoặc benchmark-private metadata
  - [x] output phải đúng canonical alert schema
  - [x] detector phải xuất config manifest + software version

### Deliverables

- [x] benchmark constants manifest
- [x] enum/identifier definitions
- [x] strict `Pydantic` models
- [x] `Pandera` schemas
- [x] release-gate checklist machine-readable

### 0.4 Repo-doc sync audit

- [x] Audit `machine-readable benchmark constants` against `docs/documentation.md`:
  - [x] `configs/benchmark/constants.yaml`
  - [x] `src/dqbench/contracts/benchmark.py`
- [x] Audit `machine-readable release gate` against `docs/documentation.md`:
  - [x] `configs/benchmark/release_gate.yaml`
  - [x] `configs/benchmark/artifact_requirements.yaml`
- [x] Audit acquisition/setup surface against locked dataset scope:
  - [x] `configs/acquisition/*.yaml`
  - [x] `configs/datasets/*.yaml`
  - [x] `scripts/download_snapshots.py`
  - [x] `src/dqbench/data/acquisition.py`
- [x] Audit detector/config surface against locked baseline and reference-detector scope:
  - [x] `configs/detectors/*.yaml`
  - [x] `src/dqbench/baselines/*.py`
  - [x] `pyproject.toml`
- [x] Audit orchestration and evaluation code against locked protocol:
  - [x] `src/dqbench/orchestration/run_experiment.py`
  - [x] `src/dqbench/evaluation/*.py`
  - [x] `src/dqbench/stats/*.py`
- [x] Audit tests against locked scope and release gate:
  - [x] `tests/contracts/*.py`
  - [x] `tests/orchestration/*.py`
  - [x] `tests/evaluation/*.py`
  - [x] `tests/injection/*.py`
- [x] Với mỗi mismatch giữa docs và repo:
  - [x] classify as `docs wrong`, `code/config wrong`, hoặc `both stale`
  - [x] fix within the same patch when benchmark semantics would otherwise drift
  - [x] fail loudly instead of keeping parallel truths

### Deliverables

- [x] repo-doc sync audit report
- [x] synchronized machine-readable constants
- [x] synchronized release-gate config

## Phase 1. Dataset Acquisition and Snapshot Freeze

### 1.1 Public acquisition workflows

- [ ] Cài acquisition workflow cho:
  - [x] `NYC TLC`
  - [x] `BTS On-Time`
  - [x] `Chicago Food`
  - [x] `NYC Parking Violations`
  - [x] `NYC HPD Housing Complaints and Violations`
  - [x] `Chicago Building Permits`
  - [x] `NYC 311`
  - [x] `Austin 311`
  - [x] `FAA OPSNET` supplementary extract
- [x] Mỗi workflow phải bám documented public URL hoặc portal workflow.
- [x] Mỗi workflow phải cho phép freeze snapshot reproducibly.

### 1.2 Raw snapshot manifests

- [ ] Với mỗi released dataset snapshot, materialize:
  - [ ] dataset identifier
  - [ ] snapshot identifier
  - [ ] snapshot date
  - [ ] source URL or portal page
  - [ ] schema version reference
  - [ ] checksum for every raw file
- [ ] Với support tables, materialize checksums riêng.

### 1.3 Support tables and domain gate

- [ ] Tải hoặc freeze mọi support table công khai cần thiết cho:
  - [ ] `NYC TLC`
  - [ ] `BTS On-Time`
- [ ] Verify domain inclusion gate cho từng dataset:
  - [ ] public acquisition reproducible
  - [ ] public schema reference hoặc data dictionary exists
  - [ ] ít nhất `80` scheduled batches
  - [ ] ít nhất `24` calibration batches và `40` evaluation batches
  - [ ] primary event timestamp và update cadence documented
  - [ ] support-table clean join coverage đạt `>= 95%` nếu có
  - [ ] released snapshot là contiguous official public window, không phải convenience subset
- [ ] Verify locked minimum paper-scale windows:
  - [ ] `NYC TLC`: contiguous `24-month` official window
  - [ ] `BTS On-Time`: contiguous `24-month` official `PREZIP` window
  - [ ] `Chicago Food`: contiguous `104-week` official window
  - [ ] `NYC Parking Violations`: contiguous `24-month` official event-time window
  - [ ] `NYC HPD Housing Complaints and Violations`: contiguous `24-month` official event-time window
  - [ ] `Chicago Building Permits`: contiguous `24-month` official event-time window
- [ ] Publish domain-scale disclosure cho từng core domain:
  - [ ] total canonical fact-row count
  - [ ] batch-row-count `p05`
  - [ ] batch-row-count `p50`
  - [ ] batch-row-count `p95`
  - [ ] batch-row-count `max`
  - [ ] number of monitored table-scoped targets
  - [ ] number of monitored column-scoped targets
- [ ] Dừng pipeline nếu domain không pass inclusion gate.

### Deliverables

- [ ] raw data snapshots
- [ ] raw snapshot manifests
- [ ] support-table manifests
- [ ] domain inclusion gate reports

## Phase 2. Canonicalization and Scope Catalogs

### 2.1 Canonical data model

- [ ] Canonicalize từng domain thành:
  - [ ] `1` fact table
  - [ ] declared support tables
- [ ] Khóa mapping từ raw columns sang canonical schema.
- [ ] Ghi rõ source references cho mọi field/range/FK semantics dùng trong benchmark.

### 2.2 Canonical batch schedule

- [ ] Xây canonical batch calendar/index từ first batch boundary đến last batch boundary trong snapshot range.
- [ ] Giữ scheduled zero-row batches trong batch index.
- [ ] Đảm bảo `freshness_lag` observable ở batch timeline.

### 2.3 Monitored scope catalog

- [ ] Xuất monitored scope catalog cho từng domain, bao gồm:
  - [ ] monitored completeness columns
  - [ ] monitored numeric validity columns
  - [ ] source of valid ranges
  - [ ] duplicate definition hoặc duplicate-key policy
  - [ ] monitored FK columns
  - [ ] declared public support tables
  - [ ] batch schedule and calendar construction policy
  - [ ] admissible target-scope sampling frame cho từng fault family
- [ ] Persist catalog như artifact công khai.

### Deliverables

- [ ] canonical fact table specification cho từng domain
- [ ] canonical batch index outputs
- [ ] monitored scope catalogs
- [ ] schema validation reports cho canonical artifacts

## Phase 3. Calibration and Evaluation Split

### 3.1 Split generation

- [ ] Sort batches chronologically.
- [ ] Materialize candidate calibration prefix là first `30%` batches, min `24` batches.
- [ ] Deterministically reserve earliest contiguous `20%` của phần post-calibration, min `12` batches, làm untouched clean holdout.
- [ ] Materialize dirty evaluation pool là phần post-calibration còn lại sau clean holdout.

### 3.2 Calibration cleanliness

- [ ] Implement deterministic calibration cleanliness screening.
- [ ] Screening phải record:
  - [ ] candidate calibration range
  - [ ] exact schema/support-table failures removed
  - [ ] excluded batches
  - [ ] deterministic exclusion rule
  - [ ] final count of screened-clean calibration batches
- [ ] Dừng domain nếu còn dưới `24` screened-clean calibration batches.

### 3.3 Frozen split artifacts

- [ ] Freeze calibration definitions theo snapshot.
- [ ] Freeze evaluation definitions theo snapshot.
- [ ] Xuất `calibration_cleanliness_report`.

### 3.4 Audited clean track

- [ ] Freeze one untouched clean evaluation copy cho mỗi core domain.
- [ ] Publish deterministic rule giữ clean track disjoint khỏi injected conditions.
- [ ] Define predeclared random audit sampling rule trên clean batches hoặc monitored scopes.
- [ ] Định nghĩa rõ `batch-scope` unit = `1` monitored scope tại `1` clean-track batch.
- [ ] Audit ít nhất `60` random `batch-scope` units cho mỗi core domain, stratified theo clean-track time range.
- [ ] Đảm bảo ít nhất `15` sampled units từ mỗi chronological quartile của clean track.
- [ ] Materialize clean-track audit protocol, gồm:
  - [ ] untouched clean evaluation range
  - [ ] audit sampling rule
  - [ ] official corroboration source hoặc manual-review procedure
  - [ ] uncertainty / exclusion policy
- [ ] Compute and publish one-sided exact `95%` `Clopper-Pearson` upper confidence bound on hidden-issue rate from the audit outcome.
- [ ] Materialize audited clean-track outputs cho `clean_run_fp_batch`, `clean_run_fp_alert`, và threshold-portability reading.

### Deliverables

- [ ] frozen calibration split definitions
- [ ] frozen evaluation split definitions
- [ ] calibration cleanliness reports
- [ ] audited clean-track protocol
- [ ] audited clean-track outputs

## Phase 4. Fault Injection and Ground Truth

### 4.1 Fault-family implementation

- [x] Implement `null_spike`.
- [x] Implement `range_violation`.
- [x] Implement `duplicate_burst`.
- [x] Implement `freshness_lag`.
- [x] Implement `fk_break`.

### 4.2 Injection contracts

- [ ] Với mỗi `domain x fault_family`, publish:
  - [ ] operator bank và operator identifiers
  - [ ] injection operator family
  - [ ] parameter ranges
  - [ ] seed semantics
  - [ ] operator-evidence map cho từng operator
  - [ ] predeclared maximum generation attempts per condition
  - [ ] edit-budget or batch-manipulation policy
  - [ ] plausibility guards on non-target features
  - [ ] target-scope selection policy
- [ ] Với các fault semantics có ít nhất `3` constructions hợp lý, mỗi `domain x fault_family` phải có ít nhất `3` operator identifiers; nếu chỉ có `1` hoặc `2`, phải mark `limited_construction` và có note giải thích.
- [ ] Operator exposure phải được phân bổ gần cân bằng theo rule deterministic trên fixed seed set, với chênh lệch count tối đa `1` trong mỗi `domain x fault_family x severity x duration`.
- [ ] Target-batch positions phải được phân bổ gần cân bằng theo evaluation-timeline quartiles; không được dồn incident về cuối timeline.
- [ ] Target batches phải được sample ngẫu nhiên từ evaluation pool, không từ calibration prefix.
- [ ] Với `freshness_lag`, state rõ implementation là delayed arrival, omitted batch materialization, hay cả hai.

### 4.3 Severity and condition validity

- [ ] Implement effect-size severity bands cho:
  - [ ] `null_spike`
  - [ ] `range_violation`
  - [ ] `duplicate_burst`
  - [ ] `fk_break`
- [ ] Implement lag-length severity bands cho `freshness_lag`.
- [ ] Verify realized dirty target feature nằm đúng severity band trước khi condition được chấp nhận.
- [ ] Freeze injector parameter ranges, acceptance rules, và maximum generation attempts trước khi detector execution bắt đầu.
- [ ] Cấm sửa injector definition sau khi đã thấy dirty-run, clean-track, hoặc external-validation outcomes trên cùng snapshot release.

### 4.4 Incident contract

- [ ] Đảm bảo mỗi dirty run chỉ có:
  - [x] đúng `1` incident
  - [x] đúng `1` fault family
- [ ] Materialize incident records với:
  - [x] fault family
  - [x] domain
  - [x] severity
  - [x] duration
  - [x] target scope
  - [x] incident start batch
  - [x] incident end batch
  - [x] detection window start batch
  - [x] detection window end batch
- [ ] Materialize injection manifests với realized pre/post values.
- [ ] Materialize selected operator id, target batches, realized non-target side effects, acceptance/rejection reason, và generation-attempt count.

### 4.5 Injection robustness

- [ ] Nếu một fault family có nhiều operators, materialize per-operator coverage summary.
- [ ] Materialize evaluation-timeline quartile coverage by operator.
- [ ] Materialize rejected-candidate counts, rejection reasons, và acceptance rates by operator.
- [ ] Publish supplementary leave-one-operator-out robustness summary khi operator bank có nhiều operators.
- [ ] Publish triviality audit để phát hiện operators quá dễ hoặc quá lộ.

### Deliverables

- [x] injection operators
- [ ] injection manifests
- [x] incident records
- [ ] severity validation reports
- [ ] operator-bank manifest
- [ ] injection robustness appendix
- [ ] operator-evidence map

## Phase 5. Batch Profiling

### 5.1 Profile generation

- [ ] Tính canonical batch profiles với đúng feature contract:
  - [x] `row_count`
  - [x] `null_ratio__<column>`
  - [x] `duplicate_ratio`
  - [x] `min__<column>`
  - [x] `max__<column>`
  - [x] `range_violation_ratio__<column>`
  - [x] `invalid_fk_ratio__<column>`

### 5.2 Validation and freeze

- [ ] Validate calibration profiles bằng `Pandera`.
- [ ] Validate evaluation profiles bằng `Pandera`.
- [x] Freeze profile-generation logic để mọi baseline consume cùng interface.

### Deliverables

- [ ] calibration profile tables
- [ ] evaluation profile tables
- [ ] profile schema-validation reports

## Phase 6. Built-in Baselines

### 6.1 Implement locked baselines

- [x] Implement `Calibration Threshold Lower Bound`.
- [x] Implement `Constraint-Rule Baseline`.
- [x] Implement `History-Based Robust Profile Baseline`.
- [x] Implement `EWMA-CUSUM Sequential Baseline`.
- [x] Implement `Isolation Forest Baseline`.

### 6.2 Baseline-specific constraints

- [x] `Constraint-Rule Baseline` phải dùng fixed rule catalog trên benchmark feature families.
- [x] `History-Based` phải dùng fixed history window `8`.
- [ ] `EWMA-CUSUM` phải dùng:
  - [x] `lambda = 0.3`
  - [x] `k = 0.5`
  - [x] zero initialization at run start
  - [x] table-scoped handling theo spec
- [x] `Isolation Forest` phải dùng đúng fixed hyperparameters.

### 6.3 Fairness policy

- [x] Tất cả baselines dùng cùng canonical batch profiles.
- [x] Thresholds chỉ calibrated từ clean calibration scores.
- [x] Hyperparameters fixed theo detector family trong một domain.
- [ ] Freeze detector configuration manifests, preprocessing rules, adapter settings, và reference-detector integration parameters trước khi dirty-run, clean-track, hoặc external-validation outcomes được quan sát.
- [ ] Cấm retune detector configs dựa trên dirty-run, clean-track, hoặc external-validation outcomes trên cùng released snapshot.
- [x] State-bearing baselines chỉ được initialize từ clean calibration prefix.
- [x] Mỗi baseline emit tối đa `1 alert / batch`.

### 6.4 Public-code reference detectors

- [x] Add `ECOD` adapter on the same canonical batch-profile interface.
- [x] Add `COPOD` adapter on the same canonical batch-profile interface.
- [x] Add `Extended Isolation Forest` adapter on the same canonical batch-profile interface.
- [ ] Add `kNN` adapter on the same canonical batch-profile interface.
- [ ] Add `LOF` adapter on the same canonical batch-profile interface.
- [ ] Add `One-Class SVM` adapter on the same canonical batch-profile interface.
- [x] Keep public-code reference detectors outside the `5` locked baseline counts and the primary leaderboard.
- [ ] Ensure the shipped public-code reference appendix is still treated as required for every paper-scale empirical release.
- [ ] Publish source-repo links, paper links, and integration notes for each public-code reference detector.
- [ ] Run and report the shipped public-code reference appendix for every paper-scale empirical release: `ECOD`, `COPOD`, `Extended Isolation Forest`, `kNN`, `LOF`, `One-Class SVM`.

### Deliverables

- [x] `5` baseline implementations
- [ ] public-code reference detector adapters
- [ ] detector config manifests
- [ ] detector-level smoke tests
- [ ] public-code reference-detector appendix

## Phase 7. Alert Generation, Matching, and Metrics

### 7.1 Alert contract

- [ ] Chuẩn hóa canonical alert schema với đầy đủ fields:
  - [x] detector identifier
  - [x] domain identifier
  - [x] batch identifier
  - [x] scope level
  - [x] scope reference
  - [x] scalar score
  - [x] calibration policy identifier
- [ ] Implement deterministic reduction cho detector native phát nhiều alert trong một batch.
- [ ] Với detector native phát nhiều alert trong một batch, materialize supplementary native-output appendix trên unreduced outputs dưới cùng matching semantics.

### 7.2 Matching engine

- [ ] Implement scope compatibility:
  - [x] exact column match -> `1.0`
  - [x] parent table match for column incident -> `0.5`
  - [x] exact table match -> `1.0`
  - [x] column match for table incident -> `0.0`
- [x] Implement `greedy earliest-valid-unmatched` matching.
- [x] Track duplicate alerts sau first matched alert.

### 7.3 Metrics engine

- [ ] Implement `8` primary metrics:
  - [x] `incident_recall`
  - [x] `incident_precision`
  - [x] `incident_f1`
  - [x] `detection_delay_norm_mean`
  - [x] `localization_accuracy_hierarchical`
  - [x] `duplicate_burden`
  - [x] `clean_run_fp_batch`
  - [x] `runtime_per_1m_rows`
- [ ] Implement supplementary metrics:
  - [x] `detection_delay_raw_mean`
  - [x] `localization_accuracy_strict`
  - [x] `clean_run_fp_alert`
  - [x] `runtime_overhead_seconds`
  - [ ] `weak_label_hit_rate`
  - [ ] `weak_label_lead_lag_median`
- [ ] Implement metric edge cases:
  - [x] zero-alert precision
  - [x] zero denominator `f1`
  - [x] unmatched incident delay penalty
  - [x] unmatched incident localization credit
  - [ ] fixed runtime boundary metadata

### Deliverables

- [x] alerts
- [x] matches
- [x] metrics
- [x] schema validation outputs

## Phase 8. External Validation and Supplementary Appendix

### 8.1 NYC 311 external validation

- [ ] Freeze one `12-month` `NYC 311` snapshot.
- [ ] Dùng full official `NYC 311` extract cho frozen window, không prefilter complaint type / borough / agency trước case-study construction.
- [ ] Implement `location-quality` case study.
- [ ] Implement `service-process timeliness` case study.
- [ ] Implement descriptive hit-rate / lead-lag summary khi weak labels hoặc issue windows khả dụng.
- [ ] Keep results tách khỏi primary leaderboard và inferential ranking tables.

### 8.2 Austin 311 external validation

- [ ] Freeze one `12-month` `Austin 311` snapshot.
- [ ] Dùng full official `Austin 311` extract hoặc full official Open311 query surface cho frozen window, không prefilter service-request category / district / department trước case-study construction.
- [ ] Implement `service-process timeliness` case study.
- [ ] Implement `request-status consistency` case study.
- [ ] Implement descriptive hit-rate / lead-lag summary khi weak labels hoặc issue windows khả dụng.
- [ ] Keep results tách khỏi primary leaderboard và inferential ranking tables.

### 8.3 BTS audit-backed supplementary appendix

- [ ] Freeze one `12-month` `BTS On-Time` snapshot từ primary benchmark.
- [ ] Freeze one `FAA OPSNET` finalized monthly reference extract.
- [ ] Materialize discrepancy-window manifest motivated by `DOT OIG` audit.
- [ ] Implement:
  - [ ] `airport-month disruption consistency` report
  - [ ] `reported-cause discrepancy` report
  - [ ] weak-label `hit-rate` và `lead-lag` summary
- [ ] Keep appendix tách khỏi primary leaderboard và inferential ranking tables.

### Deliverables

- [ ] `NYC 311` external validation outputs
- [ ] `Austin 311` external validation outputs
- [ ] `BTS` appendix outputs
- [ ] discrepancy-window manifest
- [ ] external-validation descriptive summary tables

## Phase 9. Experiment Orchestration

### 9.1 Condition generation

- [ ] Build experiment runner sinh toàn bộ condition matrix cho `6` core domains.
- [ ] Materialize run configs cho từng condition.
- [ ] Materialize clean evaluation run cho từng core domain.

### 9.2 Benchmark execution

- [ ] Run full dirty matrix cho shared-core families.
- [ ] Run `fk_break` extension trên qualifying domains.
- [ ] Run clean-run false-positive evaluation.
- [ ] Run threshold sensitivity appendix cho `p90`, `p95`, `p99` hoặc equivalent fixed clean-FP sweep.

### 9.3 Aggregation

- [ ] Aggregate per-domain summary tables.
- [ ] Aggregate shared-core cross-domain leaderboard.
- [ ] Aggregate `fk_break` extension tables.
- [ ] Aggregate `NYC 311` outputs.
- [ ] Aggregate `Austin 311` outputs.
- [ ] Aggregate `BTS` appendix outputs.

### Deliverables

- [ ] executable condition configs
- [ ] run outputs cho toàn bộ matrix
- [ ] aggregate benchmark tables

## Phase 10. Statistical Analysis

### 10.1 Cell-level aggregation

- [ ] Aggregate metrics across seeds bằng median theo benchmark cell:
  - [ ] `domain`
  - [ ] `fault_family`
  - [ ] `severity`
  - [ ] `duration`
- [ ] Xuất within-cell seed dispersion summaries.

### 10.2 Inferential statistics

- [ ] Run `Friedman` omnibus test cho mỗi primary metric trên shared-core leaderboard.
- [ ] Run pairwise `Wilcoxon signed-rank` tests.
- [ ] Apply `Holm` correction.
- [ ] Report `median paired difference`.
- [ ] Report `matched rank-biserial correlation`.
- [ ] Report `fk_break` extension statistics riêng.
- [ ] Không merge external validation tracks vào inferential ranking table.

### 10.3 Transfer analysis

- [ ] Compute fixed `injected incident rank` from:
  - [ ] `incident_f1`
  - [ ] `detection_delay_norm_mean`
  - [ ] `localization_accuracy_hierarchical`
- [ ] Compute leave-one-domain-out transfer with:
  - [ ] `Spearman`
  - [ ] `Kendall`
- [ ] Compute injected-to-clean transfer with:
  - [ ] `Spearman`
  - [ ] `Kendall`
- [ ] Compute injected-to-`BTS` weak-label transfer with:
  - [ ] `Spearman`
  - [ ] `Kendall`
- [ ] Keep `NYC 311` descriptive unless a fixed scalar validation target is explicitly locked in the spec.
- [ ] Publish threshold-portability summary trên:
  - [ ] audited clean track
  - [ ] `NYC 311` external validation
  - [ ] `Austin 311` external validation
  - [ ] `BTS` supplementary appendix
- [ ] Keep transfer analysis supplementary, không override primary leaderboard.

### Deliverables

- [ ] statistical result tables
- [ ] seed dispersion tables
- [ ] inferential summary tables
- [ ] transfer-analysis tables

## Phase 11. Artifact Packaging and Release

### 11.1 Required machine-readable outputs

- [ ] Với mỗi run, materialize:
  - [x] `alerts`
  - [x] `incidents`
  - [x] `matches`
  - [x] `metrics`
  - [x] `schema_validation`
- [ ] Với mỗi detector submission, materialize:
  - [ ] detector configuration manifest
  - [ ] software version manifest
  - [ ] runtime environment manifest
  - [ ] detector-native alert appendix outputs nếu detector native có multi-alert behavior

### 11.2 Public release contents

- [ ] Publish:
  - [ ] benchmark source code
  - [ ] executable condition configs
  - [ ] seed lists
  - [ ] data acquisition scripts
  - [ ] monitored scope catalogs
  - [ ] injection manifests and realized-severity manifests
  - [ ] operator-evidence maps
  - [ ] calibration cleanliness reports
  - [ ] audited clean-track protocol and audit outputs
  - [ ] strict `Pydantic` models
  - [ ] `Pandera` schemas
  - [ ] manifests and checksums
  - [ ] frozen split definitions
  - [ ] containerized runtime environment with pinned dependencies
  - [ ] one-command pilot entry point
  - [ ] one-command full-suite entry point
  - [ ] runtime measurement policy and hardware manifest
  - [ ] detector adapter template
  - [ ] output-schema validator
  - [ ] machine-readable schema-validation reports
  - [ ] canonical output schemas
  - [ ] aggregate tables used in the paper
  - [ ] transfer-analysis tables and summaries
  - [ ] domain-scale disclosure tables
  - [ ] detector-native multi-alert appendix outputs when applicable

### 11.3 Raw data policy

- [ ] Nếu source cho phép redistribution, package raw files đúng policy.
- [ ] Nếu source không cho redistribution, publish:
  - [ ] acquisition procedure
  - [ ] exact source references
  - [ ] checksums
  - [ ] expected local directory structure

### Deliverables

- [ ] reproducible artifact bundle
- [ ] containerized runtime
- [ ] third-party detector adapter template
- [ ] validator tooling

## Phase 12. Paper-Scale Release Verification

### 12.1 Release gate verification

- [ ] Verify locked design executed without scope drift.
- [ ] Verify all `6` core domains executed under locked protocol.
- [ ] Verify all released datasets satisfy domain inclusion gate.
- [ ] Verify shared-core leaderboard reported on matched conditions.
- [ ] Verify `fk_break` extension reported on every qualifying domain.
- [ ] Verify all `5` locked baselines executed.
- [ ] Verify all `6` public-code reference detectors executed under the appendix contract.
- [ ] Verify all `8` primary metrics reported cho mọi benchmark condition.
- [ ] Verify clean-run false-positive evaluation included.
- [ ] Verify monitored scope catalogs, injection manifests, calibration cleanliness reports published.
- [ ] Verify operator-evidence maps và operator-level robustness appendix outputs published.
- [ ] Verify audited clean-track protocol and outputs published.
- [ ] Verify runtime boundary and hardware policy published.
- [ ] Verify threshold-sensitivity appendix published.
- [ ] Verify detector configuration manifests frozen and not revised after observing dirty-run, clean-track, or external-validation outcomes.
- [ ] Verify inferential statistics reported trên shared-core leaderboard.
- [ ] Verify `NYC 311` external validation published.
- [ ] Verify `Austin 311` external validation published.
- [ ] Verify `BTS` audit-backed supplementary validation appendix published.
- [ ] Verify transfer-analysis outputs published.
- [ ] Verify the shipped public-code reference-detector appendix is published for every paper-scale empirical release.
- [ ] Verify any detector with native multi-alert behavior publishes the supplementary native-output appendix.
- [ ] Verify repo-doc sync audit is complete and no machine-readable contract still disagrees with `docs/documentation.md`.
- [ ] Verify all configs và benchmark outputs pass strict schema validation.
- [ ] Verify artifact đủ cho third-party reproduction end-to-end.

### Deliverables

- [ ] paper-scale release verification report
- [ ] final release checklist signed off

## Test Plan / Acceptance Criteria

### Contract tests

- [ ] Mọi `Pydantic` model reject invalid manifests/configs.
- [ ] Mọi `Pandera` schema reject malformed tabular artifacts.
- [ ] Output-schema validator reject malformed detector submissions.

### Domain tests

- [ ] Mỗi domain pass canonicalization tests.
- [ ] Mỗi domain pass batch index tests.
- [ ] Mỗi domain pass monitored scope catalog validation.
- [ ] Mỗi domain pass inclusion gate checks hoặc fail deterministically với lý do rõ ràng.

### Injection tests

- [ ] Mỗi fault family đạt đúng severity band.
- [ ] Mỗi fault family đạt đúng duration.
- [ ] Mỗi dirty run giữ đúng one-incident contract.
- [ ] Plausibility guards được kiểm và report.
- [ ] Target batch selection only draws from evaluation pool.
- [ ] Operator-bank metadata và realized side-effect manifests hợp lệ.
- [ ] Operator exposure is balanced under the deterministic allocation rule.

### Baseline tests

- [ ] Cả `5` baselines consume cùng canonical profile interface.
- [ ] Cả `5` baselines emit đúng alert schema.
- [ ] Cả `5` baselines obey `one alert per batch`.
- [ ] `EWMA-CUSUM` obey đúng fixed parameters và initialization rule.
- [ ] `Isolation Forest` obey đúng fixed hyperparameters.

### Evaluation tests

- [ ] Matching logic đúng scope compatibility table.
- [x] Duplicate burden logic đúng.
- [ ] Delay penalty logic đúng.
- [ ] Zero-alert precision và zero-denominator `f1` đúng.
- [ ] Weak-label metrics đúng định nghĩa.
- [ ] Rank-transfer summaries đúng định nghĩa `Spearman/Kendall`.
- [ ] Threshold-portability summaries đúng định nghĩa.
- [ ] `Injected incident rank` uses the fixed predeclared metric tuple only.

### Orchestration tests

- [ ] Run matrix size đúng spec.
- [ ] Seed aggregation đúng spec.
- [ ] Threshold sensitivity appendix chạy đúng operating points.
- [ ] Aggregate outputs khớp spec.

### Release tests

- [ ] Full paper-scale gate pass mà không cần diễn giải thủ công.
- [ ] Reproduction dry-run từ artifact pass với validator/tooling được ship kèm.
- [ ] Audited clean-track outputs và transfer-analysis outputs được publish đầy đủ.

## Defaults and Locked Assumptions

- [x] Chỉ bám `docs/documentation.md`.
- [x] Khóa đúng `6` core domains + `2` external validation tracks + `1` `BTS` supplementary appendix, không mở thêm scope ngoài spec.
- [x] Không thêm deep model.
- [x] Không mở rộng detector API ra ngoài canonical batch-profile interface + declared public support tables.
- [x] `BTS` appendix là supplementary weak-label validation, không phải exact-label leaderboard.
- [x] `EWMA-CUSUM` là baseline temporal bắt buộc trong locked set.
- [x] `Pydantic + Pandera` là bắt buộc trong implementation contract, không để tới cuối mới thêm.
