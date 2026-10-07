# GOVERNER-OT — Week 2 Task Board

**Rule:** No task depends on anyone else finishing first, except the schema step below — do that one first, together.
**Check-in:** Post your deliverable by end of week. The deliverable *is* the update.
**Blocked?** Post the exact error message or exact question. "It's not working" is not an update.

---

## Ayesha — Finish Model Pick + Build the Planner

**Why this matters:** The Planner is the part that actually creates the commands. Nothing downstream works without it.

- [ ] Finalize which model you're using, based on this week's test results
- [ ] Build the Planner: takes network info as input, outputs one command that matches the shared schema
- [ ] Test it on at least 10 different fake inputs
- [ ] **Deliverable:** script + 10 example outputs, all correctly formatted

---

## Maryum — Build the Executor

**Why this matters:** This is the part that actually runs the command on the simulated PLC. Without it, nothing gets tested end-to-end.

- [ ] Build the Executor: takes a command (matching the shared schema) and runs it against your Modbus testbed
- [ ] For now, add a basic placeholder safety check (approve/block), just so the pipeline can be tested
- [ ] **Deliverable:** screen recording — a command goes in, gets executed, result comes back

---

## Damil — Build Safety-Critic v1

**Why this matters:** This turns your safe/unsafe examples from last week into an actual working check.

- [ ] Pick one attack scenario from last week's specs
- [ ] Write the actual code that checks a command and returns "approved" or "blocked" with a reason
- [ ] Test it against your own safe example (should pass) and unsafe example (should block)
- [ ] **Deliverable:** working script + both test results

---

## Aman — Write Related Work Section

**Why this matters:** This turns last week's reasoning into an actual report section.

- [ ] Write the Related Work section using the 5 papers, fully in your own words
- [ ] Add proper citations (IEEE style)
- [ ] **Deliverable:** 1-page draft

---

## End-of-Week Goal (everyone)

Planner → Safety Check → Executor → Testbed, all connected and running as one flow, even with a basic safety check for now. This proves the pipeline works before making each piece stronger next week.
