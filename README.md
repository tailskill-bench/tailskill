# TailSkills: Focused but Fragile — Tail Knowledge Collapse in Recursive Agent Skill Distillation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-EMNLP_2026_Submission-blue)]()

> When agent skills are recursively compressed, the happy path survives — but exception handling silently vanishes.

**TailSkills** is a benchmark and experimental framework for studying **Tail Knowledge Collapse**: the systematic loss of rare exception-handling knowledge during recursive LLM-based distillation of agent skills. As skills are compressed through successive rounds (S1 → S2 → S3 → S4), common-case utility remains stable while tail performance degrades precipitously.

Paper: *Focused but Fragile: Tail Knowledge Collapse in Recursive Agent Skill Distillation* (EMNLP 2026 submission).

---

## Key Findings

| Skill Generation | Compression | Common-Case | Tail-Case | Gap (Δ) | Collapse Index |
|:----------------:|:-----------:|:-----------:|:---------:|:-------:|:--------------:|
| S1 (original)    | ~100%       | 50.8%       | 50.5%     | 0.3%    | 0.00           |
| S2 (1× distilled)| ~70%        | 52.5%       | 35.4%     | 17.1%   | 0.49           |
| S3 (2× distilled)| ~49%        | 49.2%       | 23.4%     | 25.8%   | 0.64           |
| S4 (3× distilled)| ~34%        | 49.2%       | 23.1%     | 26.1%   | 0.65           |

- **Common-case performance** remains stable across all distillation depths (50.8% → 49.2%).
- **Tail-case performance** drops from 50.5% (S1) to 23.1% (S4), a relative decline of over 54%.
- **Gap** widens from 0.3% (S1) to 26.1% (S4), confirming that compression preferentially discards tail knowledge.
- **Collapse Index** grows from 0.00 to 0.65, quantifying the widening gap between common-case and tail retention.

---

## Benchmark Structure

