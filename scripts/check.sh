#!/usr/bin/env bash
set -euo pipefail

pytest -q
python3 -m dqbench.orchestration.run_experiment --config configs/experiments/tlc_pilot.yaml
