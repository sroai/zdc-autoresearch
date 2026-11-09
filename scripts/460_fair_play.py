#!/usr/bin/env python3
"""Fair play of a Phase 4 experiment (zdc-autoresearch-loop-v4.md, F1-F3; operational wording D-default-43).

F1 truth-blind reconstruction
  F1a static walk: the JOmniFactoryGeneratorT registrations of src/detectors/*/*.cc and src/global/*/*.cc
      of the experiment's as-built source (`git show <commit>:<path>`, no checkout), walked from
      ReconstructedLambdas back to `*RawHits` leaves. FAIL on a factory type containing "Truth"; on an input
      named like truth (MCParticle, MCBeam, Truth, Association, Link, Sim, EventHeader, MCReco) unless it is a
      Link/Association input of the frozen CoG or ClusterShape factories (they only pass associations
      through); on an input no factory produces that is not `*RawHits` (read from the file); on a
      registration in the cone whose collection lists are not string literals.
  F1b patch: the added lines of `git diff <pin> <commit> -- src/` (tests and benchmarks excluded) may not name
      truth (MC particles, sim hits, associations, links, the event header, event or run numbers, the input
      file) nor carry a dataset-keyed constant (three or more D4 momenta, a seed, a dataset name).
  F1c parameters: no InputTags / OutputTags override in the experiment's parameters (rewire in code).
  F1d run time: janadot on a few D4 events with the experiment's install, parameters and detector config;
      every factory reached from ReconstructedLambdas must be in the static cone of F1a.
F2 the data are the data
  F2a every digitization registration (factory type containing "Digi") is identical to the pin's, and no
      parameter of the experiment addresses a digitization factory.
  F2b the raw hits the chain starts from (F1a's leaves present in the output, the ZDC ones required) are
      byte-identical to R0 on the D4 275 GeV file (130's compare, restricted to those collections).
F3 honest candidates (read from the experiment's D4 outputs)
  F3a at most one ReconstructedLambdas entry per event.
  F3b exactly three daughters, PDG {2112, 22, 22}, each in a Reconstructed*Neutrals collection.
  F3c the photons' cluster lists are disjoint; the neutron's is disjoint from both or is the whole cluster
      collection of its event (the stock link-all).
  F3d |E_Λ − ΣE_daughters| ≤ 1e-4 GeV.
  F3e fewer than 5 % of the candidates (≥ 20 of them) store a mass within 0.1 MeV of m_Λ (no mass constraint).
  F3f ZDC photon neutrals of one event have disjoint cluster lists and each carries ≥ 0.25 of its clusters' energy.

Any FAIL makes the experiment FOUL. Writes space/perf/fair-play-<experiment>.json and prints one line per check.

Usage:
  uv run scripts/460_fair_play.py configs/experiments/R0_stock.yaml
  uv run scripts/460_fair_play.py configs/experiments/X1_offline_chain.yaml            # source_commit: in the yaml
  uv run scripts/460_fair_play.py configs/experiments/R1_pr3064.yaml --source 70e5ca69 --no-dynamic
  uv run scripts/460_fair_play.py <yaml> --reco-dir /data/.../gate-controls/phase4/ctlF3   # a control's outputs
"""
import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import REPO_ROOT, datasets_config, load_profile, load_yaml, repo_path  # noqa: E402
from zdc.edm import collection_ids  # noqa: E402

PIN = "e5e2a60c60b6a10a25cbe35497da1d4996a492df"
EIC = repo_path("submodules", "EICrecon")
PERF = repo_path("space", "perf")
# As-built sources of the reference rows (the phase3 branch records each try as a commit, D-user-34).
SOURCES = {"R0_stock": PIN, "R2_pr3114": PIN, "L01_box3114": PIN, "R1_pr3064": "70e5ca69", "P1d_R1_nlr1": "70e5ca69",
           "Rt_truthchain": "fdaae7a6", "R3_pr3063": "bfac4276", "B9d_stable_vertex": "2aa25e17",
           "B9e_neutron_leader": "0734e166"}
