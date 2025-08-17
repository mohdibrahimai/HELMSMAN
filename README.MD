# HELMSMAN — Prompt Contracts + Fuzzing CI for Answer Engines

A production-oriented, working reference that turns prompt work into **engineering discipline**:

- **Contracts (DSL)** to specify expected behavior  
- **Harness + packs** to stress-test prompts/models  
- **Evaluators** to measure disambiguation & citation quality  
- **Diff + CI gates** to block regressions  

> Runs locally with no external APIs; uses a real, local corpus. Plug in your own retriever/LLM later without changing the framework.

---

## Why Helmsman

- **Maps to “Model Behavior Architect” work:** prompt strategy, edge-case discovery, eval at scale, A/B diffs, go/no-go gates.  
- **Engineering rigor:** behavior as tests (contracts), fuzzing, and gated releases.  
- **Explainability:** shows *why* a prompt works via contract outcomes (extend to attribution later).

---

## What’s here (MVP)

- `contracts/` — YAML **Prompt-Contracts** (`disambiguation.yaml`, `citations.yaml`)
- `core/` — `orchestrator.py` (run packs → answers → checks → JSONL) and `diff.py`
- `evals/` — simple detectors/evaluators (disambiguation & citation quality)
- `rag/` — tiny **retriever** (TF-IDF over `data/corpus.jsonl`) + naive answerer
- `truth/` — `TruthLens` placeholder (claim splitting; easy to swap for real verifier)
- `packs/` — smoke test JSONL (ambiguous EN queries)
- `prompts/` — `v1.yaml` (system prompt with “ask-if-ambiguous” clause)
- `ci/` — example **gates** and a sample **GitHub Actions** workflow
- `docker/` — minimal Dockerfile to run the orchestrator
- `tests/` — basic unit tests for loaders and detectors

---

## Quickstart

**Requirements:** Python 3.11+, `pip`

```bash
# Install minimal deps
pip install -r requirements.txt
# or: pip install pyyaml scikit-learn

# Run a smoke evaluation
python -m helmsman.core.orchestrator \
  --contracts_dir helmsman/contracts/builtin \
  --packs helmsman/packs/smoke_ambiguous_en.jsonl \
  --prompts helmsman/prompts/v1.yaml \
  --model local_v1 \
  --out helmsman/data/runs/run.jsonl
```

**Output:** JSONL with, per test case:
- `input_query`, `retrieved_snippets`, `answer`, `citations`
- `contract_results`: per-contract `{id, passed, message}`
- metadata: `run_id`, `model_version`, `prompt_version`, `locale`, `topic`, `seed_id`

---

## Contracts (DSL) — example

`contracts/builtin/disambiguation.yaml`
```yaml
id: disambiguate_before_answer
applies_to: ["general_qa","geography","celebs","travel","products"]
locales: ["en","hi","ur","es"]
precondition: "query_is_ambiguous"
obligation:
  must_ask_clarifying_q: true
metrics:
  pass_criteria: "asked_then_answered"
detectors:
  query_is_ambiguous: { fn: "detect_ambiguity" }
  asked_then_answered:
    fn: "check_asked_then_answered"
    args:
      clarify_interrogatives: ["which","who","what","do you mean"]
```

`contracts/builtin/citations.yaml`
```yaml
id: citations_minimum_and_precision
applies_to: ["general_qa","research_answering","news","science"]
locales: ["en","hi","ur","es"]
precondition: "contains_factual_claims"
obligation:
  min_citations: 2
metrics:
  pass_criteria: "precision_and_coverage"
detectors:
  contains_factual_claims: { fn: "detect_claims" }
  precision_and_coverage:
    fn: "check_citation_quality"
    args: { require_independent_domains: true }
```

---

## Packs (tests)

`packs/smoke_ambiguous_en.jsonl`
```json
{"id":"q1","input_query":"What's the best Jordan visa?","locale":"en","topic":"travel"}
{"id":"q2","input_query":"Tell me about Apple.","locale":"en","topic":"general_qa"}
{"id":"q3","input_query":"Who is Jordan?","locale":"en","topic":"celebs"}
{"id":"q4","input_query":"What is Amazon?","locale":"en","topic":"general_qa"}
```

Add your own packs (jsonl) with fields: `id`, `input_query`, `locale`, `topic`.

---

## Retrieval & Answering

- **Retriever:** TF-IDF over `helmsman/data/corpus.jsonl` (you can replace this with your docs or wire a real retriever).  
- **Answerer:** picks the top snippet’s first sentence (that’s the *placeholder* you’ll swap for your LLM/RAG chain).  
- **Citations:** snippet IDs are returned as citations; the citations contract ensures count/independence.

> Swap in your LLM by editing `helmsman/rag/answer.py` (keep the `(answer, citations)` return signature).

---

## Evaluation & TruthLens (placeholder)

- `detect_ambiguity`, `check_asked_then_answered` — basic heuristics to verify the **disambiguation** contract.
- `detect_claims`, `check_citation_quality` — minimal checks: “has ≥2 independent citations”.
- `truth/truthlens_adapter.py` — splits answer into naive claims; mark as supported if citations exist.  
  Replace this with your **real verifier** (NLI/entailment + source-snippets).

---

## Diffs & Gates

Compare two runs and enforce simple gates:

```bash
python -m helmsman.core.diff \
  --a helmsman/data/runs/baseline.jsonl \
  --b helmsman/data/runs/run.jsonl \
  --gates helmsman/ci/gates.yaml
```

`helmsman/ci/gates.yaml` contains thresholds (min disambiguation rate, max unverifiable, etc.). Extend as needed.

---

## CI (example)

Copy `helmsman/ci/workflow_example.yml` to `.github/workflows/helmsman.yml`.  
It installs deps, runs the smoke pack, produces a run, and compares vs baseline (you can version a baseline or update it per release).

Secrets not required for the MVP (no external API). If you later add an LLM, set your `OPENAI_API_KEY` (or provider key) in repo secrets and modify the workflow.

---

## Docker

Build and run the orchestrator in a container:

```bash
docker build -t helmsman .
docker run --rm -v "$PWD:/app" helmsman \
  --contracts_dir helmsman/contracts/builtin \
  --packs helmsman/packs/smoke_ambiguous_en.jsonl \
  --prompts helmsman/prompts/v1.yaml \
  --model docker_v1 \
  --out helmsman/data/runs/run.jsonl
```

---

## Tests

```bash
python -m pytest helmsman/tests -q
```

(You can extend tests for new detectors/evaluators and contract fixtures.)

---

## Extend toward “wow factor”

- **Behavioral fuzzer:** ambiguity injectors, entity collisions, date flips, multilingual/code-mix, typography noise, long-context truncation, minimal failing seeds.  
- **Attribution:** leave-one-out/segment ablation over system prompt (token sensitivity heatmaps).  
- **Multilingual:** add HI/UR/ES packs and locale-aware contracts.  
- **Reviewer UI:** Streamlit app to explore transcripts, violated contracts, and export a **Release Behavior Report**.

---

## Safety & Ethics

- Use abstract, non-dangerous seeds.  
- Contracts can route to refusals for unsafe topics.  
- No PII stored; local-only by default.

---

## Troubleshooting

- **No results / empty citations:** ensure `helmsman/data/corpus.jsonl` exists or point retriever to your own corpus.  
- **scikit-learn errors:** use Python 3.11+, reinstall with `pip install -r requirements.txt`.  
- **CI baseline:** create an initial baseline run and commit it (or store baselines per release).

---

## License

Choose one appropriate to your project (e.g., MIT); add a `LICENSE` file.
