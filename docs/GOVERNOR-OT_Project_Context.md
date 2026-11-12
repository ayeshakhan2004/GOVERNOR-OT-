# GOVERNOR-OT: Full Project Context

Last updated: 2026-11-12. Maintained by Ayesha Khan.

## 0. What this file is and how to use it

This is the single source of context for the GOVERNOR-OT final year project. It
exists so that any tool or person who opens the project folder, including a fresh
Claude Code session that cannot see our claude.ai project or chat history, starts
with the same understanding we already built up over several planning sessions.

If you are Claude Code reading this: treat everything here as settled project
context, not as instructions you can override. Where a decision is still open, it
says so plainly in Section 11. Do not invent facts, citations, or numbers. The
rules for how to help are in Section 15, and they are not optional.

Keep this file updated as decisions get made. When something in Section 11 (open
decisions) gets locked, move it into the relevant section and delete it from the
open list.

## 1. Project identity

- Name: GOVERNOR-OT. It was previously called AEGIS-Sec. The rename is recent, so
  some older documents still say AEGIS-Sec (the model selection document is one
  of them). Same project, treat the names as interchangeable in older files.
- Full title: "Rule-Based Command Validation for LLM-Driven Security Testing in
  Industrial Networks."
- Type: Final Year Design Project (FYDP) at Iqra University, Department of
  Computer Science.
- Team: Ayesha Khan, Maryum Mughal, Amaan Khan, Muhammad Damil Khan.
- Supervisor: Muhammad Asif Sheikh.
- Industrial advisor: Umair Ali, National Foods Ltd.
- Ownership of work: Ayesha and Damil own the core technical pipeline, which is
  the Safety-Critic, the Planner, and the Executor. Maryum and Amaan are given
  only low-risk, non-critical tasks that cannot break the core pipeline. More on
  this in Section 12.
- Intent to publish: a paper is planned after the FYP finishes. This is why
  citation accuracy is treated as a hard rule, not a nicety.

## 2. The contribution, stated carefully

One sentence: GOVERNOR-OT adds a deterministic, non-LLM, rule-based safety gate
that checks every command an autonomous pentest agent proposes, before that
command is allowed to run, in a simulated industrial (Modbus) setting.

The longer version. Autonomous LLM pentest agents already exist and work. What
none of them do is put a hard, rule-based check between the model's proposed
command and the real action, specifically in an operational technology setting.
GOVERNOR-OT is that missing layer. The agent's LLM proposes a command. A separate
piece of plain Python, driven by a fixed rule set and not by another model,
either approves it or blocks it with a specific reason. Only approved commands
reach the simulated PLC.

The contrast that defines the whole project, in one line: the baseline system's
LLM writes a report about what it did. Ours is stopped by a rule before it can
touch the PLC at all.

## 3. The baseline, and exactly how we relate to it

- Baseline paper: VEXAIoT, "Autonomous IoT Vulnerability EXploitation using AI
  Agents." Swinea, Aryal, Praharaj, Gupta. arXiv:2607.09653v1, July 2026.
- What it is: a two-agent framework that reaches 95.0% exploitation success
  across 260 trials on IoTGoat and Metasploitable2. It runs on the paid ChatGPT
  5.1 API. It has no pre-execution safety check of any kind.
- How we connect: VEXAIoT's own paper names, as future work, "stronger command
  validation, safety controls." We build exactly that, and we move it into an
  industrial Modbus setting they never tested. So we are extending their stated
  future work, not competing with their result.

How we must and must not compare against them. This matters because getting it
wrong is the single easiest way for a committee member to take the project apart.

- Do not call it an apples-to-apples benchmark. The hardware is different, the
  environment is different, and the attack set is different.
- The deeper problem is that the metric is close to opposite. VEXAIoT's Tables
  III to V measure attack success rate. Our whole purpose is to block unsafe
  commands. When our Critic correctly blocks a dangerous command, that is a win
  for us but reads as a failed attack in their framing. The two numbers cannot
  sit in the same table and be called comparable.
