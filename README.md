# FastWAM / OpenWAM RoboTwin Experiments

This repository contains the code, evaluation runners, manifests, historical
run outputs, and documentation used for the World Modeling experiments.

Large model files and simulator assets are intentionally excluded. In
particular, restore these locally before running:

- OpenWAM Wan2.2-TI2V-5B base model assets
- OpenWAM clean40 action-only and full-WM checkpoints
- FastWAM checkpoints and base model assets
- RoboTwin object, embodiment, and background assets

The main Experiment 3 runner and existing results are under `experiment3/`.
Machine-local absolute paths in checkpoint `config.yaml` and Experiment 3 JSON
configuration files must be updated after cloning to another machine.

## Layout

- `OpenWAM/`: OpenWAM source plus local checkpoint-loading compatibility changes
- `FastWAM/`: FastWAM source plus RoboTwin evaluation changes
- `experiment3/`: Experiment 3 runner, manifests, scripts, and historical runs
- `work/RoboTwin-openwam-verified/`: verified RoboTwin source used by OpenWAM
- `guide_docs/`: experiment design and current result summaries