START = "ReconstructedLambdas"
TRUTH_NAME = re.compile(r"MCParticle|MCBeam|Truth|Association|Link|Sim[A-Z_]|^Sim|EventHeader|MCReco|GeneratedParticles")
PASS_THROUGH = ("CalorimeterClusterRecoCoG_factory", "CalorimeterClusterShape_factory")   # frozen (F4, D-default-43)
TRUTH_CODE = re.compile(r"MCParticle|MCBeam|Truth|Association|SimCalorimeterHit|SimTrackerHit|RawHitLink|ClusterLink|"
                        r"MCReco|EventHeader|getEventNumber|getRunNumber|getContributions|CaloHitContribution|"
                        r"podio:input|input_file|getMCParticle|edm4hep::MC")
DATASET_CODE = re.compile(r"GeV_seed|\bseed[0-9]|D4_lambda|D4h_|\.edm4hep\.root")
D4_MOMENTA = ("100", "125", "150", "175", "200", "225", "250", "275")
M_LAMBDA = 1.115683


def git(*args):
    return subprocess.run(["git", "-C", str(EIC), *args], capture_output=True, text=True, check=True).stdout


# ---------------------------------------------------------------- registrations
def strip_comments(text):
    """C++ text without // and /* */ comments, string literals kept."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\":
                out.append(text[i + 1]); i += 2; continue
            if c == '"':
                in_str = False
            i += 1
        elif c == '"':
            in_str = True; out.append(c); i += 1
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2); i = n if j < 0 else j + 2
        else:
            out.append(c); i += 1
    return "".join(out)


def split_top(arg_text):
    """Split a call's argument text at depth-0 commas (parentheses, braces, brackets, strings)."""
    parts, depth, cur, in_str, i = [], 0, [], False, 0
    while i < len(arg_text):
        c = arg_text[i]
        if in_str:
            cur.append(c)
            if c == "\\":
                cur.append(arg_text[i + 1]); i += 2; continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True; cur.append(c)
        elif c in "({[":
            depth += 1; cur.append(c)
        elif c in ")}]":
            depth -= 1; cur.append(c)
        elif c == "," and depth == 0:
            parts.append("".join(cur).strip()); cur = []
        else:
            cur.append(c)
        i += 1
    if "".join(cur).strip():
        parts.append("".join(cur).strip())
    return parts


def literal_list(arg):
    """(names, is_literal) for a `{"a", "b"}` argument."""
    names = re.findall(r'"((?:[^"\\]|\\.)*)"', arg)
    rest = re.sub(r'"(?:[^"\\]|\\.)*"', "", arg)
    literal = arg.startswith("{") and re.fullmatch(r"[\s{},]*", rest) is not None
    return names, literal


def parse_registrations(text, fname):
    text = strip_comments(text)
    regs = []
    for m in re.finditer(r"JOmniFactoryGeneratorT\s*<", text):
        i, depth = m.end(), 1
        while depth:
            depth += {"<": 1, ">": -1}.get(text[i], 0); i += 1
        ftype = re.sub(r"\s+", "", text[m.end():i - 1])
        j = i
        while j < len(text) and text[j].isspace():
            j += 1
        if j >= len(text) or text[j] != "(":
            continue
        k, depth, in_str = j, 0, False
        while True:
            c = text[k]
            if in_str:
                if c == "\\":
                    k += 2; continue
                if c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        args = split_top(text[j + 1:k])
        tag = re.fullmatch(r'"([^"]*)"', args[0]).group(1) if args and re.fullmatch(r'"([^"]*)"', args[0]) else None
        ins, lit_in = literal_list(args[1]) if len(args) > 1 else ([], False)
        outs, lit_out = literal_list(args[2]) if len(args) > 2 else ([], False)
        regs.append({"type": ftype, "tag": tag, "inputs": [x for x in ins if x], "outputs": [x for x in outs if x],
                     "literal": bool(tag) and lit_in and lit_out, "file": fname,
                     "text": re.sub(r"\s+", " ", text[m.start():k + 1])})
    return regs


