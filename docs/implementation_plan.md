# Implementation Plan

Checklist này là bản triển khai chi tiết cho coder follow khi xây `dq-alert-benchmark`.

Nguồn chân lý duy nhất cho checklist này là:

- `/home/dtl/Documents/thes/docs/documentation.md`

Checklist này:

- không dựa vào hiện trạng code hiện tại
- không mở rộng scope ngoài spec
- không thay spec bằng prompt implement
- được sắp theo thứ tự phụ thuộc để tránh miss việc

## Cách dùng

- Chỉ bắt đầu phase tiếp theo khi deliverables của phase hiện tại đã được khóa.
- Không đánh dấu xong nếu chưa có artifact machine-readable hoặc test tương ứng khi checklist yêu cầu.
- Nếu phát hiện vướng mắc làm thay đổi scope, cập nhật `documentation.md` trước hoặc đồng thời với implementation.

## Phase 0. Freeze Benchmark Contract

### 0.1 Benchmark constants

- [ ] Khóa toàn bộ benchmark constants thành machine-readable config hoặc constants module:
  - [ ] `3` core domains
  - [ ] `1` external validation domain
  - [ ] `1` BTS audit-backed supplementary appendix
  - [ ] `5` fault families
  - [ ] `5` locked baselines
  - [ ] `8` primary metrics
  - [ ] `5` seeds per condition
  - [ ] `2` durations
  - [ ] `3` severities
- [ ] Khóa toàn bộ benchmark identifiers:
  - [ ] `domain`
  - [ ] `fault_family`
  - [ ] `severity`
  - [ ] `duration`
  - [ ] `scope_level`
  - [ ] `batch_unit`
  - [ ] `calibration_policy`

### 0.2 Run matrix and release gate

- [ ] Khóa run matrix:
  - [ ] `NYC TLC`: `150` dirty runs + `1` clean run
  - [ ] `BTS On-Time`: `150` dirty runs + `1` clean run
  - [ ] `Chicago Food`: `120` dirty runs + `1` clean run
  - [ ] `423` total benchmark runs
  - [ ] `2115` detector executions for the `5` locked baselines
- [ ] Chuyển paper-scale release gate thành checklist machine-checkable.
- [ ] Chuyển artifact requirements thành checklist machine-checkable.

### 0.3 Contracts and schemas

- [ ] Định nghĩa strict `Pydantic` models cho:
  - [ ] snapshot manifest
  - [ ] monitored scope catalog
  - [ ] calibration cleanliness report
  - [ ] injection manifest
  - [ ] detector configuration manifest
  - [ ] runtime manifest
  - [ ] schema validation report
- [ ] Định nghĩa `Pandera` schemas cho:
  - [ ] canonical dataframe
  - [ ] support tables
  - [ ] canonical batch index
  - [ ] calibration profiles
  - [ ] evaluation profiles
  - [ ] alerts
  - [ ] incidents
  - [ ] matches
  - [ ] metrics
- [ ] Khóa canonical output schemas cho:
  - [ ] `alerts`
  - [ ] `incidents`
  - [ ] `matches`
  - [ ] `metrics`
  - [ ] `schema_validation`
- [ ] Khóa third-party detector contract:
  - [ ] input chỉ gồm canonical batch profiles + declared public support tables
  - [ ] không truy cập hidden labels hoặc benchmark-private metadata
  - [ ] output phải đúng canonical alert schema
  - [ ] detector phải xuất config manifest + software version

### Deliverables

- [ ] benchmark constants manifest
- [ ] enum/identifier definitions
- [ ] strict `Pydantic` models
- [ ] `Pandera` schemas
- [ ] release-gate checklist machine-readable

## Phase 1. Dataset Acquisition and Snapshot Freeze

### 1.1 Public acquisition workflows

- [ ] Cài acquisition workflow cho:
  - [ ] `NYC TLC`
  - [ ] `BTS On-Time`
  - [ ] `Chicago Food`
  - [ ] `NYC 311`
  - [ ] `FAA OPSNET` supplementary extract
- [ ] Mỗi workflow phải bám documented public URL hoặc portal workflow.
- [ ] Mỗi workflow phải cho phép freeze snapshot reproducibly.

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
- [ ] Materialize evaluation pool là phần còn lại.

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

### Deliverables

- [ ] frozen calibration split definitions
- [ ] frozen evaluation split definitions
- [ ] calibration cleanliness reports

## Phase 4. Fault Injection and Ground Truth

### 4.1 Fault-family implementation

- [ ] Implement `null_spike`.
- [ ] Implement `range_violation`.
- [ ] Implement `duplicate_burst`.
- [ ] Implement `freshness_lag`.
- [ ] Implement `fk_break`.

### 4.2 Injection contracts

