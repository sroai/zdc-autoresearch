`pgrep -f` / `pkill -f` with a pattern taken from a command line also matches the shell that runs it.

- What bit: Phase 5 a wait loop `until ! pgrep -f "<script> <args>"` never ended (it matched itself); Phase 6
  (2026-11-09T04:56Z) `pkill -f "477_crystal_scope.py MSF6_Y9 --dataset D6s_9x275"; <more commands>` killed its own
  tool-call shell (exit 144): the target died, the commands after it never ran.
- Why: the tool's shell carries the whole command text in its own argv, so the pattern is in it too.
- Rule: stop a background job by the PID from `ps -eo pid,args | grep "[4]77_..."` (the bracket keeps grep and the shell
  out of the match) and `kill <pid>`, in a call of its own; wait on a job through the harness's task notification or a
  file it writes, never through `pgrep -f` on its own arguments.
