# Validação dos requisitos — passo a passo

Roteiro para confirmar, do zero, que cada requisito do [enunciado](DESAFIO.md) está atendido. Rode tudo na raiz do repositório. Cada passo diz o comando e o resultado esperado.

## 0. Ambiente

| # | Comando | Esperado |
|---|---|---|
| 0.1 | `make setup` | venv criado, dependências instaladas, `.env` criado |
| 0.2 | Preencha no `.env`: `LANGSMITH_API_KEY`, `USERNAME_LANGSMITH_HUB` e a chave do provider (`GOOGLE_API_KEY` por padrão) | — |
| 0.3 | `make check-env` | Todas as linhas com ✓ e `✅ Configuração completa` |
| 0.4 | `make smoke` | `✓ LLM_MODEL ...` e `✓ EVAL_MODEL ...` (credencial e modelos válidos) |

## 1. Pull do prompt inicial (Requisito 1)

| # | Comando | Esperado |
|---|---|---|
| 1.1 | `rm -f prompts/bug_to_user_story_v1.yml && make pull` | Sem erro |
| 1.2 | `cat prompts/bug_to_user_story_v1.yml` | Arquivo recriado, com o system prompt e o user prompt de `leonanluppi/bug_to_user_story_v1` |

## 2. Prompt otimizado (Requisito 2)

| # | Verificação | Esperado |
|---|---|---|
| 2.1 | `make test` | **8 testes passando** (os 6 exigidos + 2 extras: variáveis do template e validação de `utils.py`), sem nenhum `pass` vazio |
| 2.2 | Ler `prompts/bug_to_user_story_v2.yml` | Persona definida, regras explícitas, tratamento de edge cases, exemplos few-shot de entrada/saída, separação system × user, `{bug_report}` só no user prompt |
| 2.3 | `grep -n techniques_applied -A5 prompts/bug_to_user_story_v2.yml` | Few-shot + pelo menos mais uma técnica (CoT, ToT, Skeleton of Thought, ReAct ou Role Prompting) |
| 2.4 | README, seção "Técnicas Aplicadas (Fase 2)" | Técnicas, justificativa e exemplo de cada uma |

## 3. Push (Requisito 3)

| # | Comando | Esperado |
|---|---|---|
| 3.1 | `make push` | URL do prompt `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` |
| 3.2 | Abrir `https://smith.langchain.com/hub/{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` numa aba anônima | Prompt **público**, com descrição, tags e técnicas nos metadados |

## 4. Avaliação e critério de aprovação (Requisito 4)

| # | Comando | Esperado |
|---|---|---|
| 4.1 | `make eval` | As 5 métricas com ✓, `MÉDIA GERAL >= 0.8` e `✅ STATUS: APROVADO` |
| 4.2 | Link do experimento impresso no final | Experimento no LangSmith com 15 exemplos e as 5 notas como feedback em cada um |
| 4.3 | Abrir 3 runs do experimento | Trace detalhado (prompt enviado e resposta) de pelo menos 3 exemplos |

> Critério: **todas** as métricas ≥ 0.8 (Helpfulness, Correctness, F1-Score, Clarity, Precision), não só a média. O juiz é um LLM, então rode `make eval` pelo menos duas vezes e confirme que a aprovação se repete.

### Outros providers (opcional)

O mesmo passo 4 funciona com outro provider sem alterar nenhum arquivo protegido:

```bash
make gateway-test                 # gateway Docker + Gemini, sem custo
make eval PROVIDER=anthropic      # exige ANTHROPIC_API_KEY
make eval PROVIDER=aws            # exige credenciais AWS + AWS_*_MODEL
make eval PROVIDER=openai         # exige OPENAI_API_KEY + OPENAI_*_MODEL
```

## 5. Testes de validação (Requisito 5)

| # | Comando | Esperado |
|---|---|---|
| 5.1 | `pytest tests/test_prompts.py` | 8 passed, incluindo os 6 exigidos: `test_prompt_has_system_prompt`, `test_prompt_has_role_definition`, `test_prompt_mentions_format`, `test_prompt_has_few_shot_examples`, `test_prompt_no_todos`, `test_minimum_techniques` |
| 5.2 | Prova negativa: apague temporariamente a lista `techniques_applied` do v2 e rode `make test-one T=test_minimum_techniques` | O teste **falha** (mostra que o teste realmente verifica). Depois restaure o arquivo com `git checkout prompts/bug_to_user_story_v2.yml` |

## 6. Arquivos que não podem mudar

| # | Comando | Esperado |
|---|---|---|
| 6.1 | `git diff --stat upstream/main -- src/evaluate.py src/metrics.py src/utils.py datasets/` | Saída vazia |

## 7. Entregável

| # | Verificação | Esperado |
|---|---|---|
| 7.1 | Repositório no GitHub | Público, aparece como *fork* de `devfullcycle/mba-ia-pull-evaluation-prompt` |
| 7.2 | README, seção "Resultados Finais" | Link público do dataset (gerado **uma vez** com `make share-dataset CONFIRM=yes`), screenshots com notas ≥ 0.8 e comparação v1 × v2 |
| 7.3 | Abrir o link público do dataset numa aba anônima | Dataset com 15 exemplos e experimentos v2 visíveis |
| 7.4 | README, seção "Como Executar" | Pré-requisitos e comandos de cada fase |
