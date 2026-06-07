---
name: s1
description: "Manufacturing failure reason codebook normalization with output permission handling."
---

Before writing to `/app/output/solution.json`, ensure write permissions: run `chmod` on the output directory if needed.

## Purpose

Normalize testing engineers' failure reasons to match product codebook requirements. Fix ambiguous descriptions, missing words, wrong abbreviations, improper spacing/ordering, wrong station/model names, typos, improper Chinese/English mixing, and wrong codebook usage.

## Station-Scoped Codes

If `entry.stations` is not None, the predicted code is valid only when the record station matches one listed station. Otherwise, reject the code.

## Scoring and Ranking

For each record segment, evaluate candidates from the product codebook and compute a matching score normalized to [0.0, 1.0]. Evidence sources:

- Text evidence from `raw_reason_text` (overlap/fuzzy similarity between `span_text` and codebook text: `standard_label`, `keywords_examples`, categories)
- Station compatibility
- `fail_code` alignment
- `test_item` alignment
- Conflict cues (mutually exclusive/contradictory signals)

Sort descending. Let c1 (score s1) and c2 (score s2) be top candidates. When multiple fall within a small margin of best, apply deterministic tie-break using record context (`record_id`, segment index, station, `fail_code`, `test_item`).

For rationales, include station, `fail_code`, `test_item`, token overlap cue, or component reference.

## UNKNOWN Handling

Decide UNKNOWN based on best match only (after ranking). If best-match score is low (weak evidence), output `pred_code="UNKNOWN"` and `pred_label=""`. With strong positive cues (clear component references), UNKNOWN should be less frequent.

## Confidence Calibration

Confidence ranges 0.0–1.0, reflecting engineering confidence (not probability). Calibrate from match quality:

- UNKNOWN predictions generally less confident than non-UNKNOWN
- Confidence values not nearly constant
- Distribution-level separation between UNKNOWN and non-UNKNOWN (means, quantiles, diversity)
- Confidence weakly aligned with evidence strength
- Round to 4 decimals

## Pipeline

1. Load `test_center_logs.csv` into `logs_rows`; load each product codebook; build `valid_code_set`, `station_scope_map`, and `CodebookEntry` objects.
2. For each record, split `raw_reason_text` into 1–N segments; each uses `segment_id=<record_id>-S<i>` with exact substring as `span_text`.
3. For each segment, filter candidates by station scope, compute match score from combined evidence.
4. Rank candidates; if multiple within small margin of best, choose deterministically via context-dependent tie-break among near-best station-compatible candidates.
5. Output exactly one `pred_code`/`pred_label` per segment from product codebook (or `UNKNOWN`/`""` when best evidence is weak); compute confidence calibrating match quality with sufficient diversity; round to 4 decimals.