"""The Λ → n γ γ chain of LambdaReconstruction, re-implemented in numpy for offline studies.

Shared by scripts/414_lambda_ceiling_variants.py (the chain on ideal and smeared inputs) and
scripts/415_lambda_chain_offline.py (the chain on each row's real clusters), so both apply the
same pairing code. Positions are in the proton frame (lab rotated by −globalToProtonRotation),
in mm; energies in GeV.

Pairings:
  stock        — LambdaReconstruction.cc at the pin: π⁰ window and Λ window on IP-pointing
                 momenta, then the IDOLA vertex iteration and the Λ window again.
  vertex       — IDOLA first, then both windows on momenta pointing from that vertex. The
                 iteration runs away transversely for decays far from the IP (finding F9).
  vertex_fixed — the stable vertex (B9d): the Λ direction from the momentum-weighted centroid
                 of the impact points, the decay depth by bisection on the γγ opening angle.
"""
import numpy as np

M_PI0, M_L, M_N = 0.1349768, 1.115683, 0.93956542
ROT = -0.025                       # globalToProtonRotation (rad)
PI0_WIN, L_WIN, ITER, ZMAX = 0.1, 0.1, 10, 35800.0   # LambdaReconstruction defaults at the pin
PAIRINGS = ("stock", "vertex", "vertex_fixed")


def to_proton(x, y, z):
    a = -ROT
    return x * np.cos(a) + z * np.sin(a), y, -x * np.sin(a) + z * np.cos(a)


def to_lab(x, y, z):
    a = ROT
    return x * np.cos(a) + z * np.sin(a), y, -x * np.sin(a) + z * np.cos(a)


def four(E, x, m=0.0):
    p = np.sqrt(max(E * E - m * m, 0.0))
    return np.array([E, *(p * x / np.linalg.norm(x))])


def mass(*vs):
    s = np.sum(vs, axis=0)
    m2 = s[0] ** 2 - s[1] ** 2 - s[2] ** 2 - s[3] ** 2
    return np.sqrt(m2) if m2 > 0 else -1.0


def idola(En, E1, E2, xn, x1, x2):
    """As LambdaReconstruction: proton-frame positions in, (vertex, unit vectors) out."""
    pn = np.sqrt(max(En * En - M_N * M_N, 0.0))
    vtx = np.zeros(3)
    f, df = 0.0, 0.5
    arg = M_PI0 / (2 * np.sqrt(E1 * E2))
    th_exp = 2 * np.arcsin(min(arg, 1.0))
    for _ in range(ITER):
        un, u1, u2 = ((v - vtx) / np.linalg.norm(v - vtx) for v in (xn, x1, x2))
        lam = np.array([En + E1 + E2, *(pn * un + E1 * u1 + E2 * u2)])
        th = np.arccos(np.clip(np.dot(u1, u2), -1, 1))
        if th > th_exp:
            f -= df
        elif th < th_exp:
            f += df
        vtx = lam[1:] * (f * ZMAX / lam[3])
        df /= 2.0
    un, u1, u2 = ((v - vtx) / np.linalg.norm(v - vtx) for v in (xn, x1, x2))
    return vtx, un, u1, u2


def vertex_fixed(En, E1, E2, xn, x1, x2):
    """Stable vertex: Λ slope from the momentum-weighted impact centroid; bisection on the depth along it."""
    pn = np.sqrt(max(En * En - M_N * M_N, 0.0))
    t = (pn * xn[:2] + E1 * x1[:2] + E2 * x2[:2]) / (pn * xn[2] + E1 * x1[2] + E2 * x2[2])
    th_exp = 2 * np.arcsin(min(M_PI0 / (2 * np.sqrt(max(E1 * E2, 1e-12))), 1.0))
    lo, hi = 0.0, ZMAX
    for _ in range(20):
        z = 0.5 * (lo + hi)
        v = np.array([t[0] * z, t[1] * z, z])
        u1, u2 = ((x - v) / np.linalg.norm(x - v) for x in (x1, x2))
        if np.arccos(np.clip(np.dot(u1, u2), -1, 1)) > th_exp:
            hi = z
        else:
            lo = z
    v = np.array([t[0] * lo, t[1] * lo, lo])
    un, u1, u2 = ((x - v) / np.linalg.norm(x - v) for x in (xn, x1, x2))
    return v, un, u1, u2


def chain(E, X, pairing, n_direction=None):
    """E: energies {n, g1, g2} (the neutron's total energy); X: proton-frame positions.

    n_direction: the point the neutron's momentum aims at in the stock preselection, when it
    differs from X["n"]. In EICrecon the neutron neutral's momentum points at its leader cluster
    while IDOLA reads the position of its first linked cluster (getClusters(0)), which with
    associateAllClustersToNeutron is cluster 0 of the event, often another particle's.
    Returns the final Λ mass, or None when the chain rejects the triplet.
    """
    if pairing == "stock":
        xn_pre = X["n"] if n_direction is None else n_direction
        g1, g2, n = four(E["g1"], X["g1"]), four(E["g2"], X["g2"]), four(E["n"], xn_pre, M_N)
        if abs(mass(g1, g2) - M_PI0) > PI0_WIN * M_PI0 or abs(mass(n, g1, g2) - M_L) > L_WIN * M_L:
            return None
        vtx, un, u1, u2 = idola(E["n"], E["g1"], E["g2"], X["n"], X["g1"], X["g2"])
    else:
        fit = idola if pairing == "vertex" else vertex_fixed
        if min(E["g1"], E["g2"]) <= 0:
            return None
        vtx, un, u1, u2 = fit(E["n"], E["g1"], E["g2"], X["n"], X["g1"], X["g2"])
        g1, g2 = four(E["g1"], u1), four(E["g2"], u2)
        if abs(mass(g1, g2) - M_PI0) > PI0_WIN * M_PI0:
            return None
    m = mass(four(E["n"], un, M_N), four(E["g1"], u1), four(E["g2"], u2))
    return m if abs(m - M_L) <= L_WIN * M_L else None