- What we actually do instead: evaluate the Critic on its own terms. Build a
  labeled set of commands for one scenario, some safe and some unsafe-but-valid,
  and report how many unsafe ones it correctly blocks (catch rate) and how many
  safe ones it wrongly blocks (false-positive rate). Report cost and latency
  against VEXAIoT separately, as context, never as a head-to-head score. The
  honest framing is "we measured a safety property they did not," and that
  framing is defensible.

## 4. Three traps in how the project was originally framed

The original proposal framed the Safety-Critic as the fix for VEXAIoT's 11 of 200
execution failures. That framing does not survive scrutiny, because those 11
failures were 5 model refusals, 5 persistent syntax errors, and 1 hallucination,
and a pre-execution command check cannot fix a model that refused to produce a
command at all. The correct framing maps the three failure modes onto three
different parts of our system, and only one of them is the Safety-Critic:

- Refusals are handled by the choice of a local open-weight model, not by the
  Critic. Our selected model holds refusals to 3.3%, which is competitive with
  the commercial baseline and free.
- Syntax errors are handled by schema-constrained structured output, not by the
  Critic. Our 99.3% parse rate is the evidence. Be careful here: that is the
  schema level. Whether the final shell or Modbus call is well formed is a
  further step, so do not overclaim that structured output removes all malformed
  output.
- The hallucination case (a wrong Modbus port) is the only one the Safety-Critic
  touches, and only if it has a rule that knows the right answer.

So the Safety-Critic's real job, which the original proposal never stated plainly,
is to block commands that are valid and would run fine but are unsafe. The
textbook example is a Modbus write of a damaging value to a protected register.
VEXAIoT never measured that, because they only measured whether attacks
succeeded. That is why we are measuring something new, not beating their table.

## 5. Architecture

Three core components in a line, with one feedback loop:

Planner, a local LLM (qwen2.5-coder:14b via Ollama), proposes one command.
The AST Safety-Critic, pure Python using the ast module, rule-based and not
another AI model, validates it against a fixed rule set.
The Executor runs an approved command in a Docker and PyModbus sandbox.

The one loop: if the Critic blocks a command, it goes back to the Planner with
the specific violated rule attached, so the model gets another try with a real
reason. Nothing else in the system loops.

A live React dashboard shows approved and blocked commands in real time. It never
queries anything. It only renders whatever is pushed to it over a WebSocket.

The system is organised into five layers: presentation and monitoring,
multi-agent orchestration, execution, the testbed and target scenarios, and the
underlying platform and operations infrastructure.

## 6. The real data flow, boundary by boundary

This is the part no box-and-arrow diagram shows: what data actually exists, in
what shape, at each handover.

- Planner to schema: Ollama returns raw JSON text constrained to the Pydantic
  shape. The code calls something like Command.model_validate_json() on it. If any
  field is wrong, this throws immediately, before anything else runs.
- Schema to Safety-Critic: a validated Command object, including its code-like
  expression field, is passed in. The Critic calls ast.parse() on that expression
  string specifically, producing a tree it walks with ast.walk().
- Safety-Critic to Executor: the same Command object, unchanged, plus a boolean
  verdict. The Executor branches on command.action with a plain if or match,
  calling either a PyModbus method such as client.write_register(address, value),
  or a subprocess running the matching command-line tool, depending on the action.
- Executor to logbook: the original command, the verdict, and whatever came back
  from the real call get serialized into one row. Because the schema was clean
  from the start, nothing has to be reshaped to store it.
- Logbook to dashboard: the same row, the instant it is written, is pushed over
  the WebSocket as JSON.

The key property: the same object, unchanged, passes through every stage after it
is first created. Nothing downstream rebuilds or reinterprets it. That is the
entire practical payoff of defining the schema strictly, once, at the start.

## 7. The schema (current focus of work)