- [ ] Với mỗi `domain x fault_family`, publish:
  - [ ] injection operator family
  - [ ] parameter ranges
  - [ ] seed semantics
  - [ ] edit-budget or batch-manipulation policy
  - [ ] plausibility guards on non-target features
  - [ ] target-scope selection policy
- [ ] Với `freshness_lag`, state rõ implementation là delayed arrival, omitted batch materialization, hay cả hai.

### 4.3 Severity and condition validity

- [ ] Implement effect-size severity bands cho:
  - [ ] `null_spike`
  - [ ] `range_violation`
  - [ ] `duplicate_burst`
  - [ ] `fk_break`
- [ ] Implement lag-length severity bands cho `freshness_lag`.
- [ ] Verify realized dirty target feature nằm đúng severity band trước khi condition được chấp nhận.

### 4.4 Incident contract

- [ ] Đảm bảo mỗi dirty run chỉ có:
  - [ ] đúng `1` incident
  - [ ] đúng `1` fault family
- [ ] Materialize incident records với:
  - [ ] fault family
  - [ ] domain
  - [ ] severity
  - [ ] duration
  - [ ] target scope
  - [ ] incident start batch
  - [ ] incident end batch
  - [ ] detection window start batch
  - [ ] detection window end batch
- [ ] Materialize injection manifests với realized pre/post values.

### Deliverables

- [ ] injection operators
- [ ] injection manifests
- [ ] incident records
- [ ] severity validation reports

## Phase 5. Batch Profiling

### 5.1 Profile generation

- [ ] Tính canonical batch profiles với đúng feature contract:
  - [ ] `row_count`
  - [ ] `null_ratio__<column>`
  - [ ] `duplicate_ratio`
  - [ ] `min__<column>`
  - [ ] `max__<column>`
  - [ ] `range_violation_ratio__<column>`
  - [ ] `invalid_fk_ratio__<column>`

### 5.2 Validation and freeze

- [ ] Validate calibration profiles bằng `Pandera`.
- [ ] Validate evaluation profiles bằng `Pandera`.
- [ ] Freeze profile-generation logic để mọi baseline consume cùng interface.

### Deliverables

- [ ] calibration profile tables
- [ ] evaluation profile tables
- [ ] profile schema-validation reports

## Phase 6. Built-in Baselines

### 6.1 Implement locked baselines

- [ ] Implement `Calibration Threshold Lower Bound`.
- [ ] Implement `Constraint-Rule Baseline`.
- [ ] Implement `History-Based Robust Profile Baseline`.
- [ ] Implement `EWMA-CUSUM Sequential Baseline`.
- [ ] Implement `Isolation Forest Baseline`.

### 6.2 Baseline-specific constraints

- [ ] `Constraint-Rule Baseline` phải dùng fixed rule catalog trên benchmark feature families.
- [ ] `History-Based` phải dùng fixed history window `8`.
- [ ] `EWMA-CUSUM` phải dùng:
  - [ ] `lambda = 0.3`
  - [ ] `k = 0.5`
  - [ ] zero initialization at run start
  - [ ] table-scoped handling theo spec
- [ ] `Isolation Forest` phải dùng đúng fixed hyperparameters.

### 6.3 Fairness policy

- [ ] Tất cả baselines dùng cùng canonical batch profiles.
- [ ] Thresholds chỉ calibrated từ clean calibration scores.
- [ ] Hyperparameters fixed theo detector family trong một domain.
- [ ] State-bearing baselines chỉ được initialize từ clean calibration prefix.
- [ ] Mỗi baseline emit tối đa `1 alert / batch`.

### Deliverables

- [ ] `5` baseline implementations
- [ ] detector config manifests
- [ ] detector-level smoke tests

## Phase 7. Alert Generation, Matching, and Metrics

### 7.1 Alert contract

- [ ] Chuẩn hóa canonical alert schema với đầy đủ fields:
  - [ ] detector identifier
  - [ ] domain identifier
  - [ ] batch identifier
  - [ ] scope level
  - [ ] scope reference
  - [ ] scalar score
  - [ ] calibration policy identifier
- [ ] Implement deterministic reduction cho detector native phát nhiều alert trong một batch.

### 7.2 Matching engine

- [ ] Implement scope compatibility:
  - [ ] exact column match -> `1.0`
  - [ ] parent table match for column incident -> `0.5`
  - [ ] exact table match -> `1.0`
  - [ ] column match for table incident -> `0.0`
- [ ] Implement `greedy earliest-valid-unmatched` matching.
- [ ] Track duplicate alerts sau first matched alert.

### 7.3 Metrics engine

- [ ] Implement `8` primary metrics:
  - [ ] `incident_recall`
  - [ ] `incident_precision`
  - [ ] `incident_f1`
  - [ ] `detection_delay_norm_mean`
  - [ ] `localization_accuracy_hierarchical`
  - [ ] `duplicate_burden`
  - [ ] `clean_run_fp_batch`
  - [ ] `runtime_per_1m_rows`