TailSkills extends [SkillsBench](https://github.com/benchflow-ai/skillsbench) with 14 variant types across 6 categories, producing **208 Oracle-verified** exception-heavy task variants with deterministic verifiers.

| Category | Variant Type | N | Exp. Frag. |
|----------|-------------|:-:|:----------:|
| **A: Data Encoding** | A1: BOM injection | 23 | Med |
| | A2: Zero-width characters | 26 | Med–High |
| **B: File System** | B1: Read-only output directory | 50 | Med |
| | B2: Output contamination | 10 | Med |
| **C: Data Boundary** | C1: NaN/Inf poisoning | 13 | High |
| | C2: Duplicate primary keys | 3 | Low |
| | C3: Extreme values (0, −1, −999) | 13 | High |
| | C4: Type confusion (num → str) | 10 | High |
| **D: Network / Service** | D1: DNS jitter (50% loss) | 19 | Med–High |
| | D2: HTTPS connection throttling | 16 | Med–High |
| **E: Dependency** | E1: Missing optional dependency | 20 | Med |
| | E2: Library version drift | 2 | High |
| **G: Security** | G1: Multi-vector attack | 2 | High |
| | G2: Security fallback | 1 | High |
| **Total** | | **208** | |

Each variant satisfies a **Recoverability Constraint**: the injected anomaly must not render the task unsolvable — it should only fail if the agent's skill lacks the specific defensive logic.

---

## Distillation Protocol

Recursive distillation applies a **neutral compression prompt** at each step — it does not instruct the model to preserve or remove any particular content. The LLM decides what is "most critical," naturally favoring the happy path over exception handling.

```
S1 (~11,000 B, 100%) → S2 (~7,700 B, 70%) → S3 (~5,400 B, 49%) → S4 (~3,700 B, 34%)
```

Two distillation strategies are provided:

| Strategy | Script | Description |
|----------|--------|-------------|
| **Regular** | `scripts/distill_recursive_openai.py` | Neutral compression — no tail-preservation guidance |
| **Tail-Aware** | `scripts/distill_tail_aware.py` | Explicitly preserves exception-handling knowledge |

---

## Repository Structure

```
TailSkill/
├── configs/
│   ├── task_variant_matrix.yaml       # Task × variant applicability matrix
│   └── variants/                      # 25 YAML variant configurations
├── scripts/
│   ├── distill_recursive_openai.py    # Recursive distillation (regular)
│   ├── distill_tail_aware.py          # Tail-aware distillation
│   └── ...                            # Analysis and utility scripts
├── src/tailskills/
│   ├── inject/
│   │   ├── injector.py                # Variant task generator
│   │   ├── _tail_inject.py            # Container-side data mutation
│   │   ├── dockerfile_patcher.py      # Dockerfile overlay injection
│   │   └── test_augmentor.py          # Tail-specific test assertion injection
│   ├── evaluate/
│   │   ├── runner.py                  # Agent evaluation runner
│   │   ├── metrics.py                 # Collapse Index and gap metrics
│   │   └── reporter.py               # Result aggregation
│   └── utils/
│       ├── config_loader.py
│       ├── harbor_wrapper.py
│       └── task_analyzer.py
├── generated-tasks/                   # 208 Oracle-verified variant tasks
│   └── {task}--{variant}/
│       ├── instruction.md             # Agent-visible task (identical to base)
│       ├── environment/
│       │   ├── Dockerfile             # Patched with variant injection
│       │   └── skills/s{1..4}/        # Skill documents per generation
│       ├── solution/                  # Oracle solution
│       └── tests/                     # Deterministic verifier tests
├── acl-style-files/                   # Paper source (LaTeX)
├── AGENT.md                           # Agent construction guide
└── pyproject.toml
```

---

## Quick Start

### Prerequisites

- Docker Desktop
- Harbor v0.4.0+ (`pip install harbor-cli`)
- LLM API key (OpenAI-compatible endpoint)

### Installation

```bash
cd tailskills
pip install -e .
```

### Generate Variant Tasks

```bash
python -m tailskills inject --config configs/task_variant_matrix.yaml --output generated-tasks/
```

### Run Oracle Verification

```bash
for variant in generated-tasks/*/; do
  PYTHONUTF8=1 harbor run -p "$variant" -a oracle -y
done
```

### Run Agent Experiments

```bash
API_KEY="your-key"
BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"

for variant in generated-tasks/*/; do
  PYTHONUTF8=1 harbor run -p "$variant" \
    -a openhands-sdk -m 'openai/gemini-2.5-flash' \
    --ae LLM_API_KEY="$API_KEY" --ae LLM_BASE_URL="$BASE_URL" -y
done
```

### Distill Skills

```bash
# Regular recursive distillation
python scripts/distill_recursive_openai.py --model openai/gemini-2.5-flash

# Tail-aware distillation
python scripts/distill_tail_aware.py
```

---

## Metrics

We define three primary metrics:

- **Common-case and tail-case success rates** $A(m, s_k, \mathcal{D}_c)$ and $A(m, s_k, \mathcal{D}_t)$ across distillation depths $k$.
- **Tail-collapse gap** $G_k$: the differential degradation between common-case and tail distributions.
- **Collapse Index** $\mathrm{CI}_k$: quantifies the relative retention of tail knowledge compared to common-case knowledge, normalized by baseline.

$$\mathrm{CI}_k = 1 - \frac{A(m, s_k, \mathcal{D}_t) / A(m, s_1, \mathcal{D}_t)}{A(m, s_k, \mathcal{D}_c) / A(m, s_1, \mathcal{D}_c)}$$

A $\mathrm{CI}_k$ approaching 1 indicates severe collapse.

---

## Citation

```bibtex
@article{tailskills2026,
  title={Focused but Fragile: Tail Knowledge Collapse in Recursive Agent Skill Distillation},
  author={Anonymous},
  journal={arXiv preprint},
  year={2026}
}
```

## Acknowledgements

TailSkills is built on top of [SkillsBench](https://github.com/benchflow-ai/skillsbench) (MIT License) and uses [Harbor](https://github.com/benchflow-ai/harbor) for Docker-containerized agent evaluation.

## License

This project is licensed under the [MIT License](LICENSE).
