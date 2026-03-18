# autoresearch — nanogpt default task

Use this file only when no orchestrator-specific worker brief was provided.

Combine this file with `instructions/base_program.md`.

Assume you are already in the checkout or worktree you should use.

## Default Loop

Loop indefinitely once setup is complete:

1. Query `autoresearch summary` and read past `exp.md` files via `autoresearch read <commit>` to understand what has been tried.
2. Check the current git state.
3. Edit `train.py` with one concrete idea. Write `exp.md` with hypothesis and reasoning. Think deeply and mathematically.
4. Commit the runnable snapshot. Save the hash as the run commit.
5. Run: `python3 run.py train > run.log 2>&1`.
6. Check: `grep "^val_bpb:\|^peak_vram_mb:" run.log`.
7. If grep is empty, inspect `tail -n 50 run.log`. Fix obvious mistakes and retry a small number of times. If the idea is broken, write the failure into `exp.md`, commit the results note, and record with `--status crash` or `--status timeout`.
8. Append Results to `exp.md`, including the keep/discard decision. Commit that update. Save the hash as the result commit.
9. Record once: `autoresearch record <run-commit> --result-commit <result-commit> --status success --decision keep|discard --description "..." --metric val_bpb=<...> --metric peak_vram_mb=<...> ...`.
10. Keep the result commit only if `val_bpb` improved. If equal, worse, or crashed, revert to the previous good result commit.

Each run should finish in about 5 minutes plus startup and evaluation overhead. If a run exceeds 10 minutes, kill it and treat it as a failure.

Once the loop starts, do not stop to ask the human whether to continue. Keep iterating until interrupted.