def sources_at(commit=None, tree=None):
    """{path: text} of src/detectors/*/*.cc and src/global/*/*.cc at a commit, or under a directory (a control tree)."""
    if tree:
        return {str(f.relative_to(tree)): f.read_text() for f in sorted(Path(tree).glob("src/*/*/*.cc"))
                if re.fullmatch(r"src/(detectors|global)/[^/]+/[^/]+\.cc", str(f.relative_to(tree)))}
    files = [f for f in git("ls-tree", "-r", "--name-only", commit, "src/detectors", "src/global").split()
             if re.fullmatch(r"src/(detectors|global)/[^/]+/[^/]+\.cc", f)]
    return {f: git("show", f"{commit}:{f}") for f in files}


def registrations_of(sources):
    regs = []
    for f, text in sources.items():
        regs += parse_registrations(text, f)
    return regs


def walk(regs):
    """F1a: the cone of ReconstructedLambdas. Returns (cone registrations, leaves, failures, notes)."""
    producers = {}
    for r in regs:
        for o in r["outputs"]:
            producers.setdefault(o, []).append(r)
    cone, leaves, failures, notes, seen = [], set(), [], [], set()
    stack = [START]
    while stack:
        coll = stack.pop()
        if coll in seen:
            continue
        seen.add(coll)
        if coll.endswith("RawHits"):
            leaves.add(coll); continue
        prods = producers.get(coll)
        if not prods:
            failures.append(f"{coll}: no factory produces it and it is not *RawHits (read from the input file)")
            continue
        if len(prods) > 1:
            notes.append(f"{coll}: {len(prods)} registrations produce it ({', '.join(p['file'] for p in prods)}); all walked")
        for r in prods:
            if r in cone:
                continue
            cone.append(r)
            if not r["literal"]:
                failures.append(f"{r['file']} {r['type']} {r['tag']}: collection lists are not string literals")
            if "Truth" in r["type"]:
                failures.append(f"{r['file']} {r['type']} {r['tag']}: a truth factory in the chain")
            for i in r["inputs"]:
                if TRUTH_NAME.search(i):
                    if r["type"] in PASS_THROUGH and re.search(r"Link|Association", i):
                        notes.append(f"{r['tag']} reads {i}: exempt (frozen {r['type']} passes associations through)")
                        continue
                    failures.append(f"{r['file']} {r['type']} {r['tag']} reads {i}")
                    continue
                stack.append(i)
    return cone, leaves, failures, notes


# ---------------------------------------------------------------- checks
def check_patch(commit, tree_sources=None, pin_sources=None):
    """F1b: added source lines of pin..commit (or pin..control tree), comments stripped."""
    if tree_sources is not None:
        import difflib
        diff = ""
        for f, text in tree_sources.items():
            old = (pin_sources or {}).get(f, "")
            if old != text:
                diff += f"+++ b/{f}\n" + "".join(l + "\n" for l in difflib.unified_diff(old.splitlines(), text.splitlines(), n=0, lineterm="")
                                            if not l.startswith(("---", "+++")))
    elif commit == PIN or git("rev-parse", commit).strip() == PIN:
        return [], ["the pin itself: no patch"]
    else:
        diff = git("diff", "--unified=0", PIN, commit, "--", "src/")
    failures, fname, n_added = [], None, 0
    for line in diff.splitlines():
        if line.startswith("+++ "):
            fname = line[6:] if line.startswith("+++ b/") else None
            continue
        if not line.startswith("+") or fname is None or re.match(r"src/(tests|benchmarks)/", fname):
            continue
        n_added += 1
        code = strip_comments(line[1:])
        if not code.strip():
            continue
        if TRUTH_CODE.search(code):
            failures.append(f"{fname}: names truth: {code.strip()[:140]}")
        if DATASET_CODE.search(code) or sum(bool(re.search(rf"(?<![\d.]){p}(?![\d])", code)) for p in D4_MOMENTA) >= 3:
            failures.append(f"{fname}: dataset-keyed constant: {code.strip()[:140]}")
    return failures, [f"{n_added} added source lines scanned"]


