# GOVERNOR-OT Literature Shortlist

Verified on 2026-11-12 by searching for each paper directly. Every entry below
was found and checked this session unless the status line says otherwise. Where a
claim in one of our own documents could not be fully confirmed, it is flagged so
it can be checked against the paper text before it goes into a published writeup.

This list is grouped by the exact part of the project each source supports, so
you can see at a glance where the argument is well covered and where it is thin.
Together with the six sources already in the proposal, this gives roughly 20 to
25 citable works, which is a normal size for an FYP literature review. Aim to
discuss maybe 12 to 15 of them in real depth and cite the rest in support.

## Group A: Autonomous LLM penetration-testing agents (positioning vs the baseline)

These place VEXAIoT, and us, inside the wider line of LLM pentest agents. Use them
in related work to show what has been tried and what none of them add (a
deterministic pre-execution check in an OT setting).

- PentestGPT: Evaluating and Harnessing LLMs for Automated Penetration Testing. Deng et al., USENIX Security 2024. arXiv:2308.06782. The most cited early LLM pentest system; the standard reference point.
- PentestAgent: Incorporating LLM Agents to Automated Penetration Testing. Shen et al., ACM AsiaCCS 2025. arXiv:2411.05185. Multi-agent plus RAG, with its own benchmark on vulnerable Docker targets.
- VulnBot: Autonomous Penetration Testing for a Multi-Agent Collaborative Framework. Kong et al., 2025. arXiv:2501.13411. Multi-agent, uses a Penetration Task Graph; good contrast to our single deterministic gate.
- xOffense: AI-driven Autonomous Penetration Testing with Offensive Knowledge-Enhanced LLMs. Luong et al., 2025. arXiv:2509.13021. Uses a fine-tuned open-source model (Qwen3-32B). Directly supports our "a mid-scale local model is enough" argument.
- CHECKMATE: Automated Penetration Testing with LLM Agents and Classical Planning. Wang et al., Dec 2025. arXiv:2512.11143. Adds an external structured "brain" to fix LLM weaknesses in long-horizon planning. Same philosophy as our deterministic layer, applied to planning rather than safety. Strong to cite.
- RapidPen: Fully Automated IP-to-Shell Penetration Testing with LLM Agents. Nakatani, 2025. arXiv:2502.16730.
- AutoPentest: Enhancing Vulnerability Management with Autonomous LLM Agents. Henke, 2025. arXiv:2505.10321.

## Group B: LLMs for ICS / OT / Modbus security (this is where our OT novelty lives or dies)

The proposal currently has no sources in this group, which is the single biggest
gap. These show the OT+LLM space is active, and let us state precisely what is
missing in it: none pairs autonomous command generation with a deterministic
pre-execution safety gate.

- ICSSPulse: A Modular LLM-Assisted Platform for Industrial Control System Penetration Testing. 2026. arXiv:2602.20663 (also a Springer chapter). Network scanning plus protocol-aware Modbus and OPC UA interaction plus LLM-assisted reporting. The closest neighbour to our work. Their LLM assists reporting, not command safety, which is exactly our differentiator. Must cite and must differentiate.
- MERIDIAN: A Multi-Agent LLM Pipeline for Vulnerability Discovery, Validation and Patching in Microgrid ICS. 2025 (ResearchGate preprint). Multi-agent over SCADA, PLC, Modbus, mapped to MITRE ATT&CK for ICS. Find a stable version (arXiv or a venue) before citing.
- Large Language Models as Explainable Cyberattack Detectors for Energy ICS. Kong (U. Toronto), 2026. arXiv:2604.26079. LLM over Modbus/TCP traffic. Defensive rather than offensive, useful to show the two sides of LLM+Modbus work.
- From Words to Wires: Toward Rapid ICS Cyber-Range Construction Using LLMs (Words2Wires). 2025, Springer chapter. LLM-generated runnable Modbus/OPC-UA testbeds. Relevant to how we justify a simulated testbed and to future work.

## Group C: Structured output and constrained decoding (backs the schema)

This is the technical ground under the schema and the "structured output" step in
the Planner.

- Qwen2.5-Coder Technical Report. Hui et al., 2024. arXiv:2409.12186. Our selected Planner model; Apache 2.0; confirmed 14.7B for the 14B variant.
- Efficient Grammar-Constrained Decoding via Parser Stack Classification. Li et al., 2026. arXiv:2608.03065. How a schema is enforced at generation time (token masking against a grammar). Cite for the mechanism behind format-constrained output.

## Group D: LLM agent safety and guardrails (why a mandatory pre-execution check is needed)

This is the spine of the motivation: agents act unsafely often, and the existing
checks are mostly another model rather than a deterministic rule.

