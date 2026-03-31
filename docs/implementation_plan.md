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
  - [x] `3` core domains
  - [x] `1` external validation domain
  - [x] `1` BTS audit-backed supplementary appendix
  - [x] `5` fault families
  - [x] `5` locked baselines
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
  - [x] `423` total benchmark runs
  - [x] `2115` detector executions cho `5` locked baselines
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

- [x] Implement `null_spike`.
- [x] Implement `range_violation`.
- [x] Implement `duplicate_burst`.
- [x] Implement `freshness_lag`.
- [x] Implement `fk_break`.

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

### Deliverables

- [x] injection operators
- [ ] injection manifests
- [x] incident records
- [ ] severity validation reports

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
- [x] State-bearing baselines chỉ được initialize từ clean calibration prefix.
- [x] Mỗi baseline emit tối đa `1 alert / batch`.

### Deliverables

- [x] `5` baseline implementations
- [x] detector config manifests
- [ ] detector-level smoke tests

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
  - [x] `alerts`
  - [x] `incidents`
  - [x] `matches`
  - [x] `metrics`
  - [x] `schema_validation`
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
- [x] Duplicate burden logic đúng.
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

- [x] Chỉ bám `docs/documentation.md`.
- [x] Không thêm domain mới.
- [x] Không thêm deep model.
- [x] Không mở rộng detector API ra ngoài canonical batch-profile interface + declared public support tables.
- [x] `BTS` appendix là supplementary weak-label validation, không phải exact-label leaderboard.
- [x] `EWMA-CUSUM` là baseline temporal bắt buộc trong locked set.
- [x] `Pydantic + Pandera` là bắt buộc trong implementation contract, không để tới cuối mới thêm.
