# Atalhos do desafio. `make` ou `make help` lista os alvos.
#
# Provider: por padrão vale o que está no .env (Google Gemini). Para trocar só
# numa execução, sem editar o .env:
#   make eval PROVIDER=anthropic   # Claude, via gateway LiteLLM (Docker)
#   make eval PROVIDER=aws         # Bedrock, via gateway LiteLLM (Docker)
#   make eval PROVIDER=openai      # OpenAI direta
#   make eval PROVIDER=google      # Gemini direto, com os presets GOOGLE_*
#   make eval PROVIDER=gateway     # Gemini via gateway (testa o gateway sem custo)

SHELL := /bin/bash
.DEFAULT_GOAL := help

VENV := venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip

-include .env

GATEWAY_URL := http://localhost:$(or $(GATEWAY_PORT),4000)
GATEWAY_ENV  = LLM_PROVIDER=openai OPENAI_BASE_URL=$(GATEWAY_URL) OPENAI_API_KEY=$(LITELLM_MASTER_KEY)

PROVIDER ?=
NEEDS_GATEWAY :=
ifeq ($(PROVIDER),)
  RUN_ENV :=
else ifeq ($(PROVIDER),google)
  RUN_ENV := LLM_PROVIDER=google LLM_MODEL=$(GOOGLE_LLM_MODEL) EVAL_MODEL=$(GOOGLE_EVAL_MODEL)
else ifeq ($(PROVIDER),openai)
  RUN_ENV := LLM_PROVIDER=openai LLM_MODEL=$(OPENAI_LLM_MODEL) EVAL_MODEL=$(OPENAI_EVAL_MODEL)
else ifeq ($(PROVIDER),anthropic)
  RUN_ENV = $(GATEWAY_ENV) LLM_MODEL=anthropic/$(ANTHROPIC_LLM_MODEL) EVAL_MODEL=anthropic/$(ANTHROPIC_EVAL_MODEL)
  NEEDS_GATEWAY := yes
else ifeq ($(PROVIDER),aws)
  RUN_ENV = $(GATEWAY_ENV) LLM_MODEL=bedrock/$(AWS_LLM_MODEL) EVAL_MODEL=bedrock/$(AWS_EVAL_MODEL)
  NEEDS_GATEWAY := yes
else ifeq ($(PROVIDER),gateway)
  RUN_ENV = $(GATEWAY_ENV) LLM_MODEL=gemini/$(GOOGLE_LLM_MODEL) EVAL_MODEL=gemini/$(GOOGLE_EVAL_MODEL)
  NEEDS_GATEWAY := yes
else
  $(error PROVIDER inválido: '$(PROVIDER)'. Use google | openai | anthropic | aws | gateway)
endif

RUN = $(RUN_ENV) $(PY)
ENSURE_GATEWAY = $(if $(NEEDS_GATEWAY),@$(MAKE) --no-print-directory gateway-up,@true)

.PHONY: help setup env check-env smoke test test-one pull push eval validate \
        share-dataset gateway-up gateway-down gateway-logs gateway-test clean

help: ## Lista os alvos
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  Provider por execução: make <alvo> PROVIDER=google|openai|anthropic|aws|gateway"

$(PY):
	python3 -m venv $(VENV)
	$(PIP) install -q --upgrade pip
	$(PIP) install -q -r requirements.txt

setup: $(PY) env ## Cria o venv, instala as dependências e prepara o .env
	@echo "✓ ambiente pronto"

env: $(PY) ## Cria/completa o .env (copia chaves vazias do ../.env e gera LITELLM_MASTER_KEY)
	@$(PY) scripts/sync_env.py

check-env: $(PY) ## Mostra provider/modelos efetivos e variáveis faltando (sem segredos)
	@$(RUN_ENV) $(PY) scripts/check_env.py

smoke: $(PY) ## Faz uma chamada curta no LLM_MODEL e no EVAL_MODEL pelo src/utils.py
	$(ENSURE_GATEWAY)
	@$(RUN) scripts/smoke_llm.py

test: $(PY) ## Roda os testes de validação do prompt (pytest)
	$(PY) -m pytest tests/test_prompts.py -v

test-one: $(PY) ## Roda um teste: make test-one T=test_minimum_techniques
	$(PY) -m pytest "tests/test_prompts.py::TestPrompts::$(T)" -v

pull: $(PY) ## Pull do prompt v1 do Hub -> prompts/bug_to_user_story_v1.yml
	$(RUN) src/pull_prompts.py

push: $(PY) ## Push do prompt v2 -> {USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2 (público)
	$(RUN) src/push_prompts.py

eval: $(PY) ## Avaliação completa no LangSmith (cria experimento e imprime as 5 métricas)
	$(ENSURE_GATEWAY)
	$(RUN) src/evaluate.py

validate: test push eval ## Ciclo completo de iteração: testes -> push -> avaliação

share-dataset: $(PY) ## Gera o link PÚBLICO do dataset+experimentos (exige CONFIRM=yes; o link muda a cada execução)
	@if [ "$(CONFIRM)" != "yes" ]; then echo "⚠️  Cada execução gera um link NOVO e invalida o anterior. Rode: make share-dataset CONFIRM=yes"; exit 1; fi
	$(PY) -c 'import os; from dotenv import load_dotenv; load_dotenv(); from langsmith import Client; print(Client().share_dataset(dataset_name=os.environ["LANGSMITH_PROJECT"] + "-eval")["url"])'

gateway-up: ## Sobe o gateway LiteLLM (Docker) e espera ficar saudável
	@docker compose up -d --wait llm-gateway >/dev/null && echo "✓ gateway em $(GATEWAY_URL)"

gateway-down: ## Derruba o gateway
	docker compose down

gateway-logs: ## Logs do gateway
	docker compose logs -f llm-gateway

gateway-test: ## Testa o gateway de ponta a ponta com Gemini (sem custo)
	@$(MAKE) --no-print-directory smoke PROVIDER=gateway

clean: ## Remove caches (mantém venv e .env)
	find . -type d \( -name __pycache__ -o -name .pytest_cache \) -not -path './venv/*' -prune -exec rm -rf {} +
