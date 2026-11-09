`-Pjana:nthreads=1` aborts eicrecon at the pin; the JANA2 key is `-Pnthreads=1`.

- What bit: with `jana:parameter_strictness=2` (EICrecon's default), an unused parameter throws at init: `Parameter 'jana:nthreads' appears to be unused. Possible typo?`. The loop and setup files write `-Pjana:nthreads=1`; read it as `-Pnthreads=1`.
- `jana:nevents`, `jana:timeout`, `jana:warmup_timeout` do carry the `jana:` prefix.
- Rule: `scripts/120_reconstruct.py` and every gate script pass `-Pnthreads=<n>`. Memory: [[eicrecon-jana-nthreads-key]].
