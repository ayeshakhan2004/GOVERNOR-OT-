"""
planner.py
----------
The Planner: takes a snapshot of "what the network looks like right now"
and asks the local model to decide on ONE command to send next.

How it's forced to behave itself:
  - We pass Ollama the exact JSON schema from schema.py as the `format`
    parameter. Ollama then constrains the model's output token-by-token
    so it CANNOT return anything except valid JSON matching that shape.
    This is not "ask nicely and hope" — it's enforced at generation time.
  - We still re-validate the JSON through Pydantic after it comes back,
    because "matches the JSON shape" is not the same as "makes sense"
    (e.g. a write command missing a value would still be valid JSON).

Swap MODEL_NAME to whichever model wins the Week 1 comparison —
nothing else in this file needs to change.
"""

import json
import requests
from schema import OTCommand

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5-coder:14b"  # <-- change this once the model decision is final

SYSTEM_PROMPT = """You are the Planner agent in an industrial security scanning system.
You are given the current state of a simulated OT/Modbus network.
Decide on exactly ONE next command to send, following the required JSON schema.
Only use the target_device and register_address values that appear in the
provided network state — never invent a device or address that wasn't given to you.
Keep "reasoning" to one short sentence.

STRICT RULES ON FIELDS — follow these exactly:
1. If action is "write_register" or "write_coil", the "value" field is
   REQUIRED and MUST be a number. It must match whatever value you mention
   in "reasoning" — never leave it null when writing.
2. If action is "read_register" or "read_coil", the "value" field MUST be null.
3. A "coil" is a simple on/off switch (use read_coil / write_coil, value 0 or 1).
   A "register" holds a numeric value (use read_register / write_register).
   Never use a register action when the goal mentions a coil, and vice versa."""


def run_planner(network_state: dict, goal: str | None = None, timeout: int = 120) -> dict:
    """
    network_state: a dict describing what the Planner can currently see,
    e.g. {"devices": ["PLC-1"], "registers": {"PLC-1": [40001, 40002]}}

    goal: optional plain-English instruction, e.g. "Set register 40001 to 1
    on PLC-1." Without a goal the model defaults to the safest option
    (reading). Give it a goal when you specifically want to test whether
    it can produce a write_register / write_coil / read_coil command.

    Returns a dict with:
      "command"  -> the validated OTCommand
      "metrics"  -> timing + token counts pulled straight from Ollama's
                    own response, so you're not guessing at performance,
                    you're reading numbers Ollama already calculated.

    Raises ValueError if the model's output doesn't pass Pydantic
    validation even after schema enforcement.
    """
    user_content = f"Current network state:\n{json.dumps(network_state)}"
    if goal:
        user_content += f"\n\nGoal: {goal}"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "format": OTCommand.model_json_schema(),  # <-- this is the enforcement step
        "stream": False,
        "options": {"temperature": 0.2},  # low temperature: we want consistent, boring, safe choices
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    body = response.json()
    raw_content = body["message"]["content"]

    # NOTE for reasoning models (e.g. DeepSeek-R1-distill): some versions
    # of Ollama still return a <think>...</think> block before the JSON
    # even with format= set. If you're testing a reasoning model and this
    # line fails to parse, print(raw_content) first and strip everything
    # before the first "{" as a quick fix.
    data = json.loads(raw_content)

    command = OTCommand.model_validate(data)
    ok, reason = command.is_internally_consistent()
    if not ok:
        raise ValueError(f"Model returned an inconsistent command: {reason} -> {command}")

    # Ollama reports these durations in nanoseconds — convert to seconds
    # so they're readable and match how VEXA_IoT reports time (Table V).
    metrics = {
        "total_time_sec": round(body.get("total_duration", 0) / 1e9, 2),
        "llm_reasoning_time_sec": round(body.get("eval_duration", 0) / 1e9, 2),
        "prompt_tokens": body.get("prompt_eval_count", 0),
        "output_tokens": body.get("eval_count", 0),
        "total_tokens": body.get("prompt_eval_count", 0) + body.get("eval_count", 0),
    }

    return {"command": command, "metrics": metrics}


if __name__ == "__main__":
    demo_state = {"devices": ["PLC-1"], "registers": {"PLC-1": [40001, 40002, 40003]}}
    cmd = run_planner(demo_state)
    print(cmd.model_dump_json(indent=2))
