# Supplementary External Reference Detectors

These detectors are shipped as optional reference adapters in the artifact. They are supplementary to the `5` locked baselines and do not change the primary leaderboard contract.

All three adapters:

- consume the same canonical batch-profile vectors as the locked baselines
- emit the same canonical alert schema
- use the same clean-calibration thresholding policy in the benchmark
- are table-scored anomaly detectors today, so they currently emit `table`-scoped alerts in this scaffold

Their benchmark interpretation follows the same claim boundary as the built-in baselines. A reference detector is not treated as high quality in this project on provenance alone; it is interpreted through four evidence layers:

- contract-valid execution on the canonical batch-profile interface
- performance on the transparent injected benchmark matrix
- false-positive behavior on the audited clean track
- descriptive transfer behavior on the `NYC 311` and `BTS` supplementary validation tracks

These layers do not turn the reference detectors into official replacements for the locked five baselines. They only provide stronger, more reproducible external comparison under the same benchmark contract.

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

## Repository Integration Notes

- Project config files:
  - `configs/detectors/ecod.yaml`
  - `configs/detectors/copod.yaml`
  - `configs/detectors/extended_isolation_forest.yaml`
- Example experiment configs:
  - `configs/experiments/tlc_pilot_ecod.yaml`
  - `configs/experiments/tlc_pilot_copod.yaml`
  - `configs/experiments/tlc_pilot_eif.yaml`
- Python adapters:
  - `src/dqbench/baselines/ecod.py`
  - `src/dqbench/baselines/copod.py`
  - `src/dqbench/baselines/extended_isolation_forest.py`
