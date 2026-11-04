# Environment a run needs

Host (the user's workstation, CachyOS, 24 cores, 62 GB RAM, `/data` btrfs):

- docker, with the image `eicweb/eic_xl:26.11.0-stable` pulled (about 5 GB
  compressed): `docker pull eicweb/eic_xl:26.11.0-stable`. Not present on
  2026-11-04 (only `25.10.4-stable` is local).
- `uv` for the Python scripts (`uv run scripts/<name>.py`); dependencies in
  `pyproject.toml` (uproot, awkward, numpy, scipy, matplotlib, omegaconf,
  pyyaml).
- `gh` (authenticated) for reading issues and PRs.
- The ssh tunnel to ifarm (`docs/ifarm-tunnel.md`) for Phase 4 and for the
  MSF files that are not local.

Inside the container: `source /opt/detector/epic-main/bin/thisepic.sh`
loads epic, npsim, eicrecon, ROOT. The custom EICrecon install is prepended
by `scripts/100_in_container.sh` when `EICRECON_INSTALL` is set.

Farm: `/cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:26.11.0-stable`.
