---
name: persona-war-council
description: Convene a war council for a difficult business decision — a ruthless CFO, wartime operator, compassionate customer representative, and 1–2 situational advisors debate, then a neutral judge recommends a course and makes a hypothetical $1,000 bet. Use for "war council", "war-council", "/persona-war-council", or requests for adversarial advisor debate with a final recommendation. Works without saved personas; use persona-council for debate among an existing persona panel.
---

# Persona War Council

Pressure-test a difficult decision with advisors whose priorities conflict, then get a concrete recommendation from a separate judge.

Inspired by [Wade Foster's War-Council post](https://x.com/wadefoster/status/2066507532135203130). The three standing roles, situational advisors, debate, and neutral judge's hypothetical $1,000 stake come from his description. The workflow below is this plugin's adaptation, not a reproduction of his original skill or an endorsement by him.

## Frame the decision

Use the user's question and supplied material to state the options, desired outcome, constraints, deadline, and what is already known. Include the status quo when it is a real option. Preserve any exact question the user supplied. Ask only for missing information that would materially change the decision; otherwise state assumptions and proceed.

Separate facts with source references from assumptions and unknowns. The user's preferred answer is context, not evidence. Do not invent financial figures, customer testimony, or internal knowledge to make the debate feel informed.

## Seat the advisors

Default to these three standing roles plus 1–2 specialists chosen for the decision:

| Advisor | What they defend | What they challenge |
|---|---|---|
| Ruthless CFO | Cash, opportunity cost, unit economics, downside survival | Wishful forecasts, sunk costs, spending without a credible return |
| Wartime operator | Execution, speed, dependencies, reversibility | Plans that ignore capacity, unclear ownership, delays that destroy options |
| Compassionate customer representative | Customer outcomes, trust, accessibility, transition costs | Decisions that transfer hidden costs or harm to customers |

Choose specialists to cover an actual missing perspective: for example, a security lead for a data-sharing decision or a channel partner for a distribution change. State why each specialist is needed. Give each advisor a short role brief with their priorities and the trade-off they will scrutinize. They can agree when the evidence warrants it; do not manufacture conflict or turn the roles into caricatures.

These are temporary synthetic advisory roles, not researched people or a representative customer sample. No `.personas/` folder is required, and do not save invented advisors as grounded personas. If the user names saved personas, resolve them from `$PERSONA_HOME` when set, otherwise `./.personas/`, and read their full documents. Use exactly the named personas; explain which perspectives they cover and any gaps, without silently adding advisors or overriding their documented values. If a named persona is missing, help the user locate or create it instead of inventing its history.

Announce the roster and scope: normally 4–5 advisors, two rounds, and one judge (9–11 agent turns). Respect an existing budget; obtain agreement before expanding it. This skill calls for separate subagents, within the host's concurrency limit. If delegation is unavailable, offer a clearly labeled single-agent walkthrough rather than claiming independent advisors ran.

## Round 1 — Independent positions

Give each advisor the same decision brief and supporting material, plus only their own role brief or persona document. Run them independently, in parallel where available. Do not reveal other advisors' positions until all initial answers are in.

Ask each advisor to return:

- **Grounding:** relevant facts with references; any persona-document sections used; explicit assumptions and a high/medium/low confidence read with a reason. A role brief explains a perspective, not evidence about the business.
- **Assessment:** a concise rationale connecting the evidence to the recommendation, including the principal trade-off. Request a decision summary, not private chain-of-thought.
- **Talking:** their public position — preferred option, strongest case for it, biggest risk, one uncomfortable observation, and the fact or condition that would change their mind.

## Round 2 — Challenge and revise

Compile every advisor's Talking into a digest. Give each advisor the complete public digest and their own prior response; keep the other advisors' grounding and assessment out of the debate digest.

Ask each to engage the strongest opposing argument by advisor name, acknowledge what it gets right, and explain what remains unresolved. Return updated Grounding and a concise Assessment, followed by Talking: hold or change the recommendation, why, the strongest unanswered objection, and a practical safeguard or test. Do not reward stubbornness or agreement for its own sake.

Stop after this rebuttal round by default. A further round is useful only when a specific unresolved question can be answered with available evidence and the user's budget permits it. Missing facts call for a test or a conditional recommendation, not endless debate.

## Judge — Make the call

Use a fresh neutral subagent that has not played an advisor. Give it the original brief, source material, and both rounds' evidence and public positions. Tell it to weigh the quality of evidence and arguments, not seniority, theatrical confidence, vote count, or the user's preferred answer.

The judge returns:

1. **Recommendation:** choose a course, its conditions, and the strongest reason. If a missing fact could reverse the choice, recommend a specific information-gathering step and explain the decision on either side of its result.
2. **Trade-offs and dissent:** the strongest case against the recommendation, who bears the downside, and which objections remain unanswered.
3. **Strategic response:** identify the relevant stakeholders, their incentives, and how their plausible responses could change the outcome. Use a small payoff/scenario table if helpful; distinguish assumed payoffs from known ones. Do not claim a game-theoretic equilibrium without a specified game and supporting assumptions.
4. **Hypothetical $1,000 bet:** name the recommended course and the observable outcome on which the judge would stake the fictional $1,000, with a time horizon, success/failure criterion, and confidence. If those are not supplied, propose and label them. This is a commitment device, not real money, a measured probability, or evidence that higher stakes improve model accuracy.
5. **Next move and reversal trigger:** the first practical action, the evidence to collect, and what result would cause the recommendation to change.

The council advises; it does not authorize executing the decision, contacting people, spending money, or placing a real bet.

## Deliver the decision and report

Lead the chat response with the judge's recommendation and key condition. Follow with a compact advisor-position table, strongest unresolved disagreement, hypothetical bet, and next action. Make clear these are simulated advisors and the recommendation needs human judgment.

Write a self-contained `report.html` to `./.persona-research-runs/war-council-<YYYY-MM-DD>-<slug>/` using [the shared report specification](../persona-research/references/html-report.md). Include the decision brief, role briefs and their synthetic/saved origins, every advisor's public answers by round with confidence and collapsible grounding, and the judge's complete decision summary. Label advisor count as perspectives, not a research sample; the bet is fictional. Credit and link Wade Foster's post in the report. Tell the user the report path.
