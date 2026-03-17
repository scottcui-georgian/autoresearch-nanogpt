# autoresearch — nanogpt

This repo is a self-contained task for autonomous training experiments.

## Setup

To set up a new experiment, work with the user to:

1. Agree on a run tag based on today's date, such as `mar12`. The branch `autoresearch/<tag>` must not already exist.
2. Start in an isolated worktree. If the user has not already created one, from the repo root run:
   ```bash
   git worktree add ../worktrees/<tag> -b autoresearch/<tag>
   ```
   Then work inside `../worktrees/<tag>/`. If you are already in a worktree, continue there.
3. Read the in-scope files for full context:
  - `prepare.py` — fixed constants, tokenizer, dataloader, evaluation. Do not modify.
  - `train.py` — the only code file you modify.
  - `exp.md` — create for each experiment with hypothesis and reasoning.
  - `run.py` — task runner. Do not modify.
  - `task.toml` — task configuration. Do not modify.
  - `pyproject.toml` — available runtime dependencies. Do not modify.
4. Verify the Modal cache exists. If data has not been prepared yet, run: `uv run --only-group dev python run.py prepare`.
5. Confirm setup and start the loop.

Working in a dedicated worktree keeps your changes isolated from other agents and avoids git conflicts when running parallel experiments.

## Execution contract

Each experiment runs on a single Modal `L40S` GPU for a fixed 5-minute training budget.

- `uv run --only-group dev python run.py train > run.log 2>&1`

This is the only experiment execution command. Always redirect to `run.log` so the result can be parsed after the run.

## Scratch work

You may use local Python for quick calculations, small hypothesis checks, or one-off scripts while reasoning.

- Use: `uv run --only-group dev python`
- Example: `uv run --only-group dev python - <<'PY'`
- The project's main dependencies are CUDA-pinned for remote execution. Use `--only-group dev` to get a local Python with numpy and basic utilities.

## Allowed changes

- You may modify `train.py` only (and create `exp.md` per experiment).
- Everything inside `train.py` is fair game: architecture, optimizer, hyperparameters, batch size, model size, training loop details.

## Forbidden changes

- Do not modify `prepare.py`.
- Do not modify `run.py`.
- Do not install packages or edit `pyproject.toml`.
- Do not modify `task.toml`.
- Do not modify the evaluation harness in `prepare.py`. `evaluate_bpb` is the ground-truth metric.

## Goal

Minimize `val_bpb`. Lower is better.

The first run must always be the unmodified baseline through `uv run --only-group dev python run.py train > run.log 2>&1`.

VRAM is a soft constraint: some increase is acceptable for a real gain, but avoid wasteful blowups.

Prefer simpler changes when the metric impact is similar. Deleting complexity for equal or better results is a win.

## Output format

Each run ends with a summary block like:

```text
---
val_bpb:          1.121406
training_seconds: 300.2
total_seconds:    377.0
peak_vram_mb:     22805.5
mfu_percent:      31.37
total_tokens_M:   147.8
num_steps:        282
num_params_M:     50.3
depth:            8
```

Use:

```bash
grep "^val_bpb:\|^peak_vram_mb:" run.log
```

to extract the key result lines from a finished run.

## exp.md

Create `exp.md` in this directory for each experiment. Write it before committing. Include:

- **Hypothesis**: what you expect and why
- **Reasoning**: mathematical derivation, parameter calculations, or conceptual argument
- **References**: papers and what you took from them
- **Changes**: which file and what changed
- **Base**: parent commit hash and baseline val_bpb

After the run, append a **Results** section with val_bpb, peak_vram_mb, status (keep/discard/crash), and brief analysis. Commit the update.

## Experiment recording

Record every experiment in the DB:

```bash
autoresearch record <commit> --status pending --description "one-line summary"  # before run
uv run --only-group dev python run.py train > run.log 2>&1
autoresearch record <commit> --status success --run-log run.log  # or --status crash on failure
```

To browse others' experiments and avoid duplicate work:

```bash
autoresearch summary
autoresearch read <commit-hash>
```

## Loop

Loop indefinitely once setup is complete:

1. Query `autoresearch summary` and read others' exp.md via `autoresearch read <commit>` to understand what has been tried.
2. Check the current git state.
3. Edit `train.py` with one concrete idea. Write `exp.md` with hypothesis and reasoning. Think deeply and mathematically.
4. Commit the change.
5. Record: `autoresearch record <commit> --status pending --description "..."`.
6. Run `uv run --only-group dev python run.py train > run.log 2>&1`.
7. Read `grep "^val_bpb:\|^peak_vram_mb:" run.log`.
8. If grep is empty, inspect `tail -n 50 run.log`. Fix obvious mistakes and retry a small number of times. If the idea is broken, record with `--status crash` and move on.
9. Update DB: `autoresearch record <commit> --status success --run-log run.log` (or `--status crash`). Append Results to exp.md and amend/follow-up the commit.
10. Keep the commit only if `val_bpb` improved. If equal, worse, or crashed, revert to the previous good commit.

Each run should finish in about 5 minutes plus startup and evaluation overhead. If a run exceeds 10 minutes, kill it and treat it as a failure.

Once the loop starts, do not stop to ask the human whether to continue. Keep iterating until interrupted.
