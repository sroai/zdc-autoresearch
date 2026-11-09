#!/usr/bin/env python3
"""Geometric acceptance of the D4 Λ gun per thrown Λ (2026-11-05, user question in Phase 2).

gen_lambda_decay.cxx loops until n_events are *accepted* — Λ decays before the ZDC face (35.8 m along the proton
axis) and n, γ, γ all extrapolate within 4 mrad of the proton axis there — and never prints how many it threw.
This script re-implements its kinematics (θ uniform 0–3 mrad around the proton axis, −25 mrad crossing, exponential
decay length, isotropic Λ → nπ⁰ and π⁰ → γγ) and its cut, and counts. Validated against D4 itself: median decay z of
accepted events 28.2 / 22.8 / 19.4 m here vs 27.8 / 22.8 / 19.0 m in space/perf/shape-R0_stock.json (100/175/275 GeV).
Every D4 efficiency is conditional on this acceptance; multiply by it for the per-thrown-Λ (Λ → nπ⁰ = 100 %) value.

Usage: uv run scripts/413_lambda_gun_acceptance.py   → space/perf/lambda-gun-acceptance.json
"""
import numpy as np
mL, mn, mpi = 1.115683, 0.939565, 0.134977
ctau = 78.9  # mm (Λ cτ = 7.89 cm)
cross = -0.025
zdc_z = 35800.0
rng = np.random.default_rng(7)
def boost(p4, beta):  # p4: (N,4) E,px,py,pz ; beta: (N,3)
    b2 = (beta**2).sum(1); g = 1/np.sqrt(1-b2)
    bp = (beta*p4[:,1:]).sum(1)
    g2 = np.where(b2 > 0, (g-1)/b2, 0)
    E = g*(p4[:,0]+bp)
    p = p4[:,1:] + (g2*bp + g*p4[:,0])[:,None]*beta
    return np.column_stack([E, p])
def iso(N, m_parent, m1, m2):
    E1 = (m_parent**2 + m1**2 - m2**2)/(2*m_parent); pm = np.sqrt(E1**2 - m1**2)
    c = rng.uniform(-1,1,N); s = np.sqrt(1-c**2); ph = rng.uniform(-np.pi,np.pi,N)
    d = np.column_stack([s*np.cos(ph), s*np.sin(ph), c])*pm
    return np.column_stack([np.full(N,E1), d]), np.column_stack([np.full(N, m_parent-E1), -d])
def rotY(v, a):
    x, y, z = v[:,0], v[:,1], v[:,2]
    return np.column_stack([x*np.cos(a)+z*np.sin(a), y, -x*np.sin(a)+z*np.cos(a)])
pb = np.array([np.sin(cross), 0, np.cos(cross)])
def accept(P, N=2_000_000, thmax=0.003):
    th = rng.uniform(0, thmax, N); ph = rng.uniform(0, 2*np.pi, N)
    pv = np.column_stack([P*np.cos(ph)*np.sin(th), P*np.sin(ph)*np.sin(th), np.full(N, P*np.cos(th))])
    pv = rotY(pv, cross)
    EL = np.sqrt(P**2+mL**2); beta = pv/EL
    n_r, pi_r = iso(N, mL, mn, mpi)
    n_l = boost(n_r, beta); pi_l = boost(pi_r, beta)
    L = rng.exponential(P/mL*ctau, N)
    dpos = pv/np.linalg.norm(pv,axis=1)[:,None]*L[:,None]
    g1_r, g2_r = iso(N, mpi, 0, 0)
    bpi = pi_l[:,1:]/pi_l[:,[0]]
    g1 = boost(g1_r, bpi); g2 = boost(g2_r, bpi)
    def ang(p3):
        t = (zdc_z - dpos@pb)/(p3@pb)
        x = dpos + p3*t[:,None]
        return np.arccos(np.clip(x@pb/np.linalg.norm(x,axis=1), -1, 1))
    before = dpos@pb < zdc_z
    a_n, a1, a2 = ang(n_l[:,1:]), ang(g1[:,1:]), ang(g2[:,1:])
    ok = (a_n < .004) & (a1 < .004) & (a2 < .004) & before
    return before.mean(), ((a_n<.004)&before).mean(), ok.mean(), np.median(dpos[ok,2])/1000
print("p GeV | decays before ZDC | n inside 4 mrad | n+γ+γ inside 4 mrad (the D4 cut)")
import json, sys
out = {}
for P in (100,125,150,175,200,225,250,275):
    b, n, a, zm = accept(P); out[P] = {"decays_before_zdc": b, "n_inside_4mrad": n, "all3_inside_4mrad": a, "median_decay_z_m_accepted": zm}; print(f"{P} | {b:.3f} | {n:.3f} | {a:.4f} | {zm:.1f} m")
json.dump(out, open(sys.path[0] + "/../space/perf/lambda-gun-acceptance.json", "w"), indent=1)