def check_parameters(exp, regs):
    """F1c (rewiring) and the parameter half of F2a (digitization factories)."""
    f1, f2 = [], []
    digi_tags = {r["tag"] for r in regs if "Digi" in r["type"] and r["tag"]}
    for key in (exp.get("parameters") or {}):
        if re.search(r"InputTags|OutputTags|input_tags|output_tags|wiring", key):
            f1.append(f"parameter {key} rewires a factory")
        parts = key.split(":")
        if len(parts) >= 3 and parts[1] in digi_tags:
            f2.append(f"parameter {key} changes a digitization factory")
    return f1, f2


def check_digi(regs, pin_regs):
    """F2a: every digitization registration as at the pin."""
    norm = lambda rs: {(r["file"], r["tag"]): r["text"] for r in rs if "Digi" in r["type"]}
    a, b = norm(pin_regs), norm(regs)
    fails = [f"{k[0]} {k[1]}: digitization registration differs from the pin" for k in sorted(set(a) | set(b))
             if a.get(k) != b.get(k)]
    return fails, [f"{len(b)} digitization registrations compared"]


def run_janadot(exp, install, profile, nevents=5):
    """F1d: factory names reached from ReconstructedLambdas at run time (janadot), or raise."""
    dcfg = datasets_config()
    spec = importlib.util.spec_from_file_location("reco120", repo_path("scripts", "120_reconstruct.py"))
    r120 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r120)
    det = r120.detector_config_for("D4_lambda", dcfg)
    work = Path(profile.tmp_root) / f"janadot-{exp.name}"
    work.mkdir(parents=True, exist_ok=True)
    for old in work.glob("*"):
        if old.is_file():
            old.unlink()   # our own scratch files of a previous 460 run in this folder
    infile = Path(profile.datasets_root) / "D4_lambda" / "D4_lambda_275GeV_seed1.edm4hep.root"
    params = " ".join(f"'-P{k}={v}'" for k, v in (exp.get("parameters") or {}).items())
    wc = r120.to_container(work, profile)
    shell = (f"cd {wc} && export DETECTOR_CONFIG={det} && eicrecon -Pplugins=janadot "
             f"-Ppodio:output_file={wc}/out.edm4eic.root -Ppodio:output_collections={START} "
             f"-Pjana:nevents={nevents} -Pnthreads=1 {params} {r120.to_container(infile, profile)} > {wc}/log.txt 2>&1")
    rc = subprocess.call([str(repo_path("scripts", "100_in_container.sh")), "bash", "-c", shell],
                         env={**__import__("os").environ, "EICRECON_INSTALL": r120.to_container(install, profile)})
    dot = work / "jana.dot"
    if rc != 0 or not dot.exists():
        raise RuntimeError(f"janadot run failed rc={rc} (log {work / 'log.txt'})")
    edges = re.findall(r'^\s*"([^"]+)" -> "([^"]+)"', dot.read_text(), re.M)
    graph = {}
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
    reached, stack = set(), [f":{START}"]
    while stack:
        n = stack.pop()
        if n in reached:
            continue
        reached.add(n)
        stack += list(graph.get(n, ()))
    return sorted(n.split(":", 1)[1] for n in reached if ":" in n and not n.startswith("podio"))


def raw_hit_compare(exp_file, ref_file, collections):
    spec = importlib.util.spec_from_file_location("cmp130", repo_path("scripts", "130_compare_collections.py"))
    c130 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c130)
    return c130.compare(str(ref_file), str(exp_file), list(collections), True, 0.0)


