---
name: s1
description: "Multi-hop evidence search and structured extraction over enterprise artifact datasets (docs/chats/meetings/PRs/URLs)."
---

# Enterprise Artifact Search Skill

Delegates **multi-hop artifact retrieval + structured entity extraction** to a lightweight subagent, keeping the main agent's context lean.

Key capabilities:
1) **Product grounding & anti-distractor filtering** (prevents mixing CoFoAIX/other products when asked about CoachForce).
2) **Key reviewer extraction rules** (prevents "meeting participants == reviewers" mistake; prefers explicit reviewers, then evidence-based contributors).

---

## When to Invoke

Invoke when ANY apply:
1. Question requires **multi-hop** evidence (artifact → references → other artifacts).
2. Answer must be **retrieved** from artifacts (IDs/names/dates/roles), not inferred.
3. Evidence is scattered across multiple artifact types (docs + slack + meetings + PRs + URLs).
4. You need **precise pointers** (doc_id/message_id/meeting_id/pr_id) to justify outputs.
5. You must keep context lean.

---

## Invocation

```python
Task(subagent_type="enterprise-artifact-search", prompt="""
Dataset root: /root/DATA
Question: <paste the question verbatim>

Output requirements:
- Return JSON-ready extracted entities (employee IDs, doc IDs, etc.).
- Provide evidence pointers: artifact_id(s) + short supporting snippets.

Constraints:
- Avoid oracle/label fields (ground_truth, gold answers).
- Prefer primary artifacts (docs/chat/meetings/PRs/URLs) over metadata-only shortcuts.
- MUST enforce product grounding: only accept artifacts proven to be about the target product.
""")
```

---

## Core Procedure

### Step 0 — Parse intent + target product
- Extract target product name (e.g., "CoachForce"), entity types needed (e.g., author employee IDs, key reviewer employee IDs), and likely relevant artifact types.
- If product name is missing, infer cautiously from nearby context ONLY if explicitly supported by artifacts; otherwise mark AMBIGUOUS.

### Step 1 — Build candidate set
Search in this order:
1) Product artifact file(s): `/root/DATA/products/<Product>.json` if exists.
2) Global sweep (if needed): other product files and docs mentioning the product name.
3) Within found channels/meetings: follow doc links (e.g., `/archives/docs/<doc_id>`), referenced meeting chats, PR mentions.

Collect candidates matching:
- type/document_type/title contains "Market Research Report" (case-insensitive)
- OR doc links/slack text contains "Market Research Report"
- OR meeting transcripts tagged document_type "Market Research Report"

### Step 2 — Product Grounding (Anti-distractor gate)
A candidate report is **VALID** only if it passes **at least 2 independent grounding signals**:

**Grounding signals (choose any 2+):**
A) Located under the correct product artifact container (e.g., inside `products/CoachForce.json` *and* associated with that product's planning channels/meetings).
B) Document content/title explicitly mentions the target product name ("CoachForce") or a canonical alias list derived from artifacts.
C) Shared in a channel clearly for the target product (e.g., `planning-CoachForce`, `#coachforce-*`) OR a product-specific meeting series (e.g., `CoachForce_planning_*`).
D) Document id/link path contains a product-specific identifier consistent with the target product.
E) Meeting transcript discussing the report includes target product context in meeting title/series/channel reference.

**Reject rule:** If report content repeatedly names a different product (e.g., "CoFoAIX") and lacks CoachForce grounding → mark as DISTRACTOR and discard.

### Step 3 — Select the correct report version
If multiple VALID reports exist, choose "final/latest" by precedence:
1) Explicit "latest" marker (id/title/link contains `latest`, or most recent date field)
2) Explicit "final" marker
3) Most recent by `date` field
4) Most frequently referenced in follow-up discussions (slack replies/meeting chats)

Keep the selected report's doc_id and link as the anchor.

### Step 4 — Extract author(s)
Priority order:
1) Document fields: `author`, `authors`, `created_by`, `owner`
2) PR fields if report is introduced via PR: `author`, `created_by`
3) Slack: user who posted "Here is the report…" message (only if it clearly links to the report doc_id and is product-grounded)

Normalize into **employee IDs**:
- If already `eid_*`, keep it.
- If only a name appears, resolve via employee directory metadata (name → employee_id) after product-grounded evidence is confirmed.

### Step 5 — Extract key reviewers (DO NOT equate "participants" with reviewers)
Key reviewers must be **evidence-based contributors**, not simply attendees.

**Tier 1 (best): explicit reviewer fields**
- Document fields: `reviewers`, `key_reviewers`, `approvers`, `requested_reviewers`
- PR fields: `reviewers`, `approvers`, `requested_reviewers`

**Tier 2: explicit feedback authors**
- Document `feedback` sections attributing feedback to specific people/IDs
- Meeting transcripts where turns are attributable AND those people provide concrete suggestions/edits

**Tier 3: slack thread replies to the report-share message**
- Only include users with substantive feedback/suggestions/questions tied to the report.
- Exclude: the author (unless explicitly wanted as reviewer), pure acknowledgements ("looks good", "thanks") unless no other reviewers exist.

**Critical rule:** Meeting `participants` list alone is NOT sufficient. Only count someone as a key reviewer if the transcript shows they contributed feedback OR they appear in explicit reviewer fields.

### Step 6 — Validate IDs & de-duplicate
- All outputs must be valid employee IDs (pattern `eid_...`) and exist in the employee directory if provided.
- Remove duplicates preserving order: authors first, then key reviewers.

---

## Output Format

Before writing output, ensure proper write permissions. Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/answer.json` to fix directory permissions.

### Final Answer Object
```json
{
  "target_product": "<ProductName>",
  "report_doc_id": "<doc_id>",
  "author_employee_ids": ["eid_..."],
  "key_reviewer_employee_ids": ["eid_..."],
  "all_employee_ids_union": ["eid_..."]
}
```

### Evidence Map
For each extracted ID, include artifact type + artifact id and a short supporting snippet:
```json
{
  "employee_id": "eid_xxx",
  "role": "key_reviewer",
  "evidence": [
    {
      "artifact_type": "meeting_transcript",
      "artifact_id": "CoachForce_planning_2",
      "snippet": "…Alex: We should add a section comparing CoachForce to competitor X…"
    }
  ]
}
```

---

## Recommendation Types

Return one of:
- **USE_EVIDENCE** — evidence sufficient and product-grounded
- **NEED_MORE_SEARCH** — missing reviewer signals; must expand search
- **AMBIGUOUS** — conflicting product signals or multiple equally valid reports

---

## Do NOT Invoke When

- The answer is in a single small known file with no cross-references.
- The task is a trivial one-hop lookup and product scope is unambiguous.