The schema is one Pydantic model called Command, in one file. Every other
component imports it. The Planner produces one, the Critic reads one, the Executor
reads one, the logbook stores one. The shape has to be settled before anything
else can be written against it, which is why it comes first.

A proposed v1, assuming the first scenario is a Modbus register read and write
against the PyModbus simulator. This assumption is not yet confirmed (see Section
11). The field decisions matter more than the exact code, so they are explained
below it.

```python
from enum import Enum
from typing import Optional
from pydantic import BaseModel, model_validator

class Action(str, Enum):
    modbus_read = "modbus_read"
    modbus_write = "modbus_write"
    nmap_scan = "nmap_scan"

class Command(BaseModel):
    action: Action                     # fixed choices, never free text
    target_ip: str
    port: int = 502                    # default, so the model need not recall it
    register: Optional[int] = None     # which Modbus register
    value: Optional[int] = None        # only meaningful for a write
    expression: str                    # the single code-like call the AST step parses
    reasoning: Optional[str] = None    # for the human reading logs, never trusted

    @model_validator(mode="after")
    def write_needs_value(self):
        if self.action == Action.modbus_write and self.value is None:
            raise ValueError("modbus_write requires a value")
        return self
```

Field decisions:

- action is a fixed enum, not text, because a free-text action reopens exactly the
  guesswork the schema exists to remove.
- port defaults to 502, so the Planner's weak recall of that fact stops mattering.
  This ties directly to the model selection finding that the chosen model often
  omits the port rather than guessing it.
- value is the one real design decision the schema deep-dive warns not to make by
  accident. It is optional at the schema level, and the validator makes it
  required only when the action is a write. That decision is written down on
  purpose, not left to surface later as a confusing error.
- reasoning is optional and for a human reading logs. The Critic must never base a
  safety decision on it.
- expression is the field that makes the AST methodology real. It holds a single
  code-like call, for example modbus_write(register=40001, value=9999). The Critic
  runs ast.parse() on that string and walks the tree to read the function name and
  its arguments.

The distinction that must never blur, because a reviewer will find it if it does:
ast.parse() succeeding proves only that the expression is a syntactically valid
call with arguments. It says nothing about whether writing 9999 to register 40001
is safe. That judgment is a separate step where the Critic takes the function name
and arguments the AST gave it and checks them against the rules, for example
"register 40001 is protected, block any write to it" or "value must be within this
range." Syntactically well-formed is the schema and the AST. Actually safe is the
rule set. Keep those two apart in code, in comments, and in the writeup.

One extra safety property worth building in because it is nearly free: the Critic
can confirm the expression agrees with the structured fields. If action says
modbus_write but the expression parses to modbus_read, or the registers disagree,
block it. That catches a class of model inconsistency for almost no code.

Build order for the schema itself: finish the field list on paper first, write the
model by hand, test it against hand-made valid and invalid instances, test it
against the written safe and unsafe cases for the one scenario, generate the JSON
schema and read it before handing it to Ollama, and only then move to the Planner.

## 8. Model selection (settled)

Selected model: qwen2.5-coder:14b, running locally via Ollama. 14.7B parameters,
Apache 2.0, Qwen2.5-Coder Technical Report arXiv:2409.12186.

How it was chosen: six candidate models were run under identical
schema-constrained conditions, 15 prompts each run 10 times, 900 calls total. The
selected model had the lowest refusal rate with automated detection applied
(3.3%), zero soft-refusals, a 99.3% parse rate, and the fastest median latency of
any 14B-class model (6.85s). Its most important behaviour for our architecture is
that when it is unsure of a fact it leaves the field blank rather than inventing a
plausible wrong value. A blank field fails schema validation cleanly and goes back
through the correction loop. A confident wrong value passes schema validation and
then needs a semantic rule to catch it. That habit is the real reason to pick it,
and it should lead the justification.

Other results worth keeping in mind:

- qwen3-coder:30b is the runner-up and the recommended fallback. Strong on every
  axis but 20% refusal, concentrated on specific attack categories, and about
  double the VRAM.
- Foundation-Sec-8B-Reasoning, a security-domain model from Cisco, had the best
  factual accuracy on the Modbus port (8 of 10) but the highest refusal rate of
  all six (40.7%). This is a genuine negative result worth reporting: security
  domain pretraining and willingness to generate offensive commands are not the
  same property.
- deepseek-r1:14b and llama3.1:8b were eliminated for confident or random
  hallucination of the Modbus port.

A fourth failure mode we discovered and should claim as a small contribution:
unbounded or runaway generation. One qwen3:14b call ran for over five hours in a
repetition loop before failing. VEXAIoT's failure taxonomy has three categories
(refusal, syntax error, hallucination). We add a fourth, and we recommend any
Executor on this architecture enforce a hard timeout and token cap on every model
call by default.

## 9. Repository structure

This is the layout to build in the folder. Each box from the architecture diagram
is one Python file.

```
governor-ot/
  requirements.txt
  config/
    rules.yaml            # the Safety-Critic rules, as editable data, not code
  src/
    schema.py             # the Command model. Build this first.
    planner.py            # asks Ollama for a command, returns a Command object
    safety_critic.py      # ast.parse plus rule checks, approve or block with reason
    executor.py           # runs an approved command: PyModbus or a shell tool
    logbook.py            # writes one row: command plus verdict plus result
    pipeline.py           # wires the four together, holds the correction loop
    server.py             # FastAPI and WebSocket, pushes each logbook row out
  dashboard/              # the React app, safe work for Maryum or Amaan
  testbed/
    docker-compose.yml    # the simulated Modbus PLC, safe work for the other two
    modbus_server.py
  tests/
    test_schema.py        # hand-made valid and invalid commands
    test_safety_critic.py # the labeled safe and unsafe cases, the real experiment
  data/
    eval_cases.jsonl      # the labeled command set the Critic is graded on
```

pipeline.py is the conductor. It asks planner.py for a command, hands it to
safety_critic.py, and if approved passes the same object to executor.py, then
writes everything to logbook.py, which server.py streams to the dashboard. The
correction loop lives only in pipeline.py.

## 10. Timeline and critical path

- FYDP1 runs October to January. Deliverables are the foundation, Safety-Critic
  v1, Dashboard v1, and a four-month checkpoint.
- FYDP2 runs February to June. Full Safety-Critic, Dashboard v2, expanded testbed,
  benchmarking against the baseline, and final documentation.
- We are in November of FYDP1, building the Planner and writing the schema.

The critical path to the January checkpoint: lock the schema this week, confirm
the Planner emits it (mostly done, since the model study already shows a local 14B
model produces schema-valid commands reliably), build the Safety-Critic rule set
for one scenario, and stand up a minimal dashboard. Everything else is FYDP2. Do
not let the proposal's promise of rules covering all ten attacks pull the work
into breadth now. One scenario, done properly end to end, is worth more at the
checkpoint than ten half-built ones.

## 11. Open decisions still to lock

These are not yet decided. Do not assume an answer. Flag them when they become
relevant and get a human to decide.

- Which tools can the Planner call in FYDP1? Only nmap, searchsploit, and Modbus
  reads, or the full baseline tool list?
- Is Modbus write in scope for FYDP1, or only reads? Writes are the dangerous
  operation and the schema already treats them differently, so this changes what
  the Critic has to defend against first.
- Is the target scope a fixed list of IPs or a CIDR range, and who sets it?
- Has Damil written any schema code yet, and if so, does it match the v1 in
  Section 7?
- Is the first scenario actually a Modbus register read and write against the
  PyModbus simulator? The v1 schema assumes this. Confirm before building the
  Planner on top of it.

## 12. Team division of labour

Core work, owned by Ayesha and Damil only: the schema, the Safety-Critic, the
Executor, the Planner, and the pipeline. These are tightly coupled, so a mistake
in one breaks everything downstream. This is exactly where unreliable work cannot
be allowed.

