# Supplementary External Reference Detectors

These detectors define the official public-code reference appendix in the benchmark specification. They are supplementary to the `5` locked baselines and do not change the primary leaderboard contract.

All six appendix detectors:

- consume the same canonical batch-profile vectors as the locked baselines
- emit the same canonical alert schema
- use the same clean-calibration thresholding policy in the benchmark
- are treated as table-scored anomaly detectors under the appendix contract unless a detector-specific scope-compatibility note says otherwise

Their benchmark interpretation follows the same claim boundary as the built-in baselines. A reference detector is not treated as high quality in this project on provenance alone; it is interpreted through four evidence layers:

- contract-valid execution on the canonical batch-profile interface
- performance on the transparent injected benchmark matrix
- false-positive behavior on the audited clean track
- descriptive transfer behavior on the `NYC 311`, `Austin 311`, and `BTS` supplementary validation tracks

These layers do not turn the reference detectors into official replacements for the locked five baselines. They only provide stronger, more reproducible external comparison under the same benchmark contract.

For this repository's benchmark policy, they also serve a second role: every paper-scale empirical release must report this shipped public-code appendix, rather than relying only on internally designed representative baselines.

Appendix-level reference detectors are expected to run pinned upstream implementations through thin benchmark adapters, not local reimplementations of their core scoring logic.

## ECOD

- Detector id: `ecod`
- Code: official `PyOD` implementation
- Source repo: https://github.com/yzhao062/pyod
- Paper: Zheng Li, Yue Zhao, Xiyang Hu, Nicola Botta, Cezar Ionescu, George H. Chen, `ECOD: Unsupervised Outlier Detection Using Empirical Cumulative Distribution Functions`
- Paper links:
  - arXiv: https://arxiv.org/abs/2201.00382
  - IEEE: https://ieeexplore.ieee.org/document/9737003
- Benchmark evidence:
  - `ADBench` compares `30` algorithms on `57` datasets: https://papers.nips.cc/paper_files/paper/2022/file/cf93972b116ca5268827d575f2cc226b-Paper-Datasets_and_Benchmarks.pdf
  - `PyOD` README explicitly points to `ADBench` as its performance-comparison benchmark resource: https://github.com/yzhao062/pyod
  - In Bouman, Bukhsh, and Heskes, JMLR 2024, `ECOD` appears in the top overall ranking table with mean `AUC = 0.815`; this is lower than `EIF` (`0.849`) and `COPOD` (`0.831`) in that same table: https://www.jmlr.org/papers/volume25/23-0570/23-0570.pdf
- Why it fits this project:
  - pure Python adapter path
  - native vector input and scalar anomaly scores
  - parameter-light and easy to explain
- Risks:
  - strong generic tabular anomaly detector, but not a data-quality-specific system
  - lower face-validity for operational data-quality monitoring than systems such as `Deequ`
- Verdict: `recommended`

## COPOD

- Detector id: `copod`
- Code: official `PyOD` implementation
- Source repo: https://github.com/yzhao062/pyod
- Paper: Zhenyu Li, Yue Zhao, Nicola Botta, Cezar Ionescu, Xiyang Hu, `COPOD: Copula-Based Outlier Detection`
- Paper links:
  - arXiv: https://arxiv.org/abs/2009.09463
  - dblp entry: https://dblp.org/rec/journals/corr/abs-2009-09463
- Benchmark evidence:
  - The paper reports experiments on `30 benchmark datasets` and releases a Python implementation through `PyOD`
  - In Bouman, Bukhsh, and Heskes, JMLR 2024, `COPOD` appears in the top overall ranking table with mean `AUC = 0.831`, ahead of `ECOD` in that same table: https://www.jmlr.org/papers/volume25/23-0570/23-0570.pdf
- Why it fits this project:
  - same adapter shape as `ECOD`
  - vector-in / score-out
  - easy to run under the existing detector contract
- Risks:
  - same caveat as `ECOD`: generic OD baseline rather than a dedicated data-quality monitoring system
- Verdict: `recommended`

## Extended Isolation Forest

- Detector id: `extended_isolation_forest`
- Code: official author implementation in package `eif`
- Source repo: https://github.com/sahandha/eif
- Install path published by the repo:
  - `pip install eif`
  - `pip install git+https://github.com/sahandha/eif.git`
- Paper: Sahand Hariri, Matias Carrasco Kind, Robert J. Brunner, `Extended Isolation Forest`
- Paper links:
  - DOI: https://doi.org/10.1109/TKDE.2019.2947676
  - arXiv: https://arxiv.org/abs/1811.02141
- Benchmark evidence:
  - Bouman, Bukhsh, and Heskes, JMLR 2024 evaluate `33` unsupervised algorithms on `52` real-world multivariate tabular datasets and report that `EIF` significantly outperforms most other algorithms overall, is the top performer on the global subset, and is the recommended default when users do not know whether anomalies are local or global: https://www.jmlr.org/papers/volume25/23-0570/23-0570.pdf
  - The same JMLR benchmark states that it used the public `eif` implementation by the authors
- Why it fits this project:
  - direct vector input
  - direct anomaly-score output
  - closest external upgrade path from the existing `Isolation Forest` baseline
- Risks:
  - smaller and less actively maintained ecosystem than `PyOD`
  - in local validation for this repository on `April 1, 2026`, `eif==2.0.2` built successfully only after pinning `Cython<3`; this integration risk is now documented in the project install path
- Verdict: `recommended`, with explicit build caveat

## kNN

