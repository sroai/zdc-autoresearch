# Benchmark plot scripts, with EICrecon main's collection names

Copies of `submodules/detector_benchmarks/benchmarks/zdc_{pi0,lambda,photon,neutron}/analysis/*`
(at the pinned benchmark commit) with three renames, because the benchmarks
still use the pre-2026-05-29 names and exit quietly when a collection is missing:

| benchmark name | EICrecon main |
|---|---|
| `ReconstructedFarForwardZDCLambdas` | `ReconstructedLambdas` |
| `ReconstructedFarForwardZDCLambdaDecayProductsCM` | `ReconstructedLambdaDecayProductsCM` |
| `ReconstructedFarForwardZDCNeutrals` | `ReconstructedHcalFarForwardZDCNeutrals` |

`scripts/401_benchmark_plots.sh` runs these copies; the submodule stays frozen.
The rename itself is a finding for an upstream detector_benchmarks PR
(space/reports/FINDINGS.md). Everything else is the benchmark authors' code.

Two further edits, both about reading, none about what is plotted:

- `ur.concatenate` loads only `HcalFarForwardZDCClusters*`, `MCParticles*`,
  `ReconstructedLambda*` and `ReconstructedHcalFarForwardZDCNeutrals*` (`filter_name`): our gun files are full-detector reconstructions with `.*` output
  (about 9000 branches; reading all of them took more than 30 CPU minutes and 6.5 GB for
  the π⁰ script alone), while the benchmark's own files hold the ZDC collections.
- the index loop skips index files that do not exist (`os.path.exists`): one file per
  momentum and seed here, five index files in the benchmark.
