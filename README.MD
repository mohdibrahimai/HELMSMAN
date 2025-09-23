# Prompt Contracts + Fuzzing CI for Answer Engines

A production-oriented, working reference that turns prompt work into **engineering discipline**:

* **Contracts (DSL)** to specify expected behavior
* **Harness + packs** to stress-test prompts/models
* **Evaluators** to measure disambiguation & citation quality
* **Diff + CI gates** to block regressions

> Runs locally with no external APIs; uses a real, local corpus. Plug in your own retriever/LLM later without changing the framework.

---

## Why This Matters

* **Maps to “Model Behavior Architect” work:** prompt strategy, edge-case discovery, eval at scale, A/B diffs, go/no-go gates.
* **Engineering rigor:** behavior as tests (contracts), fuzzing, and gated releases.
* **Explainability:** shows *why* a prompt works via contract outcomes (extendable to attribution later).

---

## What’s Included (MVP)

* `contracts/` — YAML **Prompt-Contracts** (`disambiguation.yaml`, `citations.yaml`)
* `core/` — `orchestrator.py` (run packs → answers → checks → JSONL) and `diff.py`
* `evals/` — simple detectors/evaluators (disambiguation & citation quality)
* `rag/` — tiny **retriever** (TF-IDF over `data/corpus.jsonl`) + naive answerer
* `truth/` — `TruthLens` placeholder (claim splitting; can be swapped for real verifier)
* `packs/` — smoke test JSONL (ambiguous EN queries)
* `prompts/` — `v1.yaml` (system prompt with “ask-if-ambiguous” clause)
* `ci/` — example **gates** and a sample **GitHub Actions** workflow
* `docker/` — minimal Dockerfile to run the orchestrator
* `tests/` — basic unit tests for loaders and detectors

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

**Output:** JSONL with per test case results:

* `input_query`, `retrieved_snippets`, `answer`, `citations`
* `contract_results`: per-contract `{id, passed, message}`
* metadata: `run_id`, `model_version`, `prompt_version`, `locale`, `topic`, `seed_id`

---

## Contracts (DSL) — Example

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

## Packs (Tests)

`packs/smoke_ambiguous_en.jsonl`

```json
{"id":"q1","input_query":"What's the best Jordan visa?","locale":"en","topic":"travel"}
{"id":"q2","input_query":"Tell me about Apple.","locale":"en","topic":"general_qa"}
{"id":"q3","input_query":"Who is Jordan?","locale":"en","topic":"celebs"}
{"id":"q4","input_query":"What is Amazon?","locale":"en","topic":"general_qa"}
```

Add your own packs with fields: `id`, `input_query`, `locale`, `topic`.

---

## Retrieval & Answering

* **Retriever:** TF-IDF over `helmsman/data/corpus.jsonl` (replace with your docs or plug in a real retriever).
* **Answerer:** placeholder that picks the top snippet’s first sentence. Swap this for your LLM/RAG chain.
* **Citations:** snippet IDs returned as citations; contracts ensure count/independence.

---

## Evaluation & TruthLens (Placeholder)

* `detect_ambiguity`, `check_asked_then_answered` — verify the **disambiguation** contract.
* `detect_claims`, `check_citation_quality` — minimal checks for citation count & precision.
* `truth/truthlens_adapter.py` — splits answers into naive claims, marks as supported if citations exist. Replace with a **real verifier** for production.

---

## Diffs & Gates

Compare two runs and enforce gates:

```bash
python -m helmsman.core.diff \
  --a helmsman/data/runs/baseline.jsonl \
  --b helmsman/data/runs/run.jsonl \
  --gates helmsman/ci/gates.yaml
```

`helmsman/ci/gates.yaml` defines thresholds (min disambiguation rate, max unverifiable, etc.). Extend as needed.

---

## CI (Example)

Use `helmsman/ci/workflow_example.yml` as `.github/workflows/helmsman.yml`. It:

* Installs dependencies
* Runs the smoke pack
* Produces a run
* Compares results vs baseline

Secrets not required for MVP (no external API). Add keys later if wiring an LLM.

---

## Docker

```bash
docker build -t prompt-ci .
docker run --rm -v "$PWD:/app" prompt-ci \
  --contracts_dir helmsman/contracts/builtin \
  --packs helmsman/packs/smoke_ambiguous_en.jsonl \
  --prompts helmsman/prompts/v1.yaml \
  --model docker_v1 \
  --out helmsman/data/runs/run.jsonl
```

---

## Tests

```bash
pytest helmsman/tests -q
```

Extend tests for new detectors, evaluators, and contract fixtures.

---

## Extensions & Future Work

* **Behavioral fuzzing:** ambiguity injectors, entity collisions, multilingual tests.
* **Attribution:** sensitivity maps, leave-one-out ablations.
* **Multilingual coverage:** add HI/UR/ES packs.
* **Reviewer UI:** Streamlit app to explore transcripts and export **Release Behavior Reports**.

---

## Safety & Ethics

* Use safe, abstract test seeds.
* Contracts can enforce refusals for unsafe topics.
* Local-only by default; no PII stored.

---

## Troubleshooting

* **Empty citations:** ensure `helmsman/data/corpus.jsonl` exists.
* **scikit-learn issues:** use Python 3.11+, reinstall requirements.
* **CI baseline:** generate and commit a baseline run before comparison.

---

## License

Choose a suitable license (MIT or Apache-2.0 recommended) and include a `LICENSE` file.
