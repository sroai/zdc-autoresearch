#!/usr/bin/env python3
"""Generate the gun datasets D1 to D4 (configs/datasets.yaml, section guns).

For every gun, momentum and seed: run the benchmark's ROOT generator macro to
write a HepMC file, then npsim with the ZDC-only detector configuration, inside
the pinned image. Outputs land in {datasets_root}/<gun>/<gun>_<p>GeV_seed<s>.edm4hep.root
with the HepMC file beside it; every step logs to {logs_root}/sim/. Points that
already exist with the expected event count are skipped, so the script resumes.
At the end the manifest {space}/perf/manifest-datasets.json is (re)written for
the gun section.

Usage:
  uv run scripts/110_generate_guns.py                 # everything in the config
  uv run scripts/110_generate_guns.py --only D1_pi0   # one gun
  uv run scripts/110_generate_guns.py --only D1_pi0 --momenta 100 --seeds 1 --events 50 --dry-run
  uv run scripts/110_generate_guns.py --jobs 8        # parallel npsim processes (default: profile cores / 2)

The generator macros take (n_events, seed, out_file, p_min, p_max); the
benchmarks call them at a single momentum (p_min = p_max). gen_particles.cxx
(photons) takes the particle name as well. A gun whose `generator` is
`python-gun` (D3, the neutron scan) gets its HepMC file written here, without
ROOT: one particle per event from the IP, uniform within theta_max_mrad of the
proton axis. Step 0 verifies every macro signature on a 10-event run first.
The dataset ids D1h/D4h (held-out) and D1n/D4n (noise validation) are ordinary
guns here; their role is fixed in zdc-setup.md.
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import REPO_ROOT, datasets_config, load_profile, repo_path  # noqa: E402

WRAPPER = repo_path("scripts", "100_in_container.sh")


def to_container(path, profile):
    """Host path -> container path (repo at /work, data root at /data)."""
    s = str(path)
    return s.replace(str(REPO_ROOT), profile.repo_mount, 1).replace(str(profile.data_root), profile.data_mount, 1)


def macro_call(gun_cfg, generator_c, n_events, seed, out_hepmc_c, momentum, theta_max_mrad):
    """The ROOT command line for one generator point.

    gen_particles.cxx (zdc_photon) has the signature
    (n_events, seed, out, particle, p_min, p_max, theta_min, theta_max); the
    decay generators have (n_events, seed, out, p_min, p_max). Step 0 checks
    both signatures against the macro headers before the full production.
    """
    if gun_cfg.macro == "gen_particles":
        args = f'{n_events},{seed},"{out_hepmc_c}","{gun_cfg.get("particle", "gamma")}",{momentum},{momentum},0.0,{theta_max_mrad}'
    else:
        args = f'{n_events},{seed},"{out_hepmc_c}",{momentum},{momentum}'
    return f"root -l -b -q '{generator_c}({args})'"


PDG_MASS_GEV = {2112: 0.9395654, 22: 0.0, 211: 0.1395704, -211: 0.1395704, 2212: 0.9382721}
PDG_BY_NAME = {"neutron": 2112, "gamma": 22, "pi+": 211, "pi-": -211, "proton": 2212}


def write_python_gun(path, particle, n_events, seed, momentum, theta_max_mrad, crossing_angle=-0.025):
    """A HepMC3 ASCII file with one `particle` per event from the IP, uniform in θ ≤ theta_max
    around the proton beam axis (rotated by the crossing angle, as the benchmark generators do)
    and uniform in φ. Beam particles carry status 4, the gun particle status 1, so npsim treats
    the file like the benchmarks' own output. No ROOT needed; the seed makes it reproducible."""
    import math
    import random
    rng = random.Random(seed)
    pdg = PDG_BY_NAME[particle]
    mass = PDG_MASS_GEV[pdg]
    with open(path, "w") as f:
        f.write("HepMC::Version 3.02.05\nHepMC::Asciiv3-START_EVENT_LISTING\n")
        for ev in range(n_events):
            theta = rng.uniform(0.0, theta_max_mrad / 1000.0)
            phi = rng.uniform(0.0, 2 * math.pi)
            px, py, pz = momentum * math.cos(phi) * math.sin(theta), momentum * math.sin(phi) * math.sin(theta), momentum * math.cos(theta)
            # rotate about y by the crossing angle: the proton beam points at (sin a, 0, cos a)
            a = crossing_angle
            px, pz = px * math.cos(a) + pz * math.sin(a), -px * math.sin(a) + pz * math.cos(a)
            e = math.sqrt(px * px + py * py + pz * pz + mass * mass)
            f.write(f"E {ev} 1 3\nU GEV MM\n")
            f.write("P 1 0 11 0.0 0.0 10.0 10.0 0.000511 4\n")
            f.write("P 2 0 2212 0.0 0.0 0.0 0.938 0.938 4\n")
            f.write("V -1 0 [1,2]\n")
            f.write(f"P 3 -1 {pdg} {px:.9g} {py:.9g} {pz:.9g} {e:.9g} {mass:.9g} 1\n")
        f.write("HepMC::Asciiv3-END_EVENT_LISTING\n")