Safe, isolated work that can be given to Maryum and Amaan without risk to the
pipeline, because each is verifiable by inspection and cannot silently corrupt the
core:

- Standing up the Dockerised PyModbus testbed as a clean sandbox.
- Building the dashboard front-end skeleton against a fake data feed.
- Assembling the labeled safe and unsafe command list for the one scenario, which
  Ayesha reviews before it is used.

The paper search is not given to them, because post-2026 citations have to be
verified anyway and that is the one thing that cannot come back wrong.

## 13. Known weak points and outstanding corrections

This is the supervisor watch-list. Each item is something a committee member could
catch, so fix it before it is read, not after.

- The model selection document still uses the old name AEGIS-Sec. Propagate the
  rename to GOVERNOR-OT.
- Model contradiction across documents. The proposal lists Llama-3-8B or Qwen-2.5
  with Groq or Colab as options. The selection document picks qwen2.5-coder:14b on
  Kaggle or Colab with 2x T4. Fix the proposal wording so the two agree.
- Inconsistent argument about omitted fields. Section 4 of the model doc calls one
  model's omitted ports "correctly omitted rather than guessed," while Section 5.3
  calls another model's omissions "evasive" and "functionally unusable." Both
  models mostly left the field blank. The defensible position is that the port
  must be required for Modbus and the tool supplies the default, so the model
  never has to decide it. Make the document say that consistently.
- Thin factual evidence. The choice rests on 15 prompts and one factual probe (the
  Modbus port). State this in the limitations, or add a few more factual probes.
- Refusal rate is keyword-based. The 3.3% figure means no refusal keywords
  appeared, which can miss refusals worded differently. Hand-check a sample and
  report how many rows were checked.
- Unverified citation, important. Our documents say the Hammar NDSS 2026 paper
  shows "a 14B model beating DeepSeek-R1 671B, Gemini 2.5 Pro, and OpenAI o3." The
  paper, verified, describes a lightweight model and a method, and the confirmed
  comparison is a recovery-time reduction of up to 30% versus Gemini 2.5 Pro and
  OpenAI o3, plus a proven bound on hallucination probability. The DeepSeek-R1
  671B comparison and the exact 14B size could not be confirmed. Do not repeat the
  unverified sentence. Open the PDF and check before it goes into anything
  published.
- Citation hygiene. The Top-5 document credits TrustAgent to "Wang et al." The
  paper is Hua et al., arXiv:2402.01586. The proposal already has it right, so
  make them agree.
- Another citation to confirm: the proposal says a rule-based check "finished in
  under two seconds" according to the MCP auditing paper (arXiv:2603.21641). That
  paper is about auditing MCP servers, not AST checks. Confirm the figure and that
  the source supports the claim.
- Pin the exact Foundation-Sec checkpoint tested. The base is Foundation-Sec-8B
  with a 4096-token context. There is a later instruct and a reasoning variant.
  Name the precise Hugging Face checkpoint for reproducibility.
- Timeline note. The Gantt put Safety-Critic v1 in January, but the schema blocks
  both the Planner and the Safety-Critic, so the schema is the first thing to
  finish.

## 14. Literature snapshot

A verified shortlist already lives in the project as
GOVERNOR-OT_Literature_Shortlist.md, grouped by the part of the argument each
source supports. With the six sources already in the proposal, that is roughly 20
to 25 citable works, which is a normal FYP size. Aim to engage deeply with 12 to
15 and cite the rest in support. The groups:

- Group A: autonomous LLM pentest agents, for positioning against the baseline.
- Group B: LLMs for ICS, OT, and Modbus security. This is where the industrial
  novelty lives or dies, and the proposal currently has zero sources here. The
  closest neighbour is ICSSPulse (arXiv:2602.20663), an LLM-assisted Modbus and
  OPC UA pentest platform whose LLM assists reporting, not command safety. Cite it
  and state the difference clearly.
