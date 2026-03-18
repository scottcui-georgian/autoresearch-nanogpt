# autoresearch — nanogpt base worker program

This file is the static worker contract.

Assume you have already been launched in the correct checkout or worktree. Do not create
new worktrees yourself. If an orchestrator assigned you a direct worker instruction, follow that instruction
in addition to this file.

## Read First

Read these files for context:

- `workspace/prepare.py` — fixed constants, tokenizer, dataloader, evaluation. Read-only.
- `workspace/train.py` — the only code file you modify.
- `workspace/exp.md` — create or update for each experiment.
- `.runner/modal/pyproject.toml` from the repo root — remote runtime manifest. Read-only context.

## Setup

1. Confirm you are working in the assigned checkout or worktree.
2. Read the in-scope files above.
3. Assume the Modal cache already exists. Cache preparation is not part of the worker role.
4. If a training run fails because the cache is missing or invalid, stop and report the issue.
5. Confirm the current `HEAD`, branch, and assigned `agent_id` before starting experiments.

## Execution Contract

Each experiment runs on a single Modal `L40S` GPU for a fixed 5-minute training budget.

```bash
python3 run.py train > run.log 2>&1
```

This is the only experiment execution command.

## Scratch Work

You may use local Python for quick calculations or small hypothesis checks:

```bash
python3 - <<'PY'
import math
print(math.sqrt(2))
PY
```

## Allowed Changes

- You can ONLY modify `train.py`.
- You may create or update `exp.md` for each experiment.
- Everything inside `train.py` is fair game: architecture, optimizer, hyperparameters, batch size, model size, training loop details.

## Forbidden Changes

- Do not modify `prepare.py`, `run.py`, or anything under `.runner/`.
- Do not run `python3 run.py prepare`.
- Do not install packages.
- Do not modify the evaluation harness in `prepare.py`. `evaluate_bpb` is the ground-truth metric.
- Do not create or manage worktrees unless the human explicitly asks. That is the orchestrator's job.

## Goal

The worker's goal is defined by the instruction it was launched with.

- In orchestrated mode, follow the orchestrator's stated objective, loop, and stopping condition.
- In single-agent mode, follow `instructions/default_task.md`.

For this task, `val_bpb` is the primary evaluation metric unless the instruction explicitly says otherwise. Lower is better.

The first run from any fresh starting point should normally be the unmodified baseline for that starting commit unless your instruction says otherwise.

VRAM is a soft constraint: some increase is acceptable for a real gain, but avoid wasteful blowups.

Prefer simpler changes when the metric impact is similar. Deleting complexity for equal or better results is a win.

## Output Format

Each run ends with a summary block in `run.log`:

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

Useful quick check:

```bash
grep "^val_bpb:\|^peak_vram_mb:" run.log
```

## exp.md

Write `exp.md` before the run commit. Include:

- **Hypothesis**: what you expect and why
- **Reasoning**: mathematical derivation, parameter calculations, or conceptual argument
- **References**: papers/sources and what you took from them, N/A if not applicable
- **Changes**: which file and what changed
- **Base**: parent commit hash and baseline val_bpb

After the run, append a **Results** section with val_bpb, peak_vram_mb, status
(`keep`, `discard`, `crash`, or `timeout`), and brief analysis. Then make a second
commit with the completed results note.

## Experiment Recording

Record each experiment once, after the results commit exists. Each DB row stores both
the run commit and the later results commit.

```bash
autoresearch record <run-commit> \
  --result-commit <result-commit> \
  --status success \
  --decision keep|discard \
  --description "one-line summary" \
  --agent-id <agent-id> \
  --metric val_bpb=<value> \
  --metric peak_vram_mb=<value>
```

For NanoGPT, extract the numeric fields from the final summary block in `run.log` and
pass them explicitly as repeated `--metric name=value` flags. Include all numeric
summary fields, not just `val_bpb`. You can track and record more metrics if you want.

Browse experiments with:

```bash
autoresearch summary
autoresearch read <commit-hash>
```
