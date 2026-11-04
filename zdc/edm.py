"""Readers and fits for edm4eic ROOT files, shared by the scoreboard and the plots.

Everything reads through uproot; nothing here needs ROOT or the container. The
collection names come from configs/metrics.yaml so a rename in EICrecon is fixed
in one place (Step 0 verifies them against a real file).
"""
from pathlib import Path

import awkward as ak
import numpy as np
import uproot
from scipy.optimize import curve_fit


def read_collection(paths, collection, fields):
    """Jagged arrays of the given fields of one collection: {field: ak.Array}.

    `fields` are the leaf names after the dot, e.g. ["energy", "position.x"].
    Returns one awkward array per field, one entry per event.
    """
    paths = [str(p) for p in (paths if isinstance(paths, (list, tuple)) else [paths])]
    branches = [f"{collection}.{f}" for f in fields]
    arrays = uproot.concatenate({p: "events" for p in paths}, expressions=branches, library="ak")
    return {f: arrays[f"{collection}.{f}"] for f in fields}


def list_collections(path):
    """Collection names present in a file's `events` tree (the podio branch names without leaves)."""
    with uproot.open(path) as f:
        names = set()
        for key in f["events"].keys():
            head = key.split(".")[0].split("/")[0]
            if head and not head.startswith("_") and head != "PARAMETERS":
                names.add(head)
        return sorted(names)


def n_events(path):
    with uproot.open(path) as f:
        return f["events"].num_entries


def gauss(x, amplitude, mu, sigma):
    return amplitude * np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))


def fit_peak(values, center, half_width, bins=100):
    """Gaussian fit around `center` ± `half_width`, the benchmarks' recipe.

    Returns (mu, sigma, mu_err, sigma_err, n_in_window) or None when the fit fails
    or fewer than 25 entries fall in the window (the benchmarks skip those too).
    """
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    window = values[np.abs(values - center) < half_width]
    if len(window) < 25:
        return None
    counts, edges = np.histogram(window, bins=bins, range=(center - half_width, center + half_width))
    centers = (edges[1:] + edges[:-1]) / 2
    p0 = [counts.max(), np.median(window), np.std(window) or half_width / 5]
    try:
        coeff, cov = curve_fit(gauss, centers, counts, p0=p0, sigma=np.sqrt(counts) + (counts == 0), maxfev=10000)
    except (RuntimeError, ValueError):
        return None
    errors = np.sqrt(np.diag(cov))
    return float(coeff[1]), float(abs(coeff[2])), float(errors[1]), float(errors[2]), int(len(window))


def rotate_to_proton_frame(px, py, pz, crossing_angle):
    """Momentum components in the frame of the proton beam (the benchmarks' tilt)."""
    c, s = np.cos(crossing_angle), np.sin(crossing_angle)
    return px * c - pz * s, py, pz * c + px * s


def binomial_error(k, n):
    """Standard error of an efficiency k/n (Wald form, enough for the scoreboard band)."""
    if n == 0:
        return 0.0
    p = k / n
    return float(np.sqrt(p * (1 - p) / n))


def sha256_of(path, block=1 << 20):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(block):
            h.update(chunk)
    return h.hexdigest()