- VESTA: A Fully Automated Scenario Generation and Safety Evaluation Framework for LLM Agents. Jia et al., Jun 2026. arXiv:2606.08531. Confirmed: average unsafe-action rate 47.1% across 1,072 scenarios and 12 agents, some over 70%. Already in the proposal; numbers check out.
- TrustAgent: Towards Safe and Trustworthy LLM-based Agents. Hua et al., 2024. arXiv:2402.01586. The closest existing safety layer, built on an "Agent Constitution" checked by an LLM across pre, in, and post planning. Already in the proposal. Note: our Top-5 document credits this to "Wang et al." It is Hua et al. Fix that before submission.
- Safeguarding Large Language Models: A Survey. 2025, journal Artificial Intelligence Review. DOI 10.1007/s10462-025-11389-2. Peer-reviewed survey of guardrail systems (Llama Guard, NeMo Guardrails, Guardrails AI). Good anchor citation for "what a guardrail is."
- Towards Verifiably Safe Tool Use for LLM Agents. Doshi et al., ICSE 2026. arXiv:2601.08012. Argues for guardrails with formal guarantees over model-based safeguards that only reduce risk probabilistically. This is our thesis stated by someone else; one of the strongest cites in the list.
- TraceSafe: A Systematic Assessment of LLM Guardrails on Multi-Step Tool-Calling Trajectories. Chen et al., 2026. arXiv:2604.07223. Finds guardrail effectiveness is driven more by structural data competence (JSON parsing) than by semantic alignment. Nuanced and directly relevant to a schema-plus-rules design.
- Isolation as a First-Class Principle for LLM-Agent System Safety. 2026. arXiv:2607.12406. Survey; its "agent-execution boundary" is exactly where our Safety-Critic sits.
- A Survey on Autonomy-Induced Security Risks in Large Model-Based Agents. 2025. arXiv:2506.23844. Broad survey for the introduction.

## Group E: Hallucination, reliability, and why not to use an LLM as the judge

- Incident Response Planning Using a Lightweight LLM with Reduced Hallucination (arXiv title: Hallucination-Resistant Security Planning with a Large Language Model). Hammar, Alpcan, Lupu, NDSS 2026. arXiv:2602.05279. Already in the proposal. Confirmed: it reduces recovery time by up to 30% versus frontier models (Gemini 2.5 Pro, OpenAI o3) and proves a bound on hallucination probability using fine-tuning plus RAG plus lookahead planning plus conformal abstention. FLAG: our documents say it shows a "14B model beats DeepSeek-R1 671B." The paper describes a lightweight model and a method, and the comparison I could confirm is against Gemini 2.5 Pro and o3, not DeepSeek-R1 671B, and the 14B size is not confirmed. Check the exact parameter count and the exact models it beats against the paper before repeating that sentence.
- A Survey on LLM-as-a-Judge. Gu et al., 2024. arXiv:2411.15594. Documents position bias and self-enhancement bias when an LLM grades output. This is the citation that justifies NOT using an LLM to check the Planner, which is the whole point of a deterministic Critic.
- Foundation-Sec-8B Technical Report. Kassianik, Kedia et al., Cisco Foundation AI, April 2025. arXiv:2504.21039. Confirmed: Llama-3.1-8B backbone, continued pretraining on ~5.1B cybersecurity tokens, Apache 2.0, 4096-token base context. Note for the model doc: pin the exact checkpoint you tested (base vs the later reasoning/instruct variant), since you refer to "Foundation-Sec-8B-Reasoning."

## Group F: AST and static analysis as a safety mechanism (backs the AST-Critic specifically)

- Auditing MCP Servers for Over-Privileged Tool Capabilities. 2026. arXiv:2603.21641. Already in the Top 5. Deterministic, non-AI, pre-execution risk analysis of agent tool calls. Not re-verified this session; confirm the sub-two-second figure against the paper.
- ASTBAR: Distilling Benign Knowledge with Fine-Grained AST Fragments for Web Shell Detection. Gao, Chen et al., IEEE/ACM IWQoS. AST-fragment static detection of malicious scripts. Shows AST-level analysis catching what pattern matching misses, which is the argument for parsing the command rather than regex-matching it.
- Synode / static analysis and runtime enforcement against injection in Node.js (eval, exec). Staicu et al. (likely "Synode," NDSS 2018). Classic precedent for statically checking values before a dangerous sink. Confirm the exact title and venue before citing.

## How this maps onto the argument

The clean spine for the related-work section:
agents act unsafely at a measured rate (Group D, VESTA) → the existing checks are
mostly another model, which has its own bias and can fail the same way (Group D
TrustAgent, Group E LLM-as-a-Judge) → deterministic, pre-execution checking of
agent actions is a real and growing idea (Group F, plus Verifiably Safe Tool Use)
→ none of the LLM pentest agents (Group A) or the LLM+ICS systems (Group B) put a
deterministic safety gate before command execution in an OT setting → that is the
gap GOVERNOR-OT fills, on a local model whose reliability we measured ourselves.