- Group C: structured output and constrained decoding, which backs the schema.
- Group D: LLM agent safety and guardrails, the spine of the motivation.
- Group E: hallucination and reliability, and why not to use an LLM as the judge.
- Group F: AST and static analysis as a safety mechanism, which backs the
  AST-Critic specifically.

The clean spine for the related-work section: agents act unsafely at a measured
rate, the existing checks are mostly another model with its own biases,
deterministic pre-execution checking is a real and growing idea, none of the LLM
pentest agents or the LLM-plus-ICS systems put a deterministic safety gate before
command execution in an OT setting, and that gap is what GOVERNOR-OT fills, on a
local model whose reliability we measured ourselves.

See the shortlist file for the per-paper flags, especially the Hammar flag
repeated in Section 13.

## 15. Rules for how to help on this project

These apply to every tool and every session, including Claude Code.

- Never hallucinate a citation, a statistic, or a paper detail. Verify by
  searching, and flag anything not fully confirmed rather than stating it.
- Keep "AST-validated," meaning syntactically well-formed, strictly separate from
  "actually safe," meaning what the rule set enforces. Do not let these blur in
  code, comments, or writing.
- When comparing results to VEXAIoT's tables, push back on any framing that treats
  it as a direct apples-to-apples benchmark. Different hardware, environment, and
  attack set, and a near-opposite metric.
- When editing any Word document, change content only. Never touch formatting,
  margins, or layout.
- Avoid em dashes. Keep language plain and human. Avoid the generic signs of AI
  writing, which include over-symmetric lists, needless tables, and inflated
  transitions. The project coordinator flagged earlier writing as sounding
  AI-generated, so this is a real constraint.
- Be direct and specific, like a strict but fair supervisor. Point out where the
  reasoning, scope, or claims are weak before a committee member does.
- Task emails to team members use a four-day maximum deadline with the supervisor
  in CC, because the timeline is tight.

## 16. Glossary, the small things

For anyone new to the domain, or a fresh session with no background.

- PLC: programmable logic controller. The small industrial computer that controls
  physical equipment in a factory. The thing we are protecting from unsafe
  commands.
- OT: operational technology. The computing that runs industrial and physical
  processes, as opposed to IT, which runs offices and data. OT is where a bad
  command can damage real equipment.
- Modbus: a simple, old, widely used industrial protocol for talking to PLCs over
  a network. Modbus TCP uses port 502.
- Register: a numbered storage slot on a PLC that holds a value. Reading a
  register asks for its value. Writing a register changes it, which can change
  physical behaviour, which is why writes are the dangerous operation.
- PyModbus: a Python library that speaks Modbus. We use it to simulate a PLC in a
  sandbox and to send approved commands to it.
- AST: abstract syntax tree. The tree-shaped representation of a piece of code
  after it is parsed. Python's ast module turns a code string into one. We parse
  the command's expression field into an AST and read the function and arguments
  from it. Parsing succeeding means well-formed, not safe.
- Pydantic: a Python library that defines a strict data shape (a model) and
  validates incoming data against it, rejecting anything that does not fit. Our
  Command schema is a Pydantic model.
- Ollama: a tool for running local LLMs on your own machine. It can constrain a
  model's output to a given JSON shape, which is how the Planner is forced to emit
  a valid Command.
- Structured output, or schema-constrained output: making the model produce output
  that matches a fixed shape at generation time, rather than asking it politely and
  hoping. This is what removes most malformed output at the schema level.
- Planner: the component that uses the local LLM to propose a command.
- Safety-Critic: the plain-Python, rule-based component that approves or blocks a
  proposed command. Not another AI model. This is the heart of the project.
- Executor: the component that runs an approved command against the sandbox.
- Correction loop: when the Critic blocks a command, it returns to the Planner with
  the violated rule, so the model tries again with a real reason. The only loop in
  the system.

End of file.