def f3_checks(files):
    """F3a-f over the D4 outputs. Returns (failures by clause, counters)."""
    fails = {k: [] for k in "abcdef"}
    stats = {"events": 0, "lambdas": 0, "near_mass": 0, "photons": 0, "photon_ratio_min": None}
    for path in files:
        ids = collection_ids(path)
        name_of = {v: k for k, v in ids.items()}
        t = uproot.open(path)["events"]
        have = {k.split("/")[-1] for k in t.keys()}
        L = t.arrays([f"{START}.energy", f"{START}.mass", f"{START}.particles_begin", f"{START}.particles_end",
                      f"_{START}_particles.index", f"_{START}_particles.collectionID"], library="ak")
        neutral_names = sorted({n for n in ids if re.fullmatch(r"Reconstructed\w*Neutrals", n)})
        N = {}
        for n in neutral_names:
            br = [f"{n}.PDG", f"{n}.energy", f"{n}.clusters_begin", f"{n}.clusters_end",
                  f"_{n}_clusters.index", f"_{n}_clusters.collectionID"]
            if all(b in have for b in br):
                a = t.arrays(br, library="ak")
                N[ids[n]] = (n, {b.split(".", 1)[1] if not b.startswith("_") else b.rsplit(".", 1)[1]: ak.to_list(a[b])
                                 for b in br})
        cl_n = {}
        for cname in ("HcalFarForwardZDCClusters",):
            if f"{cname}.energy" in have:
                cl_n[ids.get(cname)] = t[f"{cname}.energy"].array(library="ak")
        nev = t.num_entries
        stats["events"] += nev
        E = ak.to_list(L[f"{START}.energy"]); M = ak.to_list(L[f"{START}.mass"])
        pb = ak.to_list(L[f"{START}.particles_begin"]); pe = ak.to_list(L[f"{START}.particles_end"])
        pidx = ak.to_list(L[f"_{START}_particles.index"]); pcid = ak.to_list(L[f"_{START}_particles.collectionID"])
        tag = Path(path).name

        def clusters_of(cid, ev, i):
            a = N[cid][1]
            b, e = a["clusters_begin"][ev][i], a["clusters_end"][ev][i]
            return {(int(c), int(x)) for c, x in zip(a["collectionID"][ev][b:e], a["index"][ev][b:e])}

        for ev in range(nev):
            n_l = len(E[ev])
            if n_l > 1:
                fails["a"].append(f"{tag} event {ev}: {n_l} candidates")
            for li in range(n_l):
                stats["lambdas"] += 1
                if abs(M[ev][li] - M_LAMBDA) < 1e-4:
                    stats["near_mass"] += 1
                d = list(zip(pcid[ev][pb[ev][li]:pe[ev][li]], pidx[ev][pb[ev][li]:pe[ev][li]]))
                if len(d) != 3:
                    fails["b"].append(f"{tag} event {ev}: {len(d)} daughters"); continue
                if any(c not in N for c, _ in d):
                    fails["b"].append(f"{tag} event {ev}: a daughter outside the Reconstructed*Neutrals outputs "
                                      f"({[name_of.get(c, c) for c, _ in d]})"); continue
                pdg = sorted(int(N[c][1]["PDG"][ev][i]) for c, i in d)
                if pdg != [22, 22, 2112]:
                    fails["b"].append(f"{tag} event {ev}: daughters PDG {pdg}"); continue
                esum = sum(float(N[c][1]["energy"][ev][i]) for c, i in d)
                if abs(E[ev][li] - esum) > 1e-4:
                    fails["d"].append(f"{tag} event {ev}: E_Λ {E[ev][li]:.6f} vs Σ daughters {esum:.6f}")
                byp = {}
                for c, i in d:
                    byp.setdefault(int(N[c][1]["PDG"][ev][i]), []).append((c, i))
                g1, g2 = (clusters_of(c, ev, i) for c, i in byp[22])
                n_cl = clusters_of(byp[2112][0][0], ev, byp[2112][0][1])
                if g1 & g2:
                    fails["c"].append(f"{tag} event {ev}: the photons share {len(g1 & g2)} cluster(s)")
                if n_cl & (g1 | g2):
                    cids = {c for c, _ in n_cl}
                    whole = len(cids) == 1 and next(iter(cids)) in cl_n and \
                        n_cl == {(next(iter(cids)), k) for k in range(len(cl_n[next(iter(cids))][ev]))}
                    if not whole:
                        fails["c"].append(f"{tag} event {ev}: the neutron shares clusters with a photon and is not the link-all")
        # F3f: ZDC photon neutrals
        zid = ids.get("ReconstructedHcalFarForwardZDCNeutrals")
        zc = ids.get("HcalFarForwardZDCClusters")
        if zid in N and zc in cl_n:
            a = N[zid][1]
            pdgs, en, cb, ce, ci, cc = (a[k] for k in ("PDG", "energy", "clusters_begin", "clusters_end", "index", "collectionID"))
            cle = ak.to_list(cl_n[zc])
            for ev in range(nev):
                used = set()
                for k, p in enumerate(pdgs[ev]):
                    if p != 22:
                        continue
                    stats["photons"] += 1
                    mine = {(int(cc[ev][j]), int(ci[ev][j])) for j in range(cb[ev][k], ce[ev][k])}
                    if used & mine:
                        fails["f"].append(f"{tag} event {ev}: two photons share a cluster")
                    used |= mine
                    esum = sum(cle[ev][x] for c, x in mine if c == zc)
                    if esum > 0:
                        r = en[ev][k] / esum
                        stats["photon_ratio_min"] = r if stats["photon_ratio_min"] is None else min(stats["photon_ratio_min"], r)
                        if r < 0.25:
                            fails["f"].append(f"{tag} event {ev}: a photon carries {r:.3f} of its clusters' energy")
    if stats["lambdas"] >= 20 and stats["near_mass"] / stats["lambdas"] >= 0.05:
        fails["e"].append(f"{stats['near_mass']} of {stats['lambdas']} candidates within 0.1 MeV of m_Λ")
    return fails, stats


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment", help="configs/experiments/<name>.yaml")
    ap.add_argument("--source", help="EICrecon commit the experiment was built from (default: yaml source_commit, "
                                     "the reference table, or the pin)")
    ap.add_argument("--reco-dir", help="the D4 outputs (default reco/<name>/D4_lambda)")
    ap.add_argument("--reference-dir", help="R0's D4 outputs (default reco/R0_stock/D4_lambda)")
    ap.add_argument("--no-dynamic", action="store_true", help="skip janadot (a row without an install)")
    ap.add_argument("--tree", help="a control source tree (src/detectors, src/global) instead of a commit; static checks")
    ap.add_argument("--static-only", action="store_true", help="F1a-c and F2a only (a control tree with no outputs)")
    ap.add_argument("--match", help="F3 only on outputs whose name contains this")
    ap.add_argument("--tag", help="name of the JSON (default: the experiment name)")
    args = ap.parse_args()
    profile = load_profile()
    exp = load_yaml(args.experiment)
    name = args.tag or exp.name
    commit = args.source or exp.get("source_commit") or SOURCES.get(exp.name) or PIN
    commit = git("rev-parse", commit).strip()
    install = Path(profile.install_root) / (f"eicrecon-{exp.install_label}" if exp.get("install_label") else f"eicrecon-{PIN[:12]}")
    checks = []

    def add(rule, cid, fails, notes=(), status=None):
        st = status or ("FAIL" if fails else "PASS")
        checks.append({"rule": rule, "check": cid, "status": st, "failures": fails[:20], "n_failures": len(fails),
                       "notes": list(notes)[:20]})
        print(f"{st:5s} {rule} {cid}: {len(fails)} failure(s)" + (f" — {fails[0]}" if fails else "")
              + (f"  [{notes[0]}]" if notes and not fails else ""))

    t0 = time.time()
    pin_sources = sources_at(PIN)
    tree_sources = sources_at(tree=args.tree) if args.tree else None
    regs, pin_regs = registrations_of(tree_sources or sources_at(commit)), registrations_of(pin_sources)
    cone, leaves, f1a, n1a = walk(regs)
    nonlit = sum(not r["literal"] for r in regs)
    add("F1", "a static walk", f1a, [f"{len(regs)} registrations ({nonlit} non-literal, none in the cone unless listed)",
                                      f"cone {len(cone)} factories, leaves {sorted(leaves)}"] + n1a)
    f1b, n1b = check_patch(commit, tree_sources, pin_sources)
    add("F1", "b patch", f1b, n1b)
    f1c, f2p = check_parameters(exp, regs)
    add("F1", "c parameters", f1c)
    if args.static_only or args.tree:
        add("F1", "d janadot", [], ["skipped: static checks of a control tree"], status="SKIP")
    elif args.no_dynamic:
        add("F1", "d janadot", [], ["skipped (--no-dynamic): static F1 only"], status="SKIP")
    elif not install.exists():
        add("F1", "d janadot", [], [f"no install {install}: static F1 only"], status="SKIP")
    else:
        try:
            reached = run_janadot(exp, install, profile)
            known = {r["tag"] for r in cone} | {o for r in cone for o in r["outputs"]} | leaves
            extra = [n for n in reached if n not in known and n != START]
            add("F1", "d janadot", [f"factory {n} runs in the chain but is not in the static cone" for n in extra],
                [f"{len(reached)} factories reached at run time"])
        except RuntimeError as e:
            add("F1", "d janadot", [str(e)])
    f2a, n2a = check_digi(regs, pin_regs)
    add("F2", "a digitization code and parameters", f2a + f2p, n2a)
    reco = Path(args.reco_dir) if args.reco_dir else Path(profile.reco_root) / exp.name / "D4_lambda"
    refd = Path(args.reference_dir) if args.reference_dir else Path(profile.reco_root) / "R0_stock" / "D4_lambda"
    if args.static_only or args.tree:
        return finish(args, exp, name, commit, install, reco, [], checks, t0)
    efile, rfile = reco / "D4_lambda_275GeV_seed1.edm4eic.root", refd / "D4_lambda_275GeV_seed1.edm4eic.root"
    if not efile.exists():
        efile = next(iter(sorted(reco.glob("*.edm4eic.root"))), None)
        rfile = refd / efile.name if efile else None
    if efile is None or not efile.exists():
        add("F2", "b raw hits vs R0", [f"no D4 output under {reco}"])
    else:
        present = {k.split("/")[0].split(".")[0] for k in uproot.open(efile)["events"].keys()}
        pin_cone_leaves = walk(pin_regs)[1]
        required = {l for l in leaves if l.startswith(("HcalFarForwardZDC", "EcalFarForwardZDC")) or l not in pin_cone_leaves}
        missing = sorted(required - present)
        comp = sorted(l for l in leaves if l in present)
        if missing:
            add("F2", "b raw hits vs R0", [f"the chain's raw hits {missing} are not written (add them to the output)"])
        else:
            ok, msg = raw_hit_compare(efile, rfile, comp)
            add("F2", "b raw hits vs R0", [] if ok else [f"{efile.name}: {msg}"],
                [f"{efile.name}: {comp} identical to R0" if ok else msg,
                 f"leaves not written, covered by F2a: {sorted(leaves - present)}"])
    files = sorted(f for f in reco.glob("*.edm4eic.root") if ".part." not in f.name and (not args.match or args.match in f.name))
    if not files:
        add("F3", "a-f candidates", [f"no D4 outputs under {reco}"])
    else:
        f3, stats = f3_checks(files)
        labels = {"a": "one candidate per event", "b": "three daughters n γ γ from the neutrals",
                  "c": "disjoint cluster lists", "d": "E_Λ = Σ daughters", "e": "no Λ-mass constraint",
                  "f": "photons carry their clusters"}
        for k in "abcdef":
            add("F3", f"{k} {labels[k]}", f3[k], [json.dumps(stats)] if k == "a" else [])
    finish(args, exp, name, commit, install, reco, files, checks, t0)


def finish(args, exp, name, commit, install, reco, files, checks, t0):
    verdict = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"
    out = {"experiment": name, "config": str(args.experiment), "source_commit": commit, "tree": args.tree, "install": str(install),
           "reco_dir": str(reco), "files": [f.name for f in files], "verdict": verdict,
           "failed_rules": sorted({c["rule"] for c in checks if c["status"] == "FAIL"}),
           "checks": checks, "written": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
           "seconds": round(time.time() - t0, 1)}
    path = PERF / f"fair-play-{name}.json"
    path.write_text(json.dumps(out, indent=1))
    checked = " ".join(sorted({f"{c['rule']}{c['check'][0]}" for c in checks if c["status"] != "SKIP"}))
    print(f"{verdict} {name} (failed: {', '.join(out['failed_rules']) or 'none'}; checked {checked}) -> {path.relative_to(REPO_ROOT)}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
