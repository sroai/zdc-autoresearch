#!/usr/bin/env python3
"""MSF compatibility gate (Phase 0, Step 0 item 6).

Question: do the campaign's DD4hep files (simulated with an older image) give the
same ZDC hits under the pinned EICrecon as the campaign's own reconstruction?
Only RawHits and RecHits are compared (cellID, hit count, energy per event):
clusters are not, since the campaign's older EICrecon made them.

The script reconstructs one D6a file with the R0 install, writing only the four
ZDC hit collections, then compares event by event with the campaign's reco file
of the same index. Verdict PASS = identical cellIDs, counts and energies in every
event; otherwise FAIL with the first differing event and the summary per
collection. Exit code 0 on PASS, 1 on FAIL.

Usage:
  uv run scripts/132_msf_hit_compat.py --dd4hep /data/zdc-autoresearch/datasets/D6a_local/msf_9x130_1000evt_0001.edm4hep.root \\
      --campaign-reco /data/meson-structure-2026-07/reco/9x130/msf_9x130_1000evt_0001.edm4eic.root
"""
import argparse
import subprocess
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import datasets_config, install_dir, load_profile, load_yaml, repo_path  # noqa: E402

COLLECTIONS = ["HcalFarForwardZDCRawHits", "HcalFarForwardZDCRecHits", "EcalFarForwardZDCRawHits", "EcalFarForwardZDCRecHits"]
# The leaf that carries the energy: RawHits store an ADC amplitude, RecHits a calibrated energy.
ENERGY_LEAF = {"Raw": "amplitude", "Rec": "energy"}


def reconstruct(profile, dd4hep, out, detector_config):
    install = install_dir(profile, load_yaml(repo_path("configs", "experiments", "R0_stock.yaml")).eicrecon_ref)
    cmd = (f"export DETECTOR_CONFIG={detector_config}; eicrecon -Pnthreads=1 "
           f"-Ppodio:output_collections={','.join(COLLECTIONS)} -Ppodio:output_file={out} {dd4hep}")
    log = Path(profile.logs_root) / "msf-compat.log"
    with open(log, "w") as lf:
        rc = subprocess.call([str(repo_path("scripts", "100_in_container.sh")), "bash", "-c", cmd],
                             stdout=lf, stderr=subprocess.STDOUT, env={**__import__("os").environ, "EICRECON_INSTALL": str(install)})
    if rc != 0:
        Path(out).unlink(missing_ok=True)  # eicrecon writes the file at init: a failed run must not leave one to be reused
        sys.exit(f"eicrecon failed (rc={rc}); log {log}")


def compare(ours_path, theirs_path):
    ours, theirs = uproot.open(ours_path)["events"], uproot.open(theirs_path)["events"]
    n = min(ours.num_entries, theirs.num_entries)
    print(f"events: ours {ours.num_entries}, campaign {theirs.num_entries}; comparing {n}")
    all_ok = True
    for coll in COLLECTIONS:
        leaf = ENERGY_LEAF["Raw" if "Raw" in coll else "Rec"]
        a_id = ours[f"{coll}/{coll}.cellID"].array(entry_stop=n)
        b_id = theirs[f"{coll}/{coll}.cellID"].array(entry_stop=n)
        a_e = ours[f"{coll}/{coll}.{leaf}"].array(entry_stop=n)
        b_e = theirs[f"{coll}/{coll}.{leaf}"].array(entry_stop=n)
        na, nb = ak.num(a_id), ak.num(b_id)
        count_diff = np.flatnonzero(ak.to_numpy(na != nb))
        # Hit order may differ between versions: compare sorted cellIDs and energy sums per event.
        same_ids = np.array([np.array_equal(np.sort(ak.to_numpy(x)), np.sort(ak.to_numpy(y))) for x, y in zip(a_id, b_id)])
        sa, sb = ak.to_numpy(ak.sum(a_e, axis=1)), ak.to_numpy(ak.sum(b_e, axis=1))
        same_sum = sa == sb
        ok = len(count_diff) == 0 and same_ids.all() and same_sum.all()
        all_ok &= ok
        first = np.flatnonzero(~(same_ids & same_sum))
        print(f"{'PASS' if ok else 'FAIL'} {coll}: hits ours {int(ak.sum(na))} campaign {int(ak.sum(nb))}; "
              f"events with different count {len(count_diff)}, different cellID set {int((~same_ids).sum())}, "
              f"different {leaf} sum {int((~same_sum).sum())}"
              + (f"; first differing event {first[0]}: {leaf} sum ours {sa[first[0]]:.6g} campaign {sb[first[0]]:.6g}" if len(first) else "")
              + (f"; median relative {leaf} difference {np.median(np.abs(sa - sb) / np.maximum(np.abs(sb), 1e-12)):.3g}" if not same_sum.all() else ""))
    return all_ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dd4hep", required=True)
    ap.add_argument("--campaign-reco", required=True)
    ap.add_argument("--detector-config", help="default: the D6a_local configuration (epic_craterlake_9x130)")
    ap.add_argument("--out", help="our reconstruction (default {reco_root}/msf-compat/<stem>.edm4eic.root)")
    args = ap.parse_args()
    profile = load_profile()
    out = Path(args.out or Path(profile.reco_root) / "msf-compat" / Path(args.dd4hep).name.replace(".edm4hep.root", ".edm4eic.root"))
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        reconstruct(profile, args.dd4hep, out, args.detector_config or datasets_config().msf.D6a_local.detector_config)
    ok = compare(out, args.campaign_reco)
    print("VERDICT", "PASS: D6 stays in the program" if ok else "FAIL: hits differ (see above)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
