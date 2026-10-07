"""
test_harness.py (v2)
---------------------
Runs the Planner against 10 scenarios, now split so some scenarios push
toward write/coil commands instead of letting the model always default
to a read. Also logs performance numbers (time + tokens) for every run,
the same kind of numbers VEXA_IoT reports in their Table V, so these
results can be compared directly against the baseline paper.

Run for real (needs Ollama running locally with your model pulled):
    python test_harness.py

Run in mock mode (no Ollama needed — just proves the harness logic itself
has no bugs):
    python test_harness.py --mock
"""

import sys
import csv
from schema import OTCommand

# 10 scenarios. The first 5 are open-ended (no goal) — these test whether
# the model behaves sensibly with no explicit instruction. The last 5
# include an explicit goal, each deliberately aimed at a DIFFERENT action
# type, so by the end of this run you've tested all 4 actions at least once.
SCENARIOS = [
    {"state": {"devices": ["PLC-1"], "registers": {"PLC-1": [40001, 40002, 40003]}}, "goal": None},
    {"state": {"devices": ["PLC-1"], "registers": {"PLC-1": [40010]}}, "goal": None},
    {"state": {"devices": ["PLC-2"], "registers": {"PLC-2": [30001, 30002]}}, "goal": None},
    {"state": {"devices": ["PLC-1", "PLC-2"], "registers": {"PLC-1": [40001], "PLC-2": [30005]}}, "goal": None},
    {"state": {"devices": ["PLC-3"], "registers": {"PLC-3": [50001, 50002]}}, "goal": None},

    {"state": {"devices": ["PLC-1"], "registers": {"PLC-1": [40020, 40021]}},
     "goal": "Set register 40020 on PLC-1 to the value 1."},
    {"state": {"devices": ["PLC-2"], "registers": {"PLC-2": [30010]}},
     "goal": "Read the current value of register 30010 on PLC-2."},
    {"state": {"devices": ["PLC-1", "PLC-3"], "registers": {"PLC-1": [40002], "PLC-3": [50010]}},
     "goal": "Write the value 0 to register 50010 on PLC-3."},
    {"state": {"devices": ["PLC-2"], "registers": {"PLC-2": [30020, 30021, 30022]}},
     "goal": "Check the on/off status of coil 30021 on PLC-2."},
    {"state": {"devices": ["PLC-1"], "registers": {"PLC-1": [40099]}},
     "goal": "Turn on coil 40099 on PLC-1."},
]


def mock_planner(scenario: dict, index: int) -> dict:
    """Stand-in for run_planner() when Ollama isn't available."""
    state = scenario["state"]
    device = state["devices"][0]
    address = state["registers"][device][0]
    command = OTCommand(
        action="read_register",
        target_device=device,
        register_address=address,
        value=None,
        reasoning=f"Mock run #{index}.",
    )
    # fake but realistic-shaped metrics, just to test the logging code
    metrics = {
        "total_time_sec": 1.0 + index * 0.1,
        "llm_reasoning_time_sec": 0.8 + index * 0.1,
        "prompt_tokens": 150,
        "output_tokens": 40,
        "total_tokens": 190,
    }
    return {"command": command, "metrics": metrics}


def main():
    use_mock = "--mock" in sys.argv
    if use_mock:
        from_planner = mock_planner
    else:
        from planner import run_planner
        from_planner = lambda scenario, i: run_planner(scenario["state"], goal=scenario["goal"])  # noqa: E731

    results = []
    passed = 0
    actions_seen = set()

    for i, scenario in enumerate(SCENARIOS, start=1):
        try:
            result = from_planner(scenario, i)
            command, metrics = result["command"], result["metrics"]
            ok, reason = command.is_internally_consistent()
            status = "PASS" if ok else "FAIL"
            if ok:
                passed += 1
                actions_seen.add(command.action)

            results.append({
                "run": i,
                "goal": scenario["goal"] or "(none)",
                "status": status,
                "reason": reason,
                "action": command.action,
                "total_time_sec": metrics["total_time_sec"],
                "llm_reasoning_time_sec": metrics["llm_reasoning_time_sec"],
                "prompt_tokens": metrics["prompt_tokens"],
                "output_tokens": metrics["output_tokens"],
                "total_tokens": metrics["total_tokens"],
                "output": command.model_dump_json(),
            })
        except Exception as e:
            results.append({
                "run": i, "goal": scenario["goal"] or "(none)", "status": "ERROR",
                "reason": str(e), "action": "", "total_time_sec": "", "llm_reasoning_time_sec": "",
                "prompt_tokens": "", "output_tokens": "", "total_tokens": "", "output": "",
            })

        print(f"[{results[-1]['status']}] run {i}: {results[-1]['reason']}")

    fieldnames = ["run", "goal", "status", "reason", "action", "total_time_sec",
                  "llm_reasoning_time_sec", "prompt_tokens", "output_tokens",
                  "total_tokens", "output"]
    with open("planner_test_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    valid_rows = [r for r in results if r["status"] == "PASS"]
    avg_time = round(sum(r["total_time_sec"] for r in valid_rows) / len(valid_rows), 2) if valid_rows else 0
    avg_tokens = round(sum(r["total_tokens"] for r in valid_rows) / len(valid_rows), 1) if valid_rows else 0

    print(f"\n{passed}/{len(SCENARIOS)} runs produced a valid, consistent command.")
    print(f"Action types seen: {sorted(actions_seen) if actions_seen else 'none'}")
    print(f"Average total time per command: {avg_time}s")
    print(f"Average tokens per command: {avg_tokens}")
    print("Full results written to planner_test_results.csv")


if __name__ == "__main__":
    main()
