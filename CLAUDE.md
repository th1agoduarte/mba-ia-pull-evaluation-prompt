# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Desafio 01 (módulo Prompt Engineering). Clone of `devfullcycle/mba-ia-pull-evaluation-prompt`, delivered as a **public GitHub fork**. Remotes: `upstream` = devfullcycle (read-only) and `origin` = `git@github.com:th1agoduarte/mba-ia-pull-evaluation-prompt.git` (SSH auth works; the fork must exist on GitHub before the first push). Full statement: `DESAFIO.md`. `README.md` is the deliverable documentation. `VALIDACAO.md` is the step-by-step requirement check; keep it in sync when behavior changes.

## Commands

Use the Makefile (`make help`). Run from the repo root. `evaluate.py` opens `datasets/...` by relative path, and `from utils import ...` only resolves because `python src/x.py` puts `src/` on `sys.path`.

```bash
make setup / make env      # venv + deps; env = create/complete .env from .env.example + ../.env (never overwrites filled values, generates LITELLM_MASTER_KEY)
make check-env             # effective provider/models + missing vars, no secrets printed
make smoke                 # one short call to LLM_MODEL and EVAL_MODEL through src/utils.py
make test                  # pytest tests/test_prompts.py -v
make test-one T=test_minimum_techniques
make pull | push | eval    # src/pull_prompts.py | src/push_prompts.py | src/evaluate.py
make validate              # test -> push -> eval (one iteration)
make share-dataset CONFIRM=yes   # public dataset link; changes on every call, run ONCE
```

Every run target accepts `PROVIDER=google|openai|anthropic|aws|gateway`.

## Multi-provider without touching protected files

`src/utils.py:get_llm` only supports `google`/`openai`, and the statement forbids editing it. Other providers go through a **LiteLLM gateway** (`docker-compose.yml`, `gateway/litellm-config.yaml`, image pinned to `ghcr.io/berriai/litellm:1.103.9`, port `GATEWAY_PORT`=4000). For `PROVIDER=anthropic|aws|gateway`, the Makefile starts the container (`docker compose up --wait`) and injects these env vars for that run only: `LLM_PROVIDER=openai OPENAI_BASE_URL=http://localhost:4000 OPENAI_API_KEY=$LITELLM_MASTER_KEY LLM_MODEL=<prefix>/<preset>`. Process env beats `.env` in python-dotenv. The gateway routes by model prefix wildcard: `anthropic/*`, `bedrock/*`, `gemini/*`. Presets live in `.env` as `<PROVIDER>_LLM_MODEL` / `<PROVIDER>_EVAL_MODEL`. Never set `OPENAI_BASE_URL` to an empty string: the openai SDK treats `""` as a URL.

Verified 2026-11-15: direct Gemini and `make gateway-test` (Gemini via gateway) both work. `PROVIDER=anthropic` reaches Anthropic but gets 401, because the root `ANTHROPIC_API_KEY` is a placeholder. AWS has not been tested (no credentials).

LangSmith is always the **cloud** (smith.langchain.com). Self-hosted LangSmith requires an Enterprise license, and the deliverable needs public links.

## Architecture / data flow

- **The Hub is the source of truth for evaluation.** `evaluate.py` pulls `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` from the Hub. It does not read the local YAML, so YAML edits without `make push` are not evaluated.
- The template variable must be `{bug_report}` (the dataset input key). The output is stored as `{"answer": response.text}`.
- Metrics (`src/metrics.py`): the LLM judge (`EVAL_MODEL`) scores only **F1, Clarity and Precision**. The other two are derived: `helpfulness = (clarity + precision)/2` and `correctness = (f1 + precision)/2`. **Precision drives 3 of the 5 metrics.** F1 and Precision compare against the dataset `reference`. The references are Portuguese and follow "Como um <persona>, eu quero <ação>, para que <benefício>." + "Critérios de Aceitação:" with Dado/Quando/Então/E bullets. Matching that shape and language is the main lever. Read the judge prompts in `metrics.py` before iterating.
- Approval requires every metric ≥ 0.8 **and** the mean ≥ 0.8. The dataset has 15 examples (5 simple, 7 medium, 3 complex; `metadata.complexity` in the jsonl).
- Dataset name is `{LANGSMITH_PROJECT}-eval`. It is created once and then reused. Changing `LANGSMITH_PROJECT` creates a new dataset and splits the experiment history.
- `utils.validate_prompt_structure` expects `description`, `system_prompt`, `version` and `techniques_applied` (≥2). The v1 YAML nests everything under a top-level key (`bug_to_user_story_v1:`). Keep the v2 YAML consistent with what push and the tests read.
- Pull returns a `ChatPromptTemplate`. Text is at `prompt.messages[i].prompt.template`. Owner-qualified pulls need `dangerously_pull_public_prompt=True`.

## Constraints from the statement

- **Do not modify** `src/evaluate.py`, `src/metrics.py`, `src/utils.py` or `datasets/`. Check with `git diff --stat upstream/main -- src/evaluate.py src/metrics.py src/utils.py datasets/`.
- Implement only: `prompts/bug_to_user_story_v2.yml`, `src/pull_prompts.py`, `src/push_prompts.py`, `tests/test_prompts.py`, `README.md`. The extras (Makefile, scripts/, gateway, VALIDACAO.md) are additive tooling.
- The v2 prompt must have: Few-shot (mandatory) + ≥1 of CoT / ToT / Skeleton of Thought / ReAct / Role Prompting, explicit rules, edge cases, a proper system/user split (v1 duplicates `{bug_report}` in both), and no `TODO`.
- The 6 test stubs currently `pass` trivially. "6 passed" means nothing until they are implemented.

## Env

- `.env` was generated by `make env` with the Google key copied from `../.env`. It still needs `LANGSMITH_API_KEY` and `USERNAME_LANGSMITH_HUB` from the user. Until then, every LLM call logs harmless 401 tracing errors.
- Defaults: `LLM_MODEL=gemini-3.5-flash-lite`, `EVAL_MODEL=gemini-3.5-flash`. `gemini-3.5-flash-lite` **ignores temperature** ("fixed sampling defaults" warning), so scores vary between runs. If results are noisy near 0.8, switch the generator to a model that honors `temperature=0`.
- `evaluate.py` uses `max_concurrency=1`. A run is about 15 generations + 45 judge calls, so watch the Gemini free-tier RPM/RPD.

## Plano

1. User: create a LangSmith API key and the public Hub handle, then fill `.env` (`make check-env` must be all ✓). User: fork on GitHub (see Remotes above).
2. Implement `src/pull_prompts.py`. `make pull` must produce `prompts/bug_to_user_story_v1.yml`.
3. Write `prompts/bug_to_user_story_v2.yml`: Role Prompting (PM/PO persona) + Few-shot (2–3 examples in the exact reference format) + internal CoT (output only the story) + edge-case rules (vague, multi-symptom or non-bug reports).
4. Implement `tests/test_prompts.py` (6 real tests on the v2 YAML) and `src/push_prompts.py` (validate, then `push_prompt(..., is_public=True, description, tags)` with techniques in the metadata).
5. Iterate with `make validate` (3–5 rounds). Use traces and the judges' `reasoning` comments to find failures. Record each round's scores for the README. Confirm the pass repeats on a second run.
6. `make share-dataset CONFIRM=yes` **once**. Take screenshots and record ≥3 detailed traces.
7. Fill in the README sections, run through `VALIDACAO.md` end-to-end, commit, and `git push origin main`.
