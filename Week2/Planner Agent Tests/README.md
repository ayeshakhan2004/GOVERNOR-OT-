# Planner Agent — GOVERNOR-OT (AEGIS-Sec)

This is the Planner component of the GOVERNOR-OT multi-agent OT security
platform. The Planner takes a snapshot of a simulated Modbus/OT network and
produces exactly one structured command, using a local model (no commercial
API) constrained to a strict JSON schema so it cannot return malformed or
unparseable output.

## Model used

Qwen-14B , served locally via Ollama.

## Files

| File | What it does |
|---|---|
| `schema.py` | Defines the exact shape of a valid command (`OTCommand`). Every other file imports this — it's the single source of truth shared with the Executor and Safety-Critic. |
| `planner.py` | Calls the local model through Ollama, enforces the schema at generation time, and returns a validated command plus performance metrics (time, token usage). |
| `test_harness.py` | Runs the Planner against 10 scenarios (5 open-ended, 5 with an explicit goal covering all 4 Modbus action types) and logs pass/fail plus performance data to a CSV. |
| `planner_test_results_final.csv` | Final validation run: 10/10 pass, all 4 action types produced correctly. |
| `requirements.txt` | Python dependencies. |

## How to run it

1. Install [Ollama](https://ollama.com) and start it (`ollama serve`)
2. Pull the model: `ollama pull deepseek-r1:14b` (adjust tag to match your local setup)
3. `pip install -r requirements.txt`
4. `python test_harness.py`

Run `python test_harness.py --mock` to test the harness logic without
needing Ollama running (useful for quick sanity checks).

## Result summary

First run: 7/10 passed. All 3 failures were write-type commands where the
model's reasoning stated the correct value but left the `value` field null.

Fix: added 3 explicit field-consistency rules to the system prompt in
`planner.py` (writes require a value, reads require null, coil vs. register
must match the goal).

After the fix: 10/10 passed, all 4 action types (`read_register`,
`write_register`, `read_coil`, `write_coil`) correctly produced. Average
~4.8s and ~359 tokens per command.
