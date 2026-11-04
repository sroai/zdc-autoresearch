"""Machine profile and program configs.

The machine profile (where data, builds, logs live on THIS machine) is one YAML
file: configs/local.yaml by default, another one through the ZDC_CONFIG
environment variable. Program configs (datasets, metrics, experiments) are plain
YAML files next to it. OmegaConf resolves the ${...} references inside a file;
there are no includes between files on purpose.
"""
import os
from pathlib import Path

from omegaconf import OmegaConf

REPO_ROOT = Path(__file__).resolve().parent.parent


def repo_path(*parts) -> Path:
    """A path inside the repository, independent of the current directory."""
    return REPO_ROOT.joinpath(*parts)


def load_profile() -> OmegaConf:
    """The machine profile: configs/local.yaml or $ZDC_CONFIG."""
    path = Path(os.environ.get("ZDC_CONFIG", repo_path("configs", "local.yaml")))
    if not path.exists():
        raise SystemExit(f"machine profile not found: {path} (set ZDC_CONFIG or create configs/local.yaml)")
    return OmegaConf.load(path)


def load_yaml(path) -> OmegaConf:
    """Any program config (datasets.yaml, metrics.yaml, an experiment file)."""
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"config not found: {path}")
    return OmegaConf.load(path)


def datasets_config() -> OmegaConf:
    return load_yaml(repo_path("configs", "datasets.yaml"))


def metrics_config() -> OmegaConf:
    return load_yaml(repo_path("configs", "metrics.yaml"))


def dataset_dir(profile, dataset_id: str) -> Path:
    """Where the frozen inputs of one dataset live: {datasets_root}/<id>/."""
    return Path(profile.datasets_root) / dataset_id


def reco_dir(profile, experiment: str, dataset_id: str) -> Path:
    """Where one experiment's reconstruction of one dataset lives."""
    return Path(profile.reco_root) / experiment / dataset_id


def install_dir(profile, eicrecon_sha: str) -> Path:
    """The EICrecon install prefix for one commit (short or full sha)."""
    return Path(profile.install_root) / f"eicrecon-{eicrecon_sha[:12]}"