- Detector id: `knn`
- Code: public `PyOD` implementation of distance-based k-nearest-neighbor outlier scoring
- Source repo: https://github.com/yzhao062/pyod
- Paper lineage:
  - S. Ramaswamy, R. Rastogi, K. Shim, `Efficient Algorithms for Mining Outliers from Large Data Sets`
  - ACM DOI: https://doi.org/10.1145/342009.335437
  - DBLP: https://dblp.org/rec/conf/sigmod/RamaswamyRS00
- Benchmark evidence:
  - `ADBench` compares `30` algorithms on `57` datasets and includes classical distance-based baselines in its open benchmark protocol: https://papers.neurips.cc/paper_files/paper/2022/file/cf93972b116ca5268827d575f2cc226b-Paper-Datasets_and_Benchmarks.pdf
  - Bouman, Bukhsh, and Heskes, JMLR 2024 report that `kNN` is the strongest choice on their local-anomaly subset, while `EIF` is stronger on the global-anomaly subset: https://www.jmlr.org/papers/volume25/23-0570/23-0570.pdf
- Why it fits this project:
  - adds explicit local-neighborhood coverage that the locked baselines and official appendix would otherwise underrepresent
  - vector-in / score-out detector under the same clean-calibration threshold policy
  - strong contrast case against `EIF` for the local-vs-global anomaly distinction
- Risks:
  - memory and distance-computation cost can grow faster than tree-based or empirical-distribution detectors
  - still a generic tabular OD detector rather than a dedicated recurring DQ system
- Verdict: `recommended`

## LOF

- Detector id: `lof`
- Code: official `scikit-learn` `LocalOutlierFactor` implementation
- Source repo: https://github.com/scikit-learn/scikit-learn
- Paper lineage:
  - Markus M. Breunig, Hans-Peter Kriegel, Raymond T. Ng, Jorg Sander, `LOF: Identifying Density-Based Local Outliers`
  - ACM DOI: https://doi.org/10.1145/335191.335388
  - PDF mirror via LMU: https://www.dbs.ifi.lmu.de/Publikationen/Papers/LOF.pdf
- Benchmark evidence:
  - `ADBench` includes `LOF` in its large open benchmark comparison across `57` datasets and `30` algorithms: https://papers.neurips.cc/paper_files/paper/2022/file/cf93972b116ca5268827d575f2cc226b-Paper-Datasets_and_Benchmarks.pdf
  - `PyOD` and `scikit-learn` both keep `LOF` as a maintained baseline family because it remains a standard local-density comparator in tabular anomaly studies: https://github.com/yzhao062/pyod and https://scikit-learn.org/stable/modules/outlier_detection.html
- Why it fits this project:
  - strengthens local-density anomaly coverage beyond distance-only `kNN`
  - uses a mature upstream implementation with well-documented semantics
  - remains easy to adapt to batch-profile vectors without changing the public contract
- Risks:
  - less interpretable than simple threshold and history baselines
  - sensitivity to neighborhood size and calibration density can make threshold portability harder than for some simpler detectors
- Verdict: `recommended`

## One-Class SVM

- Detector id: `one_class_svm`
- Code: official `scikit-learn` `OneClassSVM` implementation
- Source repo: https://github.com/scikit-learn/scikit-learn
- Paper lineage:
  - Bernhard Scholkopf, John C. Platt, John Shawe-Taylor, Alex J. Smola, Robert C. Williamson, `Estimating the Support of a High-Dimensional Distribution`
  - DOI: https://doi.org/10.1162/089976601750264965
  - PDF mirror: https://alex.smola.org/papers/2001/SchPlaShaSmoetal01.pdf
- Benchmark evidence:
  - `ADBench` includes `OCSVM` among its open benchmark algorithm set and shows that no single unsupervised detector dominates across all anomaly types or datasets: https://papers.neurips.cc/paper_files/paper/2022/file/cf93972b116ca5268827d575f2cc226b-Paper-Datasets_and_Benchmarks.pdf
  - `scikit-learn` maintains `OneClassSVM` as one of its canonical outlier-detection estimators: https://scikit-learn.org/stable/modules/outlier_detection.html
- Why it fits this project:
  - adds a classical boundary-learning family to the appendix-level comparison
  - uses a widely adopted upstream implementation rather than a custom local reimplementation
  - provides a contrast case to tree-, distance-, and density-based appendix detectors
- Risks:
  - kernel methods can be slower and more sensitive to scaling than the other appendix detectors
  - may require tighter runtime-policy reporting because fit cost can rise quickly with larger calibration sets
- Verdict: `recommended with runtime caveat`

## Repository Integration Notes

- Existing scaffolded config files:
  - `configs/detectors/ecod.yaml`
  - `configs/detectors/copod.yaml`
  - `configs/detectors/extended_isolation_forest.yaml`
- Existing example experiment configs:
  - `configs/experiments/tlc_pilot_ecod.yaml`
  - `configs/experiments/tlc_pilot_copod.yaml`
  - `configs/experiments/tlc_pilot_eif.yaml`
- Existing Python adapters:
  - `src/dqbench/baselines/ecod.py`
  - `src/dqbench/baselines/copod.py`
  - `src/dqbench/baselines/extended_isolation_forest.py`
- Additional official appendix deliverables still required by the specification:
  - pinned upstream integrations for `kNN`, `LOF`, and `One-Class SVM`
  - deterministic detector config manifests for all six appendix detectors
  - smoke tests and contract-validation coverage for all six appendix detectors