def run_point(profile, cfg, gun_id, gun_cfg, momentum, seed, n_events, args, dry_run):
    out_dir = Path(profile.datasets_root) / gun_id
    logs = Path(profile.logs_root) / "sim"
    out_dir.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    stem = f"{gun_id}_{momentum}GeV_seed{seed}"
    hepmc = out_dir / f"{stem}.hepmc"
    edm4hep = out_dir / f"{stem}.edm4hep.root"
    if edm4hep.exists() and edm4hep.stat().st_size > 0:
        return stem, "exists"
    theta_max = float(cfg.get("theta_max_mrad", 4.0))
    detector_config = args.detector_config or cfg.detector_config_guns
    if gun_cfg.generator == "python-gun":
        if not dry_run:
            write_python_gun(hepmc, gun_cfg.particle, n_events, seed, momentum, theta_max)
        gen_cmd = "true"
    else:
        generator_c = f"{profile.repo_mount}/{gun_cfg.generator}"
        gen_cmd = macro_call(gun_cfg, generator_c, n_events, seed, to_container(hepmc, profile), momentum, theta_max)
    sim_cmd = (
        f"npsim --compactFile $DETECTOR_PATH/{detector_config}.xml --random.seed {seed} "
        f"--numberOfEvents {n_events} --physicsList {cfg.physics_list} "
        f"--inputFiles {to_container(hepmc, profile)} --outputFile {to_container(edm4hep, profile)} -v WARNING"
    )
    full = f"set -e; cd /work; {gen_cmd} && {sim_cmd}"
    if dry_run:
        print(f"[dry-run] {stem}: {full}")
        return stem, "dry-run"
    log = logs / f"{stem}.log"
    with open(log, "w") as lf:
        rc = subprocess.call([str(WRAPPER), "bash", "-c", full], stdout=lf, stderr=subprocess.STDOUT)
    if rc != 0 or not edm4hep.exists():
        return stem, f"FAILED (rc={rc}, log {log})"
    return stem, "ok"


def points(gun_id, gun_cfg, args):
    momenta = args.momenta or list(gun_cfg.momenta_gev)
    base_seeds = args.seeds or list(gun_cfg.seeds)
    for p in momenta:
        seeds = list(base_seeds)
        extra = gun_cfg.get("extra_seeds", {}) or {}
        if not args.seeds and p in extra:
            seeds += list(extra[p])
        for s in seeds:
            yield p, s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", help="gun id(s) to generate (default: all)")
    ap.add_argument("--momenta", type=int, nargs="*", help="override the momenta (GeV)")
    ap.add_argument("--seeds", type=int, nargs="*", help="override the seeds (also drops extra_seeds)")
    ap.add_argument("--events", type=int, help="override the event count per point")
    ap.add_argument("--jobs", type=int, help="parallel npsim processes")
    ap.add_argument("--detector-config", help="override detector_config_guns (e.g. the SiPM-only cross-check)")
    ap.add_argument("--dry-run", action="store_true", help="print the commands, run nothing")
    args = ap.parse_args()

    profile = load_profile()
    cfg = datasets_config()
    jobs = args.jobs or max(1, int(profile.cores) // 2)
    guns = {k: v for k, v in cfg.guns.items() if not args.only or k in args.only}
    if not guns:
        sys.exit(f"no gun matches {args.only}; known: {list(cfg.guns)}")

    work = []
    for gun_id, gun_cfg in guns.items():
        n_events = args.events or int(gun_cfg.events)
        for p, s in points(gun_id, gun_cfg, args):
            work.append((gun_id, gun_cfg, p, s, n_events))
    print(f"{len(work)} points, {jobs} parallel")
    results = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(run_point, profile, cfg, g, gc, p, s, n, args, args.dry_run) for g, gc, p, s, n in work]
        for fut in futures:
            stem, status = fut.result()
            print(f"{status:10s} {stem}")
            results.append((stem, status))
    failed = [s for s, st in results if st.startswith("FAILED")]
    if failed:
        print(f"ERROR: {len(failed)} point(s) failed: {failed}")
        sys.exit(1)
    if not args.dry_run:
        manifest = repo_path("space", "perf", "manifest-datasets.json")
        subprocess.check_call([sys.executable, str(repo_path("scripts", "121_manifest.py")), "write", str(manifest),
                               *[str(Path(profile.datasets_root) / g) for g in guns], "--section", "guns"])
        print(f"manifest updated: {manifest}")


if __name__ == "__main__":
    main()