- [ ] Implement supplementary metrics:
  - [ ] `detection_delay_raw_mean`
  - [ ] `localization_accuracy_strict`
  - [ ] `clean_run_fp_alert`
  - [ ] `runtime_overhead_seconds`
  - [ ] `weak_label_hit_rate`
  - [ ] `weak_label_lead_lag_median`
- [ ] Implement metric edge cases:
  - [ ] zero-alert precision
  - [ ] zero denominator `f1`
  - [ ] unmatched incident delay penalty
  - [ ] unmatched incident localization credit
  - [ ] fixed runtime boundary metadata

### Deliverables

- [ ] alerts
- [ ] matches
- [ ] metrics
- [ ] schema validation outputs

## Phase 8. External Validation and Supplementary Appendix

### 8.1 NYC 311 external validation

- [ ] Freeze one `12-month` `NYC 311` snapshot.
- [ ] Implement `location-quality` case study.
- [ ] Implement `service-process timeliness` case study.
- [ ] Keep results tách khỏi primary leaderboard và inferential ranking tables.

### 8.2 BTS audit-backed supplementary appendix

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
- [ ] `BTS` appendix outputs
- [ ] discrepancy-window manifest

## Phase 9. Experiment Orchestration

### 9.1 Condition generation

- [ ] Build experiment runner sinh toàn bộ condition matrix cho `3` core domains.
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

### Deliverables

- [ ] statistical result tables
- [ ] seed dispersion tables
- [ ] inferential summary tables

## Phase 11. Artifact Packaging and Release

### 11.1 Required machine-readable outputs

- [ ] Với mỗi run, materialize:
  - [ ] `alerts`
  - [ ] `incidents`
  - [ ] `matches`
  - [ ] `metrics`
  - [ ] `schema_validation`
- [ ] Với mỗi detector submission, materialize:
  - [ ] detector configuration manifest
  - [ ] software version manifest
  - [ ] runtime environment manifest

### 11.2 Public release contents

- [ ] Publish:
  - [ ] benchmark source code
  - [ ] executable condition configs
  - [ ] seed lists
  - [ ] data acquisition scripts
  - [ ] monitored scope catalogs
  - [ ] injection manifests and realized-severity manifests
  - [ ] calibration cleanliness reports
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
- [ ] Verify all `3` core domains executed under locked protocol.
- [ ] Verify all released datasets satisfy domain inclusion gate.
- [ ] Verify shared-core leaderboard reported on matched conditions.
- [ ] Verify `fk_break` extension reported on every qualifying domain.
- [ ] Verify all `5` locked baselines executed.
- [ ] Verify all `8` primary metrics reported cho mọi benchmark condition.
- [ ] Verify clean-run false-positive evaluation included.
- [ ] Verify monitored scope catalogs, injection manifests, calibration cleanliness reports published.
- [ ] Verify runtime boundary and hardware policy published.
- [ ] Verify threshold-sensitivity appendix published.
- [ ] Verify inferential statistics reported trên shared-core leaderboard.
- [ ] Verify `NYC 311` external validation published.
- [ ] Verify `BTS` audit-backed supplementary validation appendix published.
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

### Baseline tests

- [ ] Cả `5` baselines consume cùng canonical profile interface.
- [ ] Cả `5` baselines emit đúng alert schema.
- [ ] Cả `5` baselines obey `one alert per batch`.
- [ ] `EWMA-CUSUM` obey đúng fixed parameters và initialization rule.
- [ ] `Isolation Forest` obey đúng fixed hyperparameters.

### Evaluation tests

- [ ] Matching logic đúng scope compatibility table.
- [ ] Duplicate burden logic đúng.
- [ ] Delay penalty logic đúng.
- [ ] Zero-alert precision và zero-denominator `f1` đúng.
- [ ] Weak-label metrics đúng định nghĩa.

### Orchestration tests

- [ ] Run matrix size đúng spec.
- [ ] Seed aggregation đúng spec.
- [ ] Threshold sensitivity appendix chạy đúng operating points.
- [ ] Aggregate outputs khớp spec.

### Release tests

- [ ] Full paper-scale gate pass mà không cần diễn giải thủ công.
- [ ] Reproduction dry-run từ artifact pass với validator/tooling được ship kèm.

## Defaults and Locked Assumptions

- [ ] Chỉ bám `/home/dtl/Documents/thes/docs/documentation.md`.
- [ ] Không thêm domain mới.
- [ ] Không thêm deep model.
- [ ] Không mở rộng detector API ra ngoài canonical batch-profile interface + declared public support tables.
- [ ] `BTS` appendix là supplementary weak-label validation, không phải exact-label leaderboard.
- [ ] `EWMA-CUSUM` là baseline temporal bắt buộc trong locked set.
- [ ] `Pydantic + Pandera` là bắt buộc trong implementation contract, không để tới cuối mới thêm.